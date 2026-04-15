from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

# Standard Hénon map parameters
A = Decimal("1.4")
B = Decimal("0.3")

# Initial condition
X0 = Decimal("0.1")
Y0 = Decimal("0.1")

TOTAL_STEPS = 1200
BURN_IN = 400

BASES = list(range(2, 17))
DECIMAL_DIGITS = 12


def henon_step(x: Decimal, y: Decimal, a: Decimal, b: Decimal) -> tuple[Decimal, Decimal]:
    x_next = Decimal("1") - a * x * x + y
    y_next = b * x
    return x_next, y_next


def minmax_scale(values: list[Decimal]) -> list[Decimal]:
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [Decimal("0.5") for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def decimal_fraction_to_base(x: Decimal, base: int, digits: int = DECIMAL_DIGITS) -> str:
    if not (Decimal("0") <= x <= Decimal("1")):
        raise ValueError(f"x must be in [0,1], got {x}")

    frac = x
    out: list[str] = []

    for _ in range(digits):
        frac *= base
        digit = int(frac)
        frac -= digit

        if digit < 10:
            out.append(str(digit))
        else:
            out.append(chr(ord("A") + digit - 10))

    return "".join(out)


def digit_sum(base_repr: str) -> int:
    total = 0
    for ch in base_repr:
        if ch.isdigit():
            total += int(ch)
        else:
            total += ord(ch) - ord("A") + 10
    return total


def repetition_score(base_repr: str) -> float:
    if len(base_repr) < 2:
        return 0.0
    same = sum(1 for i in range(len(base_repr) - 1) if base_repr[i] == base_repr[i + 1])
    return same / (len(base_repr) - 1)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / len(values))


def generate_trajectory() -> list[tuple[Decimal, Decimal]]:
    x = X0
    y = Y0
    out: list[tuple[Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        x, y = henon_step(x, y, A, B)
        out.append((x, y))

    return out[BURN_IN:]


def compute_component_signature(z: Decimal) -> dict[str, float]:
    digit_sums = []
    repetition_scores = []

    for base in BASES:
        rep = decimal_fraction_to_base(z, base, DECIMAL_DIGITS)
        digit_sums.append(digit_sum(rep))
        repetition_scores.append(repetition_score(rep))

    return {
        "avg_digit_sum": mean(digit_sums),
        "digit_sum_span": float(max(digit_sums) - min(digit_sums)),
        "avg_repetition": mean(repetition_scores),
        "repetition_span": float(max(repetition_scores) - min(repetition_scores)),
    }


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    trajectory = generate_trajectory()
    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)

    fieldnames = [
        "step",
        "x",
        "y",
        "x_scaled",
        "y_scaled",
        "x_digit_sum_span",
        "x_repetition_span",
        "y_digit_sum_span",
        "y_repetition_span",
        "xy_digit_sum_span_mean",
        "xy_repetition_span_mean",
    ]

    x_digit_spans = []
    x_rep_spans = []
    y_digit_spans = []
    y_rep_spans = []

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, (x, y, xs_n, ys_n) in enumerate(zip(xs, ys, xs_scaled, ys_scaled)):
            sig_x = compute_component_signature(xs_n)
            sig_y = compute_component_signature(ys_n)

            x_digit_spans.append(sig_x["digit_sum_span"])
            x_rep_spans.append(sig_x["repetition_span"])
            y_digit_spans.append(sig_y["digit_sum_span"])
            y_rep_spans.append(sig_y["repetition_span"])

            writer.writerow(
                {
                    "step": idx,
                    "x": f"{x:.18f}",
                    "y": f"{y:.18f}",
                    "x_scaled": f"{xs_n:.18f}",
                    "y_scaled": f"{ys_n:.18f}",
                    "x_digit_sum_span": sig_x["digit_sum_span"],
                    "x_repetition_span": sig_x["repetition_span"],
                    "y_digit_sum_span": sig_y["digit_sum_span"],
                    "y_repetition_span": sig_y["repetition_span"],
                    "xy_digit_sum_span_mean": mean([sig_x["digit_sum_span"], sig_y["digit_sum_span"]]),
                    "xy_repetition_span_mean": mean([sig_x["repetition_span"], sig_y["repetition_span"]]),
                }
            )

    print("OMNIABASE HENON MULTIBASE V0")
    print("-" * 72)
    print(f"steps_written={len(xs)}")
    print(f"x_digit_sum_span_std={std(x_digit_spans):.6f}")
    print(f"x_repetition_span_std={std(x_rep_spans):.6f}")
    print(f"y_digit_sum_span_std={std(y_digit_spans):.6f}")
    print(f"y_repetition_span_std={std(y_rep_spans):.6f}")
    print("-" * 72)
    print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/henon_multibase_v0.csv"))