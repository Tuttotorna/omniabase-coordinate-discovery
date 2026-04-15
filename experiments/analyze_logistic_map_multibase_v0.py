from __future__ import annotations

from pathlib import Path
import csv
import math
from collections import defaultdict


INPUT_CSV = Path("outputs/logistic_map_multibase_v0.csv")
OUTPUT_SUMMARY_CSV = Path("outputs/logistic_map_multibase_v0_summary.csv")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / len(values))


def mean_abs_step_diff(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    diffs = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
    return mean(diffs)


def load_rows(path: Path) -> dict[float, list[dict[str, float]]]:
    grouped: dict[float, list[dict[str, float]]] = defaultdict(list)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = float(row["r"])
            grouped[r].append(
                {
                    "step": float(row["step"]),
                    "x": float(row["x"]),
                    "avg_digit_sum": float(row["avg_digit_sum"]),
                    "digit_sum_span": float(row["digit_sum_span"]),
                    "avg_repetition": float(row["avg_repetition"]),
                    "repetition_span": float(row["repetition_span"]),
                }
            )

    return dict(sorted(grouped.items(), key=lambda kv: kv[0]))


def summarize_regime(rows: list[dict[str, float]]) -> dict[str, float]:
    xs = [row["x"] for row in rows]
    avg_digit_sum = [row["avg_digit_sum"] for row in rows]
    digit_sum_span = [row["digit_sum_span"] for row in rows]
    avg_repetition = [row["avg_repetition"] for row in rows]
    repetition_span = [row["repetition_span"] for row in rows]

    unique_states_rounded = len({round(x, 12) for x in xs})
    unique_avg_digit_sum_rounded = len({round(v, 12) for v in avg_digit_sum})
    unique_avg_repetition_rounded = len({round(v, 12) for v in avg_repetition})

    return {
        "n_steps": len(rows),
        "unique_states_rounded_12": unique_states_rounded,
        "unique_avg_digit_sum_rounded_12": unique_avg_digit_sum_rounded,
        "unique_avg_repetition_rounded_12": unique_avg_repetition_rounded,
        "x_mean": mean(xs),
        "x_std": std(xs),
        "x_mean_abs_step_diff": mean_abs_step_diff(xs),
        "avg_digit_sum_mean": mean(avg_digit_sum),
        "avg_digit_sum_std": std(avg_digit_sum),
        "avg_digit_sum_mean_abs_step_diff": mean_abs_step_diff(avg_digit_sum),
        "digit_sum_span_mean": mean(digit_sum_span),
        "digit_sum_span_std": std(digit_sum_span),
        "digit_sum_span_mean_abs_step_diff": mean_abs_step_diff(digit_sum_span),
        "avg_repetition_mean": mean(avg_repetition),
        "avg_repetition_std": std(avg_repetition),
        "avg_repetition_mean_abs_step_diff": mean_abs_step_diff(avg_repetition),
        "repetition_span_mean": mean(repetition_span),
        "repetition_span_std": std(repetition_span),
        "repetition_span_mean_abs_step_diff": mean_abs_step_diff(repetition_span),
    }


def write_summary(path: Path, grouped: dict[float, list[dict[str, float]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r",
        "n_steps",
        "unique_states_rounded_12",
        "unique_avg_digit_sum_rounded_12",
        "unique_avg_repetition_rounded_12",
        "x_mean",
        "x_std",
        "x_mean_abs_step_diff",
        "avg_digit_sum_mean",
        "avg_digit_sum_std",
        "avg_digit_sum_mean_abs_step_diff",
        "digit_sum_span_mean",
        "digit_sum_span_std",
        "digit_sum_span_mean_abs_step_diff",
        "avg_repetition_mean",
        "avg_repetition_std",
        "avg_repetition_mean_abs_step_diff",
        "repetition_span_mean",
        "repetition_span_std",
        "repetition_span_mean_abs_step_diff",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r, rows in grouped.items():
            summary = summarize_regime(rows)
            writer.writerow({"r": r, **summary})


def print_console_summary(grouped: dict[float, list[dict[str, float]]]) -> None:
    print("OMNIABASE COORDINATE DISCOVERY - REGIME SUMMARY")
    print("-" * 60)

    for r, rows in grouped.items():
        s = summarize_regime(rows)
        print(f"r = {r:.2f}")
        print(f"  n_steps: {int(s['n_steps'])}")
        print(f"  unique_states_rounded_12: {int(s['unique_states_rounded_12'])}")
        print(f"  x_std: {s['x_std']:.12f}")
        print(f"  x_mean_abs_step_diff: {s['x_mean_abs_step_diff']:.12f}")
        print(f"  avg_digit_sum_std: {s['avg_digit_sum_std']:.12f}")
        print(f"  avg_digit_sum_mean_abs_step_diff: {s['avg_digit_sum_mean_abs_step_diff']:.12f}")
        print(f"  digit_sum_span_std: {s['digit_sum_span_std']:.12f}")
        print(f"  avg_repetition_std: {s['avg_repetition_std']:.12f}")
        print(f"  repetition_span_std: {s['repetition_span_std']:.12f}")
        print("-" * 60)


if __name__ == "__main__":
    grouped = load_rows(INPUT_CSV)
    write_summary(OUTPUT_SUMMARY_CSV, grouped)
    print_console_summary(grouped)
    print(f"Done. Wrote {OUTPUT_SUMMARY_CSV}")