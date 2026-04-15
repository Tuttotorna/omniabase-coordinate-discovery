from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

X0 = Decimal("0.123456")
TOTAL_STEPS = 600
BURN_IN = 300
BASES = list(range(2, 17))
DECIMAL_DIGITS = 12

# Focus on the stable window around r ~ 3.83 (period-3 window)
R_START = Decimal("3.820")
R_END = Decimal("3.860")
R_STEP = Decimal("0.001")


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
        "digit_sum_span": float(max(digit_sums) - min(digit_sums)),
        "repetition_span": float(max(repetition_scores) - min(repetition_scores)),
    }


def summarize_regime(xs: list[Decimal]) -> dict[str, float]:
    x_values = [float(x) for x in xs]
    digit_sum_span_values = []
    repetition_span_values = []

    for x in xs:
        sig = compute_state_signature(x)
        digit_sum_span_values.append(sig["digit_sum_span"])
        repetition_span_values.append(sig["repetition_span"])

    return {
        "unique_states": len({round(v, 10) for v in x_values}),
        "x_std": std(x_values),
        "digit_sum_span_std": std(digit_sum_span_values),
        "repetition_span_std": std(repetition_span_values),
    }


def generate_r_values() -> list[Decimal]:
    values = []
    r = R_START
    while r <= R_END:
        values.append(r)
        r += R_STEP
    return values


def minmax_params(values: list[float]) -> tuple[float, float]:
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return lo, hi + 1.0
    return lo, hi


def minmax_norm(x: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.0
    y = (x - lo) / (hi - lo)
    return max(0.0, min(1.0, y))


def build_transition_scores(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    digit_vals = [row["digit_sum_span_std"] for row in rows]
    rep_vals = [row["repetition_span_std"] for row in rows]

    digit_lo, digit_hi = minmax_params(digit_vals)
    rep_lo, rep_hi = minmax_params(rep_vals)

    out: list[dict[str, float]] = []
    prev_digit = None
    prev_rep = None

    # Local relative deltas inside the scanned window
    rel_digit_deltas = []
    rel_rep_deltas = []
    for row in rows:
        if prev_digit is None:
            rel_digit_deltas.append(0.0)
            rel_rep_deltas.append(0.0)
        else:
            rel_digit_deltas.append(
                0.0 if prev_digit == 0 else (row["digit_sum_span_std"] - prev_digit) / abs(prev_digit)
            )
            rel_rep_deltas.append(
                0.0 if prev_rep == 0 else (row["repetition_span_std"] - prev_rep) / abs(prev_rep)
            )
        prev_digit = row["digit_sum_span_std"]
        prev_rep = row["repetition_span_std"]

    rel_digit_lo, rel_digit_hi = minmax_params(rel_digit_deltas)
    rel_rep_lo, rel_rep_hi = minmax_params(rel_rep_deltas)

    for row, rel_digit, rel_rep in zip(rows, rel_digit_deltas, rel_rep_deltas):
        norm_digit = minmax_norm(row["digit_sum_span_std"], digit_lo, digit_hi)
        norm_rep = minmax_norm(row["repetition_span_std"], rep_lo, rep_hi)
        norm_rel_digit = minmax_norm(rel_digit, rel_digit_lo, rel_digit_hi)
        norm_rel_rep = minmax_norm(rel_rep, rel_rep_lo, rel_rep_hi)

        score = (
            0.35 * norm_digit
            + 0.25 * norm_rep
            + 0.25 * norm_rel_digit
            + 0.15 * norm_rel_rep
        )

        out.append(
            {
                **row,
                "rel_delta_digit_sum_span_std": rel_digit,
                "rel_delta_repetition_span_std": rel_rep,
                "transition_score_v1": score,
            }
        )

    return out


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    raw_rows = []
    for r in generate_r_values():
        xs = generate_trajectory(r)
        summary = summarize_regime(xs)
        raw_rows.append({"r": float(r), **summary})

    rows = build_transition_scores(raw_rows)

    fieldnames = [
        "r",
        "unique_states",
        "x_std",
        "digit_sum_span_std",
        "repetition_span_std",
        "rel_delta_digit_sum_span_std",
        "rel_delta_repetition_span_std",
        "transition_score_v1",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE WINDOW SCAN 3.83 V1")
        print("-" * 72)

        for row in rows:
            writer.writerow(
                {
                    "r": f"{row['r']:.3f}",
                    "unique_states": int(row["unique_states"]),
                    "x_std": row["x_std"],
                    "digit_sum_span_std": row["digit_sum_span_std"],
                    "repetition_span_std": row["repetition_span_std"],
                    "rel_delta_digit_sum_span_std": row["rel_delta_digit_sum_span_std"],
                    "rel_delta_repetition_span_std": row["rel_delta_repetition_span_std"],
                    "transition_score_v1": row["transition_score_v1"],
                }
            )

            print(
                f"r={row['r']:.3f} | "
                f"states={int(row['unique_states'])} | "
                f"x_std={row['x_std']:.6f} | "
                f"digit_span_std={row['digit_sum_span_std']:.6f} | "
                f"rep_span_std={row['repetition_span_std']:.6f} | "
                f"score={row['transition_score_v1']:.6f}"
            )

    print("-" * 72)
    print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/logistic_map_window_383_v1.csv"))