from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math
import random

getcontext().prec = 50

# Fixed Lorenz parameters
SIGMA = Decimal("10.0")
BETA = Decimal("2.6666666666666667")  # 8/3

# Simulated live regime change
RHO_BEFORE = Decimal("13.0")
RHO_AFTER = Decimal("25.0")
SWITCH_STEP = 6000

# Initial condition
X0 = Decimal("0.1")
Y0 = Decimal("0.0")
Z0 = Decimal("0.0")

# Integration settings
DT = Decimal("0.01")
TOTAL_STEPS = 12000
BURN_IN = 1000

BASES = list(range(2, 17))
DECIMAL_DIGITS = 12

# Rolling detection settings
WINDOW = 120
ALERT_THRESHOLD = 0.62

# Noise settings
NOISE_STD = 0.05
RANDOM_SEED = 42


def lorenz_derivatives(
    x: Decimal,
    y: Decimal,
    z: Decimal,
    sigma: Decimal,
    rho: Decimal,
    beta: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return dx, dy, dz


def rk4_step(
    x: Decimal,
    y: Decimal,
    z: Decimal,
    dt: Decimal,
    sigma: Decimal,
    rho: Decimal,
    beta: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    k1x, k1y, k1z = lorenz_derivatives(x, y, z, sigma, rho, beta)

    x2 = x + dt * k1x / Decimal("2")
    y2 = y + dt * k1y / Decimal("2")
    z2 = z + dt * k1z / Decimal("2")
    k2x, k2y, k2z = lorenz_derivatives(x2, y2, z2, sigma, rho, beta)

    x3 = x + dt * k2x / Decimal("2")
    y3 = y + dt * k2y / Decimal("2")
    z3 = z + dt * k2z / Decimal("2")
    k3x, k3y, k3z = lorenz_derivatives(x3, y3, z3, sigma, rho, beta)

    x4 = x + dt * k3x
    y4 = y + dt * k3y
    z4 = z + dt * k3z
    k4x, k4y, k4z = lorenz_derivatives(x4, y4, z4, sigma, rho, beta)

    x_next = x + dt * (k1x + Decimal("2") * k2x + Decimal("2") * k3x + k4x) / Decimal("6")
    y_next = y + dt * (k1y + Decimal("2") * k2y + Decimal("2") * k3y + k4y) / Decimal("6")
    z_next = z + dt * (k1z + Decimal("2") * k2z + Decimal("2") * k3z + k4z) / Decimal("6")
    return x_next, y_next, z_next


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


def minmax_scale(values: list[Decimal]) -> list[Decimal]:
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [Decimal("0.5") for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


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


def joint_radius(x: Decimal, y: Decimal, z: Decimal) -> float:
    return math.sqrt(float(x * x + y * y + z * z))


def build_relative_deltas(values: list[float]) -> list[float]:
    out = [0.0]
    for prev, curr in zip(values[:-1], values[1:]):
        if prev == 0.0:
            out.append(0.0 if curr == 0.0 else 1.0)
        else:
            out.append((curr - prev) / abs(prev))
    return out


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


def generate_full_trajectory(noisy: bool, rng: random.Random) -> list[dict[str, float]]:
    x = X0
    y = Y0
    z = Z0
    rows: list[dict[str, float]] = []

    for step in range(TOTAL_STEPS):
        rho = RHO_BEFORE if step < SWITCH_STEP else RHO_AFTER
        x, y, z = rk4_step(x, y, z, DT, SIGMA, rho, BETA)

        x_obs = x
        y_obs = y
        z_obs = z

        if noisy:
            x_obs = x + Decimal(str(rng.gauss(0.0, NOISE_STD)))
            y_obs = y + Decimal(str(rng.gauss(0.0, NOISE_STD)))
            z_obs = z + Decimal(str(rng.gauss(0.0, NOISE_STD)))

        rows.append(
            {
                "step": float(step),
                "rho": float(rho),
                "x": x_obs,
                "y": y_obs,
                "z": z_obs,
                "radius": joint_radius(x_obs, y_obs, z_obs),
            }
        )

    return rows[BURN_IN:]


def attach_window_scores(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    xs = [row["x"] for row in rows]
    ys = [row["y"] for row in rows]
    zs = [row["z"] for row in rows]
    rs = [Decimal(str(row["radius"])) for row in rows]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)
    zs_scaled = minmax_scale(zs)
    rs_scaled = minmax_scale(rs)

    component_digit_series = []
    component_rep_series = []
    radius_digit_series = []
    radius_rep_series = []

    for xs_n, ys_n, zs_n, rs_n in zip(xs_scaled, ys_scaled, zs_scaled, rs_scaled):
        sig_x = component_signature(xs_n)
        sig_y = component_signature(ys_n)
        sig_z = component_signature(zs_n)
        sig_r = component_signature(rs_n)

        component_digit_series.append(mean([sig_x["digit_sum_span"], sig_y["digit_sum_span"], sig_z["digit_sum_span"]]))
        component_rep_series.append(mean([sig_x["repetition_span"], sig_y["repetition_span"], sig_z["repetition_span"]]))
        radius_digit_series.append(sig_r["digit_sum_span"])
        radius_rep_series.append(sig_r["repetition_span"])

    rel_component_digit = build_relative_deltas(component_digit_series)
    rel_component_rep = build_relative_deltas(component_rep_series)
    rel_radius_digit = build_relative_deltas(radius_digit_series)
    rel_radius_rep = build_relative_deltas(radius_rep_series)

    event_raw = []
    order_raw = []

    for i in range(len(rows)):
        start = max(0, i - WINDOW + 1)

        window_component_digit = component_digit_series[start : i + 1]
        window_component_rep = component_rep_series[start : i + 1]
        window_radius_digit = radius_digit_series[start : i + 1]
        window_radius_rep = radius_rep_series[start : i + 1]
        window_rel_component_digit = rel_component_digit[start : i + 1]
        window_rel_component_rep = rel_component_rep[start : i + 1]
        window_rel_radius_digit = rel_radius_digit[start : i + 1]
        window_rel_radius_rep = rel_radius_rep[start : i + 1]

        order_val = (
            0.25 * (1.0 / (1.0 + std(window_component_digit)))
            + 0.15 * (1.0 / (1.0 + std(window_component_rep)))
            + 0.35 * (1.0 / (1.0 + std(window_radius_digit)))
            + 0.25 * (1.0 / (1.0 + std(window_radius_rep)))
        )

        event_val = (
            0.20 * mean([abs(v) for v in window_rel_component_digit])
            + 0.10 * mean([abs(v) for v in window_rel_component_rep])
            + 0.40 * mean([abs(v) for v in window_rel_radius_digit])
            + 0.30 * mean([abs(v) for v in window_rel_radius_rep])
        )

        order_raw.append(order_val)
        event_raw.append(event_val)

    order_lo, order_hi = minmax_params(order_raw)
    event_lo, event_hi = minmax_params(event_raw)

    out = []
    for row, order_val, event_val in zip(rows, order_raw, event_raw):
        order_score = minmax_norm(order_val, order_lo, order_hi)
        event_score = minmax_norm(event_val, event_lo, event_hi)
        alert = int(event_score >= ALERT_THRESHOLD)

        out.append(
            {
                "step": int(row["step"]),
                "rho": row["rho"],
                "x": float(row["x"]),
                "y": float(row["y"]),
                "z": float(row["z"]),
                "radius": row["radius"],
                "order_score_v1": order_score,
                "event_score_v1": event_score,
                "alert_flag": alert,
            }
        )

    return out


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    clean_rows = attach_window_scores(generate_full_trajectory(noisy=False, rng=random.Random(RANDOM_SEED)))
    noisy_rows = attach_window_scores(generate_full_trajectory(noisy=True, rng=random.Random(RANDOM_SEED)))

    fieldnames = [
        "condition",
        "step",
        "rho",
        "x",
        "y",
        "z",
        "radius",
        "order_score_v1",
        "event_score_v1",
        "alert_flag",
    ]

    def first_alert(rows: list[dict[str, float]]) -> int | None:
        for row in rows:
            if row["step"] >= SWITCH_STEP and row["alert_flag"] == 1:
                return row["step"]
        return None

    clean_alert = first_alert(clean_rows)
    noisy_alert = first_alert(noisy_rows)

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE LORENZ REALTIME ALERT NOISE V1")
        print("-" * 92)

        for condition, rows in [("clean", clean_rows), ("noisy", noisy_rows)]:
            for row in rows:
                writer.writerow({"condition": condition, **row})

            print(condition)
            for probe in [SWITCH_STEP - 5, SWITCH_STEP - 1, SWITCH_STEP, SWITCH_STEP + 1, SWITCH_STEP + 5, SWITCH_STEP + 20, SWITCH_STEP + 50]:
                match = next((r for r in rows if r["step"] == probe), None)
                if match is not None:
                    print(
                        f"step={match['step']} | "
                        f"rho={match['rho']:.1f} | "
                        f"order={match['order_score_v1']:.6f} | "
                        f"event={match['event_score_v1']:.6f} | "
                        f"alert={match['alert_flag']}"
                    )
            print("-" * 92)

        print(f"clean_first_alert_after_switch={clean_alert}")
        if clean_alert is not None:
            clean_delay = clean_alert - SWITCH_STEP
            print(f"clean_alert_delay_steps={clean_delay}")
            print(f"clean_alert_delay_time={clean_delay * float(DT):.6f}")

        print(f"noisy_first_alert_after_switch={noisy_alert}")
        if noisy_alert is not None:
            noisy_delay = noisy_alert - SWITCH_STEP
            print(f"noisy_alert_delay_steps={noisy_delay}")
            print(f"noisy_alert_delay_time={noisy_delay * float(DT):.6f}")

        print("-" * 92)
        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/lorenz_realtime_alert_noise_v1.csv"))