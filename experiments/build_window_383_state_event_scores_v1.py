from __future__ import annotations

from pathlib import Path
import csv
import math

INPUT_CSV = Path("outputs/logistic_map_window_383_v1.csv")
OUTPUT_CSV = Path("outputs/logistic_map_window_383_state_event_scores_v1.csv")


def parse_float(value: str) -> float:
    value = value.strip().lower()
    if value == "inf":
        return math.inf
    if value == "-inf":
        return -math.inf
    return float(value)


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
                    "transition_score_v1": float(row["transition_score_v1"]),
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


def build_local_relative_deltas(rows: list[dict[str, float]]) -> tuple[list[float], list[float]]:
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


def run() -> None:
    rows = load_rows(INPUT_CSV)
    rel_digit_deltas, rel_rep_deltas = build_local_relative_deltas(rows)

    unique_vals = [row["unique_states"] for row in rows]
    digit_vals = [row["digit_sum_span_std"] for row in rows]
    rep_vals = [row["repetition_span_std"] for row in rows]

    unique_lo, unique_hi = minmax_params(unique_vals)
    digit_lo, digit_hi = minmax_params(digit_vals)
    rep_lo, rep_hi = minmax_params(rep_vals)
    rel_digit_lo, rel_digit_hi = minmax_params(rel_digit_deltas)
    rel_rep_lo, rel_rep_hi = minmax_params(rel_rep_deltas)

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
        "transition_score_v1",
    ]

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE WINDOW 3.83 STATE / EVENT SCORE V1")
        print("-" * 84)

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

            writer.writerow(
                {
                    "r": f"{row['r']:.3f}",
                    "unique_states": int(row["unique_states"]),
                    "x_std": row["x_std"],
                    "digit_sum_span_std": row["digit_sum_span_std"],
                    "repetition_span_std": row["repetition_span_std"],
                    "rel_delta_digit_sum_span_std": rel_digit,
                    "rel_delta_repetition_span_std": rel_rep,
                    "order_score_v1": order_score,
                    "event_score_v1": event_score,
                    "transition_score_v1": row["transition_score_v1"],
                }
            )

            print(
                f"r={row['r']:.3f} | "
                f"states={int(row['unique_states'])} | "
                f"order={order_score:.6f} | "
                f"event={event_score:.6f} | "
                f"mixed={row['transition_score_v1']:.6f}"
            )

        print("-" * 84)
        print(f"Done. Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    run()