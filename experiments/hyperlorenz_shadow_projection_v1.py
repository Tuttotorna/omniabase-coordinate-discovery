from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

# Full 4D hyper-Lorenz-like system
A = Decimal("10.0")
B = Decimal("2.6666666666666667")
C = Decimal("28.0")
R = Decimal("1.0")

X0 = Decimal("0.1")
Y0 = Decimal("0.0")
Z0 = Decimal("0.0")
W0 = Decimal("0.1")

DT = Decimal("0.01")
TOTAL_STEPS = 16000
BURN_IN = 3000

BASES = list(range(2, 17))
DECIMAL_DIGITS = 12


def hyperlorenz_derivatives(
    x: Decimal,
    y: Decimal,
    z: Decimal,
    w: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    dx = A * (y - x) + w
    dy = C * x - y - x * z
    dz = x * y - B * z
    dw = -(y * z) + R * w
    return dx, dy, dz, dw


def rk4_step(
    x: Decimal,
    y: Decimal,
    z: Decimal,
    w: Decimal,
    dt: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    k1x, k1y, k1z, k1w = hyperlorenz_derivatives(x, y, z, w)

    x2 = x + dt * k1x / Decimal("2")
    y2 = y + dt * k1y / Decimal("2")
    z2 = z + dt * k1z / Decimal("2")
    w2 = w + dt * k1w / Decimal("2")
    k2x, k2y, k2z, k2w = hyperlorenz_derivatives(x2, y2, z2, w2)

    x3 = x + dt * k2x / Decimal("2")
    y3 = y + dt * k2y / Decimal("2")
    z3 = z + dt * k2z / Decimal("2")
    w3 = w + dt * k2w / Decimal("2")
    k3x, k3y, k3z, k3w = hyperlorenz_derivatives(x3, y3, z3, w3)

    x4 = x + dt * k3x
    y4 = y + dt * k3y
    z4 = z + dt * k3z
    w4 = w + dt * k3w
    k4x, k4y, k4z, k4w = hyperlorenz_derivatives(x4, y4, z4, w4)

    x_next = x + dt * (k1x + Decimal("2") * k2x + Decimal("2") * k3x + k4x) / Decimal("6")
    y_next = y + dt * (k1y + Decimal("2") * k2y + Decimal("2") * k3y + k4y) / Decimal("6")
    z_next = z + dt * (k1z + Decimal("2") * k2z + Decimal("2") * k3z + k4z) / Decimal("6")
    w_next = w + dt * (k1w + Decimal("2") * k2w + Decimal("2") * k3w + k4w) / Decimal("6")
    return x_next, y_next, z_next, w_next


def generate_full_trajectory() -> list[tuple[Decimal, Decimal, Decimal, Decimal]]:
    x, y, z, w = X0, Y0, Z0, W0
    out: list[tuple[Decimal, Decimal, Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        x, y, z, w = rk4_step(x, y, z, w, DT)
        out.append((x, y, z, w))

    return out[BURN_IN:]


def generate_shadow_trajectory() -> list[tuple[Decimal, Decimal]]:
    """
    Naive 2D shadow model that ignores hidden dimensions.
    This is intentionally simpler than the true system.
    """
    x, y = X0, Y0
    out: list[tuple[Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        dx = A * (y - x)
        dy = C * x - y
        x = x + DT * dx
        y = y + DT * dy
        out.append((x, y))

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


def summarize_xy_projection_from_4d(full_traj: list[tuple[Decimal, Decimal, Decimal, Decimal]]) -> dict[str, float]:
    xs = [row[0] for row in full_traj]
    ys = [row[1] for row in full_traj]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)

    x_digit_spans = []
    y_digit_spans = []
    x_rep_spans = []
    y_rep_spans = []

    xy_radius_raw = [math.sqrt(float(x * x + y * y)) for x, y in zip(xs, ys)]
    xy_radius_scaled = minmax_scale([Decimal(str(v)) for v in xy_radius_raw])
    xy_radius_digit_spans = []
    xy_radius_rep_spans = []

    for xs_n, ys_n, rs_n in zip(xs_scaled, ys_scaled, xy_radius_scaled):
        sig_x = component_signature(xs_n)
        sig_y = component_signature(ys_n)
        sig_r = component_signature(rs_n)

        x_digit_spans.append(sig_x["digit_sum_span"])
        y_digit_spans.append(sig_y["digit_sum_span"])
        x_rep_spans.append(sig_x["repetition_span"])
        y_rep_spans.append(sig_y["repetition_span"])
        xy_radius_digit_spans.append(sig_r["digit_sum_span"])
        xy_radius_rep_spans.append(sig_r["repetition_span"])

    return {
        "model": "projection_from_4d",
        "unique_xy_pairs": float(len({(round(float(x), 6), round(float(y), 6)) for x, y in zip(xs, ys)})),
        "x_std": std([float(x) for x in xs]),
        "y_std": std([float(y) for y in ys]),
        "xy_component_digit_mean": mean([std(x_digit_spans), std(y_digit_spans)]),
        "xy_component_rep_mean": mean([std(x_rep_spans), std(y_rep_spans)]),
        "xy_radius_digit_std": std(xy_radius_digit_spans),
        "xy_radius_rep_std": std(xy_radius_rep_spans),
    }


def summarize_naive_xy_shadow(shadow_traj: list[tuple[Decimal, Decimal]]) -> dict[str, float]:
    xs = [row[0] for row in shadow_traj]
    ys = [row[1] for row in shadow_traj]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)

    x_digit_spans = []
    y_digit_spans = []
    x_rep_spans = []
    y_rep_spans = []

    xy_radius_raw = [math.sqrt(float(x * x + y * y)) for x, y in zip(xs, ys)]
    xy_radius_scaled = minmax_scale([Decimal(str(v)) for v in xy_radius_raw])
    xy_radius_digit_spans = []
    xy_radius_rep_spans = []

    for xs_n, ys_n, rs_n in zip(xs_scaled, ys_scaled, xy_radius_scaled):
        sig_x = component_signature(xs_n)
        sig_y = component_signature(ys_n)
        sig_r = component_signature(rs_n)

        x_digit_spans.append(sig_x["digit_sum_span"])
        y_digit_spans.append(sig_y["digit_sum_span"])
        x_rep_spans.append(sig_x["repetition_span"])
        y_rep_spans.append(sig_y["repetition_span"])
        xy_radius_digit_spans.append(sig_r["digit_sum_span"])
        xy_radius_rep_spans.append(sig_r["repetition_span"])

    return {
        "model": "naive_xy_shadow",
        "unique_xy_pairs": float(len({(round(float(x), 6), round(float(y), 6)) for x, y in zip(xs, ys)})),
        "x_std": std([float(x) for x in xs]),
        "y_std": std([float(y) for y in ys]),
        "xy_component_digit_mean": mean([std(x_digit_spans), std(y_digit_spans)]),
        "xy_component_rep_mean": mean([std(x_rep_spans), std(y_rep_spans)]),
        "xy_radius_digit_std": std(xy_radius_digit_spans),
        "xy_radius_rep_std": std(xy_radius_rep_spans),
    }


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    full_traj = generate_full_trajectory()
    shadow_traj = generate_shadow_trajectory()

    row_proj = summarize_xy_projection_from_4d(full_traj)
    row_shadow = summarize_naive_xy_shadow(shadow_traj)

    fieldnames = [
        "model",
        "unique_xy_pairs",
        "x_std",
        "y_std",
        "xy_component_digit_mean",
        "xy_component_rep_mean",
        "xy_radius_digit_std",
        "xy_radius_rep_std",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row_proj)
        writer.writerow(row_shadow)

    print("OMNIABASE HYPERLORENZ SHADOW PROJECTION V1")
    print("-" * 84)
    print(
        f"projection_from_4d | pairs={int(row_proj['unique_xy_pairs'])} | "
        f"xy_digit={row_proj['xy_component_digit_mean']:.6f} | "
        f"xy_radius={row_proj['xy_radius_digit_std']:.6f}"
    )
    print(
        f"naive_xy_shadow    | pairs={int(row_shadow['unique_xy_pairs'])} | "
        f"xy_digit={row_shadow['xy_component_digit_mean']:.6f} | "
        f"xy_radius={row_shadow['xy_radius_digit_std']:.6f}"
    )
    print("-" * 84)
    print(f"delta_xy_component_digit_mean={row_proj['xy_component_digit_mean'] - row_shadow['xy_component_digit_mean']:.6f}")
    print(f"delta_xy_radius_digit_std={row_proj['xy_radius_digit_std'] - row_shadow['xy_radius_digit_std']:.6f}")
    print(f"delta_xy_component_rep_mean={row_proj['xy_component_rep_mean'] - row_shadow['xy_component_rep_mean']:.6f}")
    print(f"delta_xy_radius_rep_std={row_proj['xy_radius_rep_std'] - row_shadow['xy_radius_rep_std']:.6f}")
    print("-" * 84)
    print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/hyperlorenz_shadow_projection_v1.csv"))