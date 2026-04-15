from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

X0 = Decimal("0.123456")
TOTAL_STEPS = 400
BURN_IN = 150
BASES = list(range(2, 17))
DECIMAL_DIGITS = 12

# Fine scan around the transition region
R_START = Decimal("3.540")
R_END = Decimal("3.610")
R_STEP = Decimal("0.002")


def logistic_map_step(x: Decimal, r: Decimal) -> Decimal:
    return r * x * (Decimal(1) - x)


def generate_trajectory(r: Decimal) -> list[Decimal]:
    x = X0
    values: list[Decimal] = []
    for _ in range(TOTAL_STEPS):
        x = logistic_map_step(x, r)
        values.append(x)
    return values[BURN_IN:]


def decimal_fraction_to_base(x: Decimal, base: int, digits: int = DECIMAL_DIGITS) -> str:
    if not (Decimal("0") <= x <= Decimal("1")):
        raise ValueError(f"x must be in [0,1], got {x}")
    if base < 2:
        raise ValueError("base must be >= 2")

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


def compute_state_signature(x: Decimal) -> dict[str, float]:
    digit_sums = []
    repetition_scores = []

    for base in BASES:
        rep = decimal_fraction_to_base(x, base, DECIMAL_DIGITS)
        digit_sums.append(digit_sum(rep))
        repetition_scores.append(repetition_score(rep))

    return {
        "avg_digit_sum": mean(digit_sums),
        "digit_sum_span": float(max(digit_sums) - min(digit_sums)),
        "avg_repetition": mean(repetition_scores),
        "repetition_span": float(max(repetition_scores) - min(repetition_scores)),
    }


def summarize_regime(xs: list[Decimal]) -> dict[str, float]:
    x_values = [float(x) for x in xs]

    avg_digit_sum_values = []
    digit_sum_span_values = []
    avg_repetition_values = []
    repetition_span_values = []

    for x in xs:
        sig = compute_state_signature(x)
        avg_digit_sum_values.append(sig["avg_digit_sum"])
        digit_sum_span_values.append(sig["digit_sum_span"])
        avg_repetition_values.append(sig["avg_repetition"])
        repetition_span_values.append(sig["repetition_span"])

    return {
        "unique_states_rounded_12": len({round(v, 12) for v in x_values}),
        "x_std": std(x_values),
        "avg_digit_sum_std": std(avg_digit_sum_values),
        "digit_sum_span_std": std(digit_sum_span_values),
        "avg_repetition_std": std(avg_repetition_values),
        "repetition_span_std": std(repetition_span_values),
    }


def generate_r_values() -> list[Decimal]:
    values = []
    r = R_START
    while r <= R_END:
        values.append(r)
        r += R_STEP
    return values


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r",
        "unique_states_rounded_12",
        "x_std",
        "avg_digit_sum_std",
        "digit_sum_span_std",
        "avg_repetition_std",
        "repetition_span_std",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in generate_r_values():
            xs = generate_trajectory(r)
            summary = summarize_regime(xs)
            writer.writerow(
                {
                    "r": f"{r:.3f}",
                    **summary,
                }
            )

    print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/logistic_map_regime_scan_v1.csv"))