from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math
import random

getcontext().prec = 50

SAMPLE_COUNT = 12000
BASES = list(range(2, 17))
DECIMAL_DIGITS = 12
RANDOM_SEED = 42

SERIES_NAMES = [
    "pure_noise",
    "trend_plus_noise",
    "mean_reverting",
    "chaotic_driver_market",
]


def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x >= 1.0:
        return 0.999999999999
    return x


def decimal_fraction_to_base(x: Decimal, base: int, digits: int = DECIMAL_DIGITS) -> str:
    if not (Decimal("0") <= x < Decimal("1")):
        if x == Decimal("1"):
            x = Decimal("0.999999999999")
        else:
            raise ValueError(f"x must be in [0,1), got {x}")

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


def transition_entropy_score(base_repr: str) -> float:
    if len(base_repr) < 2:
        return 0.0
    pairs = [base_repr[i : i + 2] for i in range(len(base_repr) - 1)]
    return len(set(pairs)) / len(pairs)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / len(values))


def build_relative_deltas(values: list[float]) -> list[float]:
    out = [0.0]
    for prev, curr in zip(values[:-1], values[1:]):
        if prev == 0.0:
            out.append(0.0 if curr == 0.0 else 1.0)
        else:
            out.append((curr - prev) / abs(prev))
    return out


def component_signature(x: Decimal) -> dict[str, float]:
    digit_sums = []
    repetition_scores = []
    transition_scores = []

    for base in BASES:
        rep = decimal_fraction_to_base(x, base, DECIMAL_DIGITS)
        digit_sums.append(digit_sum(rep))
        repetition_scores.append(repetition_score(rep))
        transition_scores.append(transition_entropy_score(rep))

    return {
        "digit_sum_span": float(max(digit_sums) - min(digit_sums)),
        "repetition_span": float(max(repetition_scores) - min(repetition_scores)),
        "transition_entropy_span": float(max(transition_scores) - min(transition_scores)),
        "digit_sum_mean": mean(digit_sums),
        "repetition_mean": mean(repetition_scores),
        "transition_entropy_mean": mean(transition_scores),
    }


def generate_pure_noise(n: int, seed: int) -> list[Decimal]:
    rng = random.Random(seed)
    return [Decimal(str(rng.random())) for _ in range(n)]


def generate_trend_plus_noise(n: int, seed: int) -> list[Decimal]:
    rng = random.Random(seed)
    out = []
    price = 0.2
    drift = 0.00003

    for _ in range(n):
        noise = rng.gauss(0.0, 0.01)
        price = price + drift + noise
        price = clamp01(price)
        out.append(Decimal(str(price)))

    return out


def generate_mean_reverting(n: int, seed: int) -> list[Decimal]:
    rng = random.Random(seed)
    out = []
    x = 0.5
    theta = 0.08

    for _ in range(n):
        noise = rng.gauss(0.0, 0.015)
        x = x + theta * (0.5 - x) + noise
        x = clamp01(x)
        out.append(Decimal(str(x)))

    return out


def generate_chaotic_driver_market(n: int) -> list[Decimal]:
    out = []
    x = Decimal("0.173421")
    r = Decimal("3.97")
    price = 0.5

    for _ in range(n + 300):
        x = r * x * (Decimal("1") - x)
        chaos = float(x) - 0.5
        price = price + 0.0035 * chaos + 0.002 * math.tanh(8.0 * chaos)
        price = clamp01(price)
        out.append(Decimal(str(price)))

    return out[300:]


def generate_series(name: str, n: int, seed: int) -> list[Decimal]:
    if name == "pure_noise":
        return generate_pure_noise(n, seed)
    if name == "trend_plus_noise":
        return generate_trend_plus_noise(n, seed)
    if name == "mean_reverting":
        return generate_mean_reverting(n, seed)
    if name == "chaotic_driver_market":
        return generate_chaotic_driver_market(n)
    raise ValueError(f"Unknown series: {name}")


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


def summarize_series(name: str, n: int, seed: int) -> dict[str, float]:
    seq = generate_series(name, n, seed)

    digit_sum_spans = []
    repetition_spans = []
    transition_entropy_spans = []

    digit_sum_means = []
    repetition_means = []
    transition_entropy_means = []

    values = [float(x) for x in seq]
    rel_value = build_relative_deltas(values)

    for x in seq:
        sig = component_signature(x)
        digit_sum_spans.append(sig["digit_sum_span"])
        repetition_spans.append(sig["repetition_span"])
        transition_entropy_spans.append(sig["transition_entropy_span"])

        digit_sum_means.append(sig["digit_sum_mean"])
        repetition_means.append(sig["repetition_mean"])
        transition_entropy_means.append(sig["transition_entropy_mean"])

    rel_digit = build_relative_deltas(digit_sum_spans)
    rel_rep = build_relative_deltas(repetition_spans)
    rel_trans = build_relative_deltas(transition_entropy_spans)

    return {
        "series": name,
        "value_std": std(values),
        "rel_value_abs_mean": mean([abs(v) for v in rel_value]),
        "digit_sum_span_std": std(digit_sum_spans),
        "repetition_span_std": std(repetition_spans),
        "transition_entropy_span_std": std(transition_entropy_spans),
        "digit_sum_mean_std": std(digit_sum_means),
        "repetition_mean_std": std(repetition_means),
        "transition_entropy_mean_std": std(transition_entropy_means),
        "rel_digit_abs_mean": mean([abs(v) for v in rel_digit]),
        "rel_rep_abs_mean": mean([abs(v) for v in rel_rep]),
        "rel_trans_abs_mean": mean([abs(v) for v in rel_trans]),
    }


def attach_scores(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    vstd = [r["value_std"] for r in rows]
    rv = [r["rel_value_abs_mean"] for r in rows]
    dss = [r["digit_sum_span_std"] for r in rows]
    rss = [r["repetition_span_std"] for r in rows]
    tss = [r["transition_entropy_span_std"] for r in rows]
    dms = [r["digit_sum_mean_std"] for r in rows]
    rms = [r["repetition_mean_std"] for r in rows]
    tms = [r["transition_entropy_mean_std"] for r in rows]
    rda = [r["rel_digit_abs_mean"] for r in rows]
    rra = [r["rel_rep_abs_mean"] for r in rows]
    rta = [r["rel_trans_abs_mean"] for r in rows]

    vstd_lo, vstd_hi = minmax_params(vstd)
    rv_lo, rv_hi = minmax_params(rv)
    dss_lo, dss_hi = minmax_params(dss)
    rss_lo, rss_hi = minmax_params(rss)
    tss_lo, tss_hi = minmax_params(tss)
    dms_lo, dms_hi = minmax_params(dms)
    rms_lo, rms_hi = minmax_params(rms)
    tms_lo, tms_hi = minmax_params(tms)
    rda_lo, rda_hi = minmax_params(rda)
    rra_lo, rra_hi = minmax_params(rra)
    rta_lo, rta_hi = minmax_params(rta)

    out = []
    for row in rows:
        norm_vstd = minmax_norm(row["value_std"], vstd_lo, vstd_hi)
        norm_rv = minmax_norm(row["rel_value_abs_mean"], rv_lo, rv_hi)
        norm_dss = minmax_norm(row["digit_sum_span_std"], dss_lo, dss_hi)
        norm_rss = minmax_norm(row["repetition_span_std"], rss_lo, rss_hi)
        norm_tss = minmax_norm(row["transition_entropy_span_std"], tss_lo, tss_hi)
        norm_dms = minmax_norm(row["digit_sum_mean_std"], dms_lo, dms_hi)
        norm_rms = minmax_norm(row["repetition_mean_std"], rms_lo, rms_hi)
        norm_tms = minmax_norm(row["transition_entropy_mean_std"], tms_lo, tms_hi)
        norm_rda = minmax_norm(row["rel_digit_abs_mean"], rda_lo, rda_hi)
        norm_rra = minmax_norm(row["rel_rep_abs_mean"], rra_lo, rra_hi)
        norm_rta = minmax_norm(row["rel_trans_abs_mean"], rta_lo, rta_hi)

        structure_score = (
            0.10 * norm_vstd
            + 0.10 * norm_rv
            + 0.14 * norm_dss
            + 0.08 * norm_rss
            + 0.14 * norm_tss
            + 0.10 * norm_dms
            + 0.06 * norm_rms
            + 0.10 * norm_tms
            + 0.08 * norm_rda
            + 0.04 * norm_rra
            + 0.06 * norm_rta
        )

        out.append({**row, "structure_score_v1": structure_score})
    return out


def qualitative_label(name: str) -> str:
    if name == "pure_noise":
        return "noise_reference"
    if name == "trend_plus_noise":
        return "trend_regime_reference"
    if name == "mean_reverting":
        return "mean_reverting_reference"
    if name == "chaotic_driver_market":
        return "latent_chaotic_driver_reference"
    return "unknown"


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = [summarize_series(name, SAMPLE_COUNT, RANDOM_SEED) for name in SERIES_NAMES]
    rows = attach_scores(rows)
    rows_sorted = sorted(rows, key=lambda r: r["structure_score_v1"], reverse=True)

    fieldnames = [
        "series",
        "reference_label",
        "value_std",
        "rel_value_abs_mean",
        "digit_sum_span_std",
        "repetition_span_std",
        "transition_entropy_span_std",
        "digit_sum_mean_std",
        "repetition_mean_std",
        "transition_entropy_mean_std",
        "rel_digit_abs_mean",
        "rel_rep_abs_mean",
        "rel_trans_abs_mean",
        "structure_score_v1",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE SYNTHETIC MARKET MULTIBASE V1")
        print("-" * 108)

        for row in rows_sorted:
            writer.writerow(
                {
                    "series": row["series"],
                    "reference_label": qualitative_label(row["series"]),
                    "value_std": row["value_std"],
                    "rel_value_abs_mean": row["rel_value_abs_mean"],
                    "digit_sum_span_std": row["digit_sum_span_std"],
                    "repetition_span_std": row["repetition_span_std"],
                    "transition_entropy_span_std": row["transition_entropy_span_std"],
                    "digit_sum_mean_std": row["digit_sum_mean_std"],
                    "repetition_mean_std": row["repetition_mean_std"],
                    "transition_entropy_mean_std": row["transition_entropy_mean_std"],
                    "rel_digit_abs_mean": row["rel_digit_abs_mean"],
                    "rel_rep_abs_mean": row["rel_rep_abs_mean"],
                    "rel_trans_abs_mean": row["rel_trans_abs_mean"],
                    "structure_score_v1": row["structure_score_v1"],
                }
            )

            print(
                f"series={row['series']} | "
                f"structure={row['structure_score_v1']:.6f} | "
                f"value_std={row['value_std']:.6f} | "
                f"digit_span={row['digit_sum_span_std']:.6f} | "
                f"trans_span={row['transition_entropy_span_std']:.6f}"
            )

        print("-" * 108)
        print("ranking:")
        for idx, row in enumerate(rows_sorted, start=1):
            print(f"{idx}. {row['series']} -> {row['structure_score_v1']:.6f}")
        print("-" * 108)
        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/synthetic_market_multibase_v1.csv"))