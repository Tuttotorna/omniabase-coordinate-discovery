from __future__ import annotations

from pathlib import Path
import csv
import math
from statistics import mean

INPUT_CSV = Path("outputs/logistic_map_regime_scan_v1.csv")
DELTA_CSV = Path("outputs/logistic_map_regime_scan_deltas_v1.csv")
OUTPUT_CSV = Path("outputs/logistic_map_transition_score_v1.csv")


def load_scan_rows(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "r": float(row["r"]),
                    "unique_states": float(row["unique_states_rounded_12"]),
                    "x_std": float(row["x_std"]),
                    "avg_digit_sum_std": float(row["avg_digit_sum_std"]),
                    "digit_sum_span_std": float(row["digit_sum_span_std"]),
                    "avg_repetition_std": float(row["avg_repetition_std"]),
                    "repetition_span_std": float(row["repetition_span_std"]),
                }
            )
    rows.sort(key=lambda x: x["r"])
    return rows


def load_delta_rows(path: Path) -> dict[float, dict[str, float]]:
    out: dict[float, dict[str, float]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r_curr = float(row["r_curr"])
            out[r_curr] = {
                "delta_unique_states": float(row["delta_unique_states"]),
                "delta_x_std": float(row["delta_x_std"]),
                "rel_delta_x_std": parse_float(row["rel_delta_x_std"]),
                "delta_digit_sum_span_std": float(row["delta_digit_sum_span_std"]),
                "rel_delta_digit_sum_span_std": parse_float(row["rel_delta_digit_sum_span_std"]),
                "delta_repetition_span_std": float(row["delta_repetition_span_std"]),
                "rel_delta_repetition_span_std": parse_float(row["rel_delta_repetition_span_std"]),
            }
    return out


def parse_float(value: str) -> float:
    value = value.strip().lower()
    if value == "inf":
        return math.inf
    if value == "-inf":
        return -math.inf
    return float(value)


def finite_values(values: list[float]) -> list[float]:
    return [v for v in values if math.isfinite(v)]


def minmax_params(values: list[float]) -> tuple[float, float]:
    vals = finite_values(values)
    if not vals:
        return 0.0, 1.0
    lo = min(vals)
    hi = max(vals)
    if hi == lo:
        return lo, hi + 1.0
    return lo, hi


def minmax_norm(x: float, lo: float, hi: float) -> float:
    if not math.isfinite(x):
        return 1.0
    if hi == lo:
        return 0.0
    y = (x - lo) / (hi - lo)
    return max(0.0, min(1.0, y))


def run() -> None:
    scan_rows = load_scan_rows(INPUT_CSV)
    delta_by_r = load_delta_rows(DELTA_CSV)

    digit_vals = [row["digit_sum_span_std"] for row in scan_rows]
    rep_vals = [row["repetition_span_std"] for row in scan_rows]
    rel_digit_vals = [
        delta_by_r[row["r"]]["rel_delta_digit_sum_span_std"]
        for row in scan_rows
        if row["r"] in delta_by_r
    ]
    rel_rep_vals = [
        delta_by_r[row["r"]]["rel_delta_repetition_span_std"]
        for row in scan_rows
        if row["r"] in delta_by_r and math.isfinite(delta_by_r[row["r"]]["rel_delta_repetition_span_std"])
    ]

    digit_lo, digit_hi = minmax_params(digit_vals)
    rep_lo, rep_hi = minmax_params(rep_vals)
    rel_digit_lo, rel_digit_hi = minmax_params(rel_digit_vals)
    rel_rep_lo, rel_rep_hi = minmax_params(rel_rep_vals)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r",
        "unique_states",
        "x_std",
        "digit_sum_span_std",
        "repetition_span_std",
        "rel_delta_digit_sum_span_std",
        "rel_delta_repetition_span_std",
        "norm_digit_sum_span_std",
        "norm_repetition_span_std",
        "norm_rel_delta_digit_sum_span_std",
        "norm_rel_delta_repetition_span_std",
        "transition_score_v1",
    ]

    scores: list[float] = []

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE TRANSITION SCORE V1")
        print("-" * 72)

        for row in scan_rows:
            r = row["r"]
            delta = delta_by_r.get(r)

            rel_digit = 0.0
            rel_rep = 0.0
            if delta is not None:
                rel_digit = delta["rel_delta_digit_sum_span_std"]
                rel_rep = delta["rel_delta_repetition_span_std"]
                if not math.isfinite(rel_rep):
                    rel_rep = 1.0

            norm_digit = minmax_norm(row["digit_sum_span_std"], digit_lo, digit_hi)
            norm_rep = minmax_norm(row["repetition_span_std"], rep_lo, rep_hi)
            norm_rel_digit = minmax_norm(rel_digit, rel_digit_lo, rel_digit_hi)
            norm_rel_rep = minmax_norm(rel_rep, rel_rep_lo, rel_rep_hi)

            # Weighted score:
            # - static cross-base disagreement
            # - static repetition dispersion
            # - local relative jump in disagreement
            # - local relative jump in repetition dispersion
            score = (
                0.35 * norm_digit
                + 0.25 * norm_rep
                + 0.25 * norm_rel_digit
                + 0.15 * norm_rel_rep
            )

            scores.append(score)

            writer.writerow(
                {
                    "r": f"{r:.3f}",
                    "unique_states": int(row["unique_states"]),
                    "x_std": row["x_std"],
                    "digit_sum_span_std": row["digit_sum_span_std"],
                    "repetition_span_std": row["repetition_span_std"],
                    "rel_delta_digit_sum_span_std": rel_digit,
                    "rel_delta_repetition_span_std": rel_rep,
                    "norm_digit_sum_span_std": norm_digit,
                    "norm_repetition_span_std": norm_rep,
                    "norm_rel_delta_digit_sum_span_std": norm_rel_digit,
                    "norm_rel_delta_repetition_span_std": norm_rel_rep,
                    "transition_score_v1": score,
                }
            )

            print(
                f"r={r:.3f} | "
                f"states={int(row['unique_states'])} | "
                f"x_std={row['x_std']:.8f} | "
                f"digit_span={row['digit_sum_span_std']:.8f} | "
                f"rep_span={row['repetition_span_std']:.8f} | "
                f"score={score:.6f}"
            )

        print("-" * 72)
        print(f"mean_score={mean(scores):.6f}")
        print(f"max_score={max(scores):.6f}")
        print(f"min_score={min(scores):.6f}")
        print(f"Done. Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    run()