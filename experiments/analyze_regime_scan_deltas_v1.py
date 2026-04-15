from __future__ import annotations

from pathlib import Path
import csv

INPUT_CSV = Path("outputs/logistic_map_regime_scan_v1.csv")
OUTPUT_CSV = Path("outputs/logistic_map_regime_scan_deltas_v1.csv")


def load_rows(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "r": float(row["r"]),
                    "unique_states_rounded_12": float(row["unique_states_rounded_12"]),
                    "x_std": float(row["x_std"]),
                    "avg_digit_sum_std": float(row["avg_digit_sum_std"]),
                    "digit_sum_span_std": float(row["digit_sum_span_std"]),
                    "avg_repetition_std": float(row["avg_repetition_std"]),
                    "repetition_span_std": float(row["repetition_span_std"]),
                }
            )
    rows.sort(key=lambda x: x["r"])
    return rows


def safe_rel_delta(prev: float, curr: float) -> float:
    if prev == 0.0:
        return 0.0 if curr == 0.0 else float("inf")
    return (curr - prev) / abs(prev)


def run(input_csv: Path, output_csv: Path) -> None:
    rows = load_rows(input_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r_prev",
        "r_curr",
        "delta_r",
        "unique_states_prev",
        "unique_states_curr",
        "delta_unique_states",
        "x_std_prev",
        "x_std_curr",
        "delta_x_std",
        "rel_delta_x_std",
        "digit_sum_span_std_prev",
        "digit_sum_span_std_curr",
        "delta_digit_sum_span_std",
        "rel_delta_digit_sum_span_std",
        "repetition_span_std_prev",
        "repetition_span_std_curr",
        "delta_repetition_span_std",
        "rel_delta_repetition_span_std",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE REGIME DELTA ANALYSIS")
        print("-" * 72)

        for prev, curr in zip(rows[:-1], rows[1:]):
            delta_r = curr["r"] - prev["r"]

            delta_unique_states = curr["unique_states_rounded_12"] - prev["unique_states_rounded_12"]

            delta_x_std = curr["x_std"] - prev["x_std"]
            rel_delta_x_std = safe_rel_delta(prev["x_std"], curr["x_std"])

            delta_digit_sum_span_std = curr["digit_sum_span_std"] - prev["digit_sum_span_std"]
            rel_delta_digit_sum_span_std = safe_rel_delta(
                prev["digit_sum_span_std"], curr["digit_sum_span_std"]
            )

            delta_repetition_span_std = curr["repetition_span_std"] - prev["repetition_span_std"]
            rel_delta_repetition_span_std = safe_rel_delta(
                prev["repetition_span_std"], curr["repetition_span_std"]
            )

            writer.writerow(
                {
                    "r_prev": f"{prev['r']:.3f}",
                    "r_curr": f"{curr['r']:.3f}",
                    "delta_r": f"{delta_r:.3f}",
                    "unique_states_prev": int(prev["unique_states_rounded_12"]),
                    "unique_states_curr": int(curr["unique_states_rounded_12"]),
                    "delta_unique_states": int(delta_unique_states),
                    "x_std_prev": prev["x_std"],
                    "x_std_curr": curr["x_std"],
                    "delta_x_std": delta_x_std,
                    "rel_delta_x_std": rel_delta_x_std,
                    "digit_sum_span_std_prev": prev["digit_sum_span_std"],
                    "digit_sum_span_std_curr": curr["digit_sum_span_std"],
                    "delta_digit_sum_span_std": delta_digit_sum_span_std,
                    "rel_delta_digit_sum_span_std": rel_delta_digit_sum_span_std,
                    "repetition_span_std_prev": prev["repetition_span_std"],
                    "repetition_span_std_curr": curr["repetition_span_std"],
                    "delta_repetition_span_std": delta_repetition_span_std,
                    "rel_delta_repetition_span_std": rel_delta_repetition_span_std,
                }
            )

            print(
                f"{prev['r']:.3f} -> {curr['r']:.3f} | "
                f"states {int(prev['unique_states_rounded_12'])} -> {int(curr['unique_states_rounded_12'])} | "
                f"d_x_std={delta_x_std:.8f} | "
                f"d_digit_span={delta_digit_sum_span_std:.8f} | "
                f"d_rep_span={delta_repetition_span_std:.8f}"
            )

        print("-" * 72)
        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(INPUT_CSV, OUTPUT_CSV)