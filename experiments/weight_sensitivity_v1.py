from __future__ import annotations

from pathlib import Path
import csv
import math

INPUT_CSV = Path("outputs/logistic_map_window_383_state_event_scores_v1.csv")
OUTPUT_CSV = Path("outputs/logistic_map_weight_sensitivity_v1.csv")

# Alternative weight sets to test qualitative stability
ORDER_WEIGHT_SETS = {
    "order_base": (0.45, 0.35, 0.20),
    "order_more_unique": (0.55, 0.25, 0.20),
    "order_more_digit": (0.35, 0.45, 0.20),
    "order_more_rep": (0.40, 0.25, 0.35),
}

EVENT_WEIGHT_SETS = {
    "event_base": (0.25, 0.20, 0.35, 0.20),
    "event_more_delta": (0.15, 0.15, 0.45, 0.25),
    "event_more_static": (0.35, 0.30, 0.20, 0.15),
    "event_more_rep_delta": (0.20, 0.15, 0.25, 0.40),
}


def load_rows(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "r": float(row["r"]),
                    "unique_states": float(row["unique_states"]),
                    "x_std": float(row["x_std"]),
                    "digit_sum_span_std": float(row["digit_sum_span_std"]),
                    "repetition_span_std": float(row["repetition_span_std"]),
                    "rel_delta_digit_sum_span_std": float(row["rel_delta_digit_sum_span_std"]),
                    "rel_delta_repetition_span_std": float(row["rel_delta_repetition_span_std"]),
                }
            )
    rows.sort(key=lambda x: x["r"])
    return rows


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


def compute_normalized_fields(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    unique_vals = [row["unique_states"] for row in rows]
    digit_vals = [row["digit_sum_span_std"] for row in rows]
    rep_vals = [row["repetition_span_std"] for row in rows]
    rel_digit_vals = [row["rel_delta_digit_sum_span_std"] for row in rows]
    rel_rep_vals = [row["rel_delta_repetition_span_std"] for row in rows]

    unique_lo, unique_hi = minmax_params(unique_vals)
    digit_lo, digit_hi = minmax_params(digit_vals)
    rep_lo, rep_hi = minmax_params(rep_vals)
    rel_digit_lo, rel_digit_hi = minmax_params(rel_digit_vals)
    rel_rep_lo, rel_rep_hi = minmax_params(rel_rep_vals)

    out = []
    for row in rows:
        out.append(
            {
                **row,
                "norm_unique": minmax_norm(row["unique_states"], unique_lo, unique_hi),
                "norm_digit": minmax_norm(row["digit_sum_span_std"], digit_lo, digit_hi),
                "norm_rep": minmax_norm(row["repetition_span_std"], rep_lo, rep_hi),
                "norm_rel_digit": minmax_norm(row["rel_delta_digit_sum_span_std"], rel_digit_lo, rel_digit_hi),
                "norm_rel_rep": minmax_norm(row["rel_delta_repetition_span_std"], rel_rep_lo, rel_rep_hi),
            }
        )
    return out


def run() -> None:
    rows = load_rows(INPUT_CSV)
    rows = compute_normalized_fields(rows)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r",
        "unique_states",
        "order_profile",
        "event_profile",
        "order_score",
        "event_score",
    ]

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE WEIGHT SENSITIVITY V1")
        print("-" * 88)

        for order_name, (wu, wd, wr) in ORDER_WEIGHT_SETS.items():
            for event_name, (ed, er, erd, err) in EVENT_WEIGHT_SETS.items():
                print(f"{order_name} + {event_name}")

                for row in rows:
                    order_score = (
                        wu * (1.0 - row["norm_unique"])
                        + wd * (1.0 - row["norm_digit"])
                        + wr * (1.0 - row["norm_rep"])
                    )

                    event_score = (
                        ed * row["norm_digit"]
                        + er * row["norm_rep"]
                        + erd * row["norm_rel_digit"]
                        + err * row["norm_rel_rep"]
                    )

                    writer.writerow(
                        {
                            "r": f"{row['r']:.3f}",
                            "unique_states": int(row["unique_states"]),
                            "order_profile": order_name,
                            "event_profile": event_name,
                            "order_score": order_score,
                            "event_score": event_score,
                        }
                    )

                    # Print only key diagnostic points
                    if row["r"] in {3.827, 3.829, 3.845, 3.851}:
                        print(
                            f"  r={row['r']:.3f} | "
                            f"states={int(row['unique_states'])} | "
                            f"order={order_score:.6f} | "
                            f"event={event_score:.6f}"
                        )

                print("-" * 88)

        print(f"Done. Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    run()