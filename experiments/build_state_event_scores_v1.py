from __future__ import annotations

from pathlib import Path
import csv
import math

INPUT_SCAN_CSV = Path("outputs/logistic_map_regime_scan_v1.csv")
INPUT_DELTA_CSV = Path("outputs/logistic_map_regime_scan_deltas_v1.csv")
OUTPUT_CSV = Path("outputs/logistic_map_state_event_scores_v1.csv")


def parse_float(value: str) -> float:
    value = value.strip().lower()
    if value == "inf":
        return math.inf
    if value == "-inf":
        return -math.inf
    return float(value)


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
    scan_rows = load_scan_rows(INPUT_SCAN_CSV)
    delta_by_r = load_delta_rows(INPUT_DELTA_CSV)

    unique_states_vals = [row["unique_states"] for row in scan_rows]
    digit_span_vals = [row["digit_sum_span_std"] for row in scan_rows]
    rep_span_vals = [row["repetition_span_std"] for row in scan_rows]

    rel_digit_delta_vals = []
    rel_rep_delta_vals = []
    for row in scan_rows:
        d = delta_by_r.get(row["r"])
        if d is not None:
            rel_digit_delta_vals.append(d["rel_delta_digit_sum_span_std"])
            rel_rep_delta_vals.append(d["rel_delta_repetition_span_std"])

    unique_lo, unique_hi = minmax_params(unique_states_vals)
    digit_lo, digit_hi = minmax_params(digit_span_vals)
    rep_lo, rep_hi = minmax_params(rep_span_vals)
    rel_digit_lo, rel_digit_hi = minmax_params(rel_digit_delta_vals)
    rel_rep_lo, rel_rep_hi = minmax_params(rel_rep_delta_vals)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r",
        "unique_states",
        "x_std",
        "digit_sum_span_std",
        "repetition_span_std",
        "rel_delta_digit_sum_span_std",
        "rel_delta_repetition_span_std",
        "order_score_v1",
        "event_score_v1",
    ]

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE STATE / EVENT SCORE V1")
        print("-" * 80)

        for row in scan_rows:
            r = row["r"]
            d = delta_by_r.get(r, None)

            rel_digit = 0.0
            rel_rep = 0.0
            if d is not None:
                rel_digit = d["rel_delta_digit_sum_span_std"]
                rel_rep = d["rel_delta_repetition_span_std"]
                if not math.isfinite(rel_rep):
                    rel_rep = 1.0

            norm_unique = minmax_norm(row["unique_states"], unique_lo, unique_hi)
            norm_digit = minmax_norm(row["digit_sum_span_std"], digit_lo, digit_hi)
            norm_rep = minmax_norm(row["repetition_span_std"], rep_lo, rep_hi)
            norm_rel_digit = minmax_norm(rel_digit, rel_digit_lo, rel_digit_hi)
            norm_rel_rep = minmax_norm(rel_rep, rel_rep_lo, rel_rep_hi)

            # ORDER:
            # high when unique_states is low and cross-base dispersion is low
            order_score = (
                0.45 * (1.0 - norm_unique)
                + 0.35 * (1.0 - norm_digit)
                + 0.20 * (1.0 - norm_rep)
            )

            # EVENT:
            # high when local relative change is strong and cross-base tension is high
            event_score = (
                0.25 * norm_digit
                + 0.20 * norm_rep
                + 0.35 * norm_rel_digit
                + 0.20 * norm_rel_rep
            )

            writer.writerow(
                {
                    "r": f"{r:.3f}",
                    "unique_states": int(row["unique_states"]),
                    "x_std": row["x_std"],
                    "digit_sum_span_std": row["digit_sum_span_std"],
                    "repetition_span_std": row["repetition_span_std"],
                    "rel_delta_digit_sum_span_std": rel_digit,
                    "rel_delta_repetition_span_std": rel_rep,
                    "order_score_v1": order_score,
                    "event_score_v1": event_score,
                }
            )

            print(
                f"r={r:.3f} | "
                f"states={int(row['unique_states'])} | "
                f"order={order_score:.6f} | "
                f"event={event_score:.6f}"
            )

        print("-" * 80)
        print(f"Done. Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    run()