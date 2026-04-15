from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math
import random

getcontext().prec = 50

X0 = Decimal("0.123456")
TOTAL_STEPS = 600
BURN_IN = 300
BASES = list(range(2, 17))
DECIMAL_DIGITS = 12
NOISE_STD = 0.0005
RANDOM_SEED = 42

# Representative regimes:
# - periodic
# - transition edge
# - ordered window inside chaos
# - chaotic regime
R_VALUES = [
    Decimal("3.540"),
    Decimal("3.566"),
    Decimal("3.829"),
    Decimal("3.851"),
]


def logistic_map_step(x: Decimal, r: Decimal) -> Decimal:
    return r * x * (Decimal(1) - x)


def clamp_unit_interval(x: Decimal) -> Decimal:
    if x < Decimal("0"):
        return Decimal("0")
    if x > Decimal("1"):
        return Decimal("1")
    return x


def generate_trajectory(r: Decimal, noisy: bool, rng: random.Random) -> list[Decimal]:
    x = X0
    values: list[Decimal] = []

    for _ in range(TOTAL_STEPS):
        x = logistic_map_step(x, r)

        if noisy:
            noise = Decimal(str(rng.gauss(0.0, NOISE_STD)))
            x = clamp_unit_interval(x + noise)

        values.append(x)

    return values[BURN_IN:]


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


def build_relative_deltas(rows: list[dict[str, float]]) -> tuple[list[float], list[float]]:
    rel_digit = [0.0]
    rel_rep = [0.0]

    for prev, curr in zip(rows[:-1], rows[1:]):
        prev_digit = prev["digit_sum_span_std"]
        prev_rep = prev["repetition_span_std"]

        if prev_digit == 0.0:
            rel_digit.append(0.0 if curr["digit_sum_span_std"] == 0.0 else 1.0)
        else:
            rel_digit.append((curr["digit_sum_span_std"] - prev_digit) / abs(prev_digit))

        if prev_rep == 0.0:
            rel_rep.append(0.0 if curr["repetition_span_std"] == 0.0 else 1.0)
        else:
            rel_rep.append((curr["repetition_span_std"] - prev_rep) / abs(prev_rep))

    return rel_digit, rel_rep


def attach_scores(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    rel_digit_deltas, rel_rep_deltas = build_relative_deltas(rows)

    unique_vals = [row["unique_states"] for row in rows]
    digit_vals = [row["digit_sum_span_std"] for row in rows]
    rep_vals = [row["repetition_span_std"] for row in rows]

    unique_lo, unique_hi = minmax_params(unique_vals)
    digit_lo, digit_hi = minmax_params(digit_vals)
    rep_lo, rep_hi = minmax_params(rep_vals)
    rel_digit_lo, rel_digit_hi = minmax_params(rel_digit_deltas)
    rel_rep_lo, rel_rep_hi = minmax_params(rel_rep_deltas)

    out: list[dict[str, float]] = []

    for row, rel_digit, rel_rep in zip(rows, rel_digit_deltas, rel_rep_deltas):
        norm_unique = minmax_norm(row["unique_states"], unique_lo, unique_hi)
        norm_digit = minmax_norm(row["digit_sum_span_std"], digit_lo, digit_hi)
        norm_rep = minmax_norm(row["repetition_span_std"], rep_lo, rep_hi)
        norm_rel_digit = minmax_norm(rel_digit, rel_digit_lo, rel_digit_hi)
        norm_rel_rep = minmax_norm(rel_rep, rel_rep_lo, rel_rep_hi)

        order_score = (
            0.45 * (1.0 - norm_unique)
            + 0.35 * (1.0 - norm_digit)
            + 0.20 * (1.0 - norm_rep)
        )

        event_score = (
            0.25 * norm_digit
            + 0.20 * norm_rep
            + 0.35 * norm_rel_digit
            + 0.20 * norm_rel_rep
        )

        transition_score = (
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
                "order_score_v1": order_score,
                "event_score_v1": event_score,
                "transition_score_v1": transition_score,
            }
        )

    return out


def run(output_csv: Path) -> None:
    rng = random.Random(RANDOM_SEED)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    raw_rows = []
    for noisy in [False, True]:
        regime_rows = []
        for r in R_VALUES:
            xs = generate_trajectory(r, noisy=noisy, rng=rng)
            summary = summarize_regime(xs)
            regime_rows.append(
                {
                    "condition": "noisy" if noisy else "clean",
                    "r": float(r),
                    **summary,
                }
            )

        scored_rows = attach_scores(regime_rows)
        raw_rows.extend(scored_rows)

    fieldnames = [
        "condition",
        "r",
        "unique_states",
        "x_std",
        "digit_sum_span_std",
        "repetition_span_std",
        "rel_delta_digit_sum_span_std",
        "rel_delta_repetition_span_std",
        "order_score_v1",
        "event_score_v1",
        "transition_score_v1",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE LOGISTIC MAP NOISE ROBUSTNESS V1")
        print("-" * 88)

        for row in raw_rows:
            writer.writerow(
                {
                    "condition": row["condition"],
                    "r": f"{row['r']:.3f}",
                    "unique_states": int(row["unique_states"]),
                    "x_std": row["x_std"],
                    "digit_sum_span_std": row["digit_sum_span_std"],
                    "repetition_span_std": row["repetition_span_std"],
                    "rel_delta_digit_sum_span_std": row["rel_delta_digit_sum_span_std"],
                    "rel_delta_repetition_span_std": row["rel_delta_repetition_span_std"],
                    "order_score_v1": row["order_score_v1"],
                    "event_score_v1": row["event_score_v1"],
                    "transition_score_v1": row["transition_score_v1"],
                }
            )

            print(
                f"{row['condition']:>5} | "
                f"r={row['r']:.3f} | "
                f"states={int(row['unique_states'])} | "
                f"order={row['order_score_v1']:.6f} | "
                f"event={row['event_score_v1']:.6f} | "
                f"mixed={row['transition_score_v1']:.6f}"
            )

        print("-" * 88)
        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/logistic_map_noise_robustness_v1.csv"))