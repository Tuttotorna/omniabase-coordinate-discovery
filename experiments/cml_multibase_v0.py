from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

# Coupled Map Lattice (ring topology)
N = 10
R = Decimal("3.90")
EPSILON = Decimal("0.20")

TOTAL_STEPS = 1200
BURN_IN = 400

BASES = list(range(2, 17))
DECIMAL_DIGITS = 12


def logistic_local(x: Decimal, r: Decimal) -> Decimal:
    return r * x * (Decimal("1") - x)


def cml_step(state: list[Decimal], r: Decimal, epsilon: Decimal) -> list[Decimal]:
    n = len(state)
    local = [logistic_local(x, r) for x in state]
    out: list[Decimal] = []

    for i in range(n):
        left = local[(i - 1) % n]
        center = local[i]
        right = local[(i + 1) % n]

        x_next = (
            (Decimal("1") - epsilon) * center
            + (epsilon / Decimal("2")) * (left + right)
        )
        out.append(x_next)

    return out


def generate_initial_state(n: int) -> list[Decimal]:
    # Slight gradient to avoid trivial synchronization at start
    return [Decimal("0.1") + Decimal(i) * Decimal("0.03") for i in range(n)]


def generate_trajectory() -> list[list[Decimal]]:
    state = generate_initial_state(N)
    out: list[list[Decimal]] = []

    for _ in range(TOTAL_STEPS):
        state = cml_step(state, R, EPSILON)
        out.append(state[:])

    return out[BURN_IN:]


def minmax_scale(values: list[Decimal]) -> list[Decimal]:
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [Decimal("0.5") for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


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


def component_signature(z_scaled: Decimal) -> dict[str, float]:
    digit_sums = []
    repetition_scores = []

    for base in BASES:
        rep = decimal_fraction_to_base(z_scaled, base, DECIMAL_DIGITS)
        digit_sums.append(digit_sum(rep))
        repetition_scores.append(repetition_score(rep))

    return {
        "digit_sum_span": float(max(digit_sums) - min(digit_sums)),
        "repetition_span": float(max(repetition_scores) - min(repetition_scores)),
    }


def state_mean(state: list[Decimal]) -> Decimal:
    return sum(state) / Decimal(len(state))


def state_variance(state: list[Decimal]) -> float:
    m = float(state_mean(state))
    vals = [float(x) for x in state]
    return sum((v - m) ** 2 for v in vals) / len(vals)


def neighbor_gradient(state: list[Decimal]) -> float:
    n = len(state)
    diffs = []
    for i in range(n):
        diffs.append(abs(float(state[(i + 1) % n] - state[i])))
    return mean(diffs)


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    trajectory = generate_trajectory()

    # Per-site scaling across time
    per_site_series = [[step[i] for step in trajectory] for i in range(N)]
    per_site_scaled = [minmax_scale(series) for series in per_site_series]

    fieldnames = [
        "step",
        "state_mean",
        "state_variance",
        "neighbor_gradient",
        "component_digit_span_mean",
        "component_repetition_span_mean",
        "global_mean_digit_span",
        "global_mean_repetition_span",
        "global_variance_digit_span",
        "global_variance_repetition_span",
    ]

    component_digit_span_means = []
    component_rep_span_means = []
    global_mean_digit_spans = []
    global_mean_rep_spans = []
    global_var_digit_spans = []
    global_var_rep_spans = []

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for t, state in enumerate(trajectory):
            sigs = []
            scaled_state_now = []

            for i in range(N):
                z_scaled = per_site_scaled[i][t]
                scaled_state_now.append(z_scaled)
                sigs.append(component_signature(z_scaled))

            mean_scaled = state_mean(scaled_state_now)
            var_scaled = Decimal(str(state_variance(scaled_state_now)))

            sig_mean = component_signature(mean_scaled)
            sig_var = component_signature(var_scaled)

            component_digit_mean = mean([s["digit_sum_span"] for s in sigs])
            component_rep_mean = mean([s["repetition_span"] for s in sigs])

            component_digit_span_means.append(component_digit_mean)
            component_rep_span_means.append(component_rep_mean)
            global_mean_digit_spans.append(sig_mean["digit_sum_span"])
            global_mean_rep_spans.append(sig_mean["repetition_span"])
            global_var_digit_spans.append(sig_var["digit_sum_span"])
            global_var_rep_spans.append(sig_var["repetition_span"])

            writer.writerow(
                {
                    "step": t,
                    "state_mean": float(state_mean(state)),
                    "state_variance": state_variance(state),
                    "neighbor_gradient": neighbor_gradient(state),
                    "component_digit_span_mean": component_digit_mean,
                    "component_repetition_span_mean": component_rep_mean,
                    "global_mean_digit_span": sig_mean["digit_sum_span"],
                    "global_mean_repetition_span": sig_mean["repetition_span"],
                    "global_variance_digit_span": sig_var["digit_sum_span"],
                    "global_variance_repetition_span": sig_var["repetition_span"],
                }
            )

    print("OMNIABASE CML MULTIBASE V0")
    print("-" * 76)
    print(f"steps_written={len(trajectory)}")
    print(f"component_digit_span_mean_std={std(component_digit_span_means):.6f}")
    print(f"component_repetition_span_mean_std={std(component_rep_span_means):.6f}")
    print(f"global_mean_digit_span_std={std(global_mean_digit_spans):.6f}")
    print(f"global_mean_repetition_span_std={std(global_mean_rep_spans):.6f}")
    print(f"global_variance_digit_span_std={std(global_var_digit_spans):.6f}")
    print(f"global_variance_repetition_span_std={std(global_var_rep_spans):.6f}")
    print("-" * 76)
    print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/cml_multibase_v0.csv"))