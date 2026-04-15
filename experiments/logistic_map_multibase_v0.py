from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv

getcontext().prec = 50


R_VALUES = [3.50, 3.55, 3.60, 3.70, 3.80, 3.90, 4.00]
X0 = Decimal("0.123456")
TOTAL_STEPS = 300
BURN_IN = 100
BASES = list(range(2, 17))
DECIMAL_DIGITS = 12


def logistic_map_step(x: Decimal, r: Decimal) -> Decimal:
    return r * x * (Decimal(1) - x)


def generate_trajectory(r_value: float) -> list[Decimal]:
    r = Decimal(str(r_value))
    x = X0
    values: list[Decimal] = []

    for _ in range(TOTAL_STEPS):
        x = logistic_map_step(x, r)
        values.append(x)

    return values[BURN_IN:]


def decimal_fraction_to_base(x: Decimal, base: int, digits: int = DECIMAL_DIGITS) -> str:
    """
    Convert a Decimal x in [0, 1] into base-N fractional digits.
    Returns only the fractional part digits, without '0.' prefix.
    """
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
    """
    Very simple local repetition score:
    proportion of adjacent equal symbols.
    """
    if len(base_repr) < 2:
        return 0.0
    same = sum(1 for i in range(len(base_repr) - 1) if base_repr[i] == base_repr[i + 1])
    return same / (len(base_repr) - 1)


def compute_signatures(x: Decimal) -> dict[str, float]:
    """
    Minimal Omniabase-style signature extractor for one scalar state.
    Produces cross-base features without claiming they are final.
    """
    digit_sums = []
    repetition_scores = []

    for base in BASES:
        rep = decimal_fraction_to_base(x, base, DECIMAL_DIGITS)
        digit_sums.append(digit_sum(rep))
        repetition_scores.append(repetition_score(rep))

    avg_digit_sum = sum(digit_sums) / len(digit_sums)
    digit_sum_span = max(digit_sums) - min(digit_sums)
    avg_repetition = sum(repetition_scores) / len(repetition_scores)
    repetition_span = max(repetition_scores) - min(repetition_scores)

    return {
        "avg_digit_sum": avg_digit_sum,
        "digit_sum_span": float(digit_sum_span),
        "avg_repetition": avg_repetition,
        "repetition_span": repetition_span,
    }


def run_experiment(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r",
        "step",
        "x",
        "avg_digit_sum",
        "digit_sum_span",
        "avg_repetition",
        "repetition_span",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in R_VALUES:
            trajectory = generate_trajectory(r)
            for step_idx, x in enumerate(trajectory):
                sig = compute_signatures(x)
                writer.writerow(
                    {
                        "r": r,
                        "step": step_idx,
                        "x": f"{x:.18f}",
                        "avg_digit_sum": sig["avg_digit_sum"],
                        "digit_sum_span": sig["digit_sum_span"],
                        "avg_repetition": sig["avg_repetition"],
                        "repetition_span": sig["repetition_span"],
                    }
                )


if __name__ == "__main__":
    run_experiment(Path("outputs/logistic_map_multibase_v0.csv"))
    print("Done. Wrote outputs/logistic_map_multibase_v0.csv")