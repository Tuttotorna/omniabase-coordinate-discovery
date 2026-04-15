from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

# Standard Lorenz parameters
SIGMA = Decimal("10.0")
RHO = Decimal("28.0")
BETA = Decimal("2.6666666666666667")  # 8/3

# Initial condition
X0 = Decimal("0.1")
Y0 = Decimal("0.0")
Z0 = Decimal("0.0")

# Integration settings
DT = Decimal("0.01")
TOTAL_STEPS = 12000
BURN_IN = 2000

BASES = list(range(2, 17))
DECIMAL_DIGITS = 12


def lorenz_derivatives(x: Decimal, y: Decimal, z: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    dx = SIGMA * (y - x)
    dy = x * (RHO - z) - y
    dz = x * y - BETA * z
    return dx, dy, dz


def rk4_step(x: Decimal, y: Decimal, z: Decimal, dt: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    k1x, k1y, k1z = lorenz_derivatives(x, y, z)

    x2 = x + dt * k1x / Decimal("2")
    y2 = y + dt * k1y / Decimal("2")
    z2 = z + dt * k1z / Decimal("2")
    k2x, k2y, k2z = lorenz_derivatives(x2, y2, z2)

    x3 = x + dt * k2x / Decimal("2")
    y3 = y + dt * k2y / Decimal("2")
    z3 = z + dt * k2z / Decimal("2")
    k3x, k3y, k3z = lorenz_derivatives(x3, y3, z3)

    x4 = x + dt * k3x
    y4 = y + dt * k3y
    z4 = z + dt * k3z
    k4x, k4y, k4z = lorenz_derivatives(x4, y4, z4)

    x_next = x + dt * (k1x + Decimal("2") * k2x + Decimal("2") * k3x + k4x) / Decimal("6")
    y_next = y + dt * (k1y + Decimal("2") * k2y + Decimal("2") * k3y + k4y) / Decimal("6")
    z_next = z + dt * (k1z + Decimal("2") * k2z + Decimal("2") * k3z + k4z) / Decimal("6")
    return x_next, y_next, z_next


def generate_trajectory() -> list[tuple[Decimal, Decimal, Decimal]]:
    x = X0
    y = Y0
    z = Z0
    out: list[tuple[Decimal, Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        x, y, z = rk4_step(x, y, z, DT)
        out.append((x, y, z))

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


def joint_radius(x: Decimal, y: Decimal, z: Decimal) -> float:
    return math.sqrt(float(x * x + y * y + z * z))


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    trajectory = generate_trajectory()

    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    zs = [p[2] for p in trajectory]
    radii = [joint_radius(x, y, z) for x, y, z in trajectory]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)
    zs_scaled = minmax_scale(zs)
    radii_scaled = minmax_scale([Decimal(str(r)) for r in radii])

    fieldnames = [
        "step",
        "x",
        "y",
        "z",
        "x_scaled",
        "y_scaled",
        "z_scaled",
        "radius",
        "radius_scaled",
        "x_digit_sum_span",
        "x_repetition_span",
        "y_digit_sum_span",
        "y_repetition_span",
        "z_digit_sum_span",
        "z_repetition_span",
        "radius_digit_sum_span",
        "radius_repetition_span",
        "xyz_component_digit_sum_mean",
        "xyz_component_repetition_mean",
    ]

    x_digit_spans = []
    y_digit_spans = []
    z_digit_spans = []
    r_digit_spans = []

    x_rep_spans = []
    y_rep_spans = []
    z_rep_spans = []
    r_rep_spans = []

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, (x, y, z, xs_n, ys_n, zs_n, r_raw, r_n) in enumerate(
            zip(xs, ys, zs, xs_scaled, ys_scaled, zs_scaled, radii, radii_scaled)
        ):
            sig_x = component_signature(xs_n)
            sig_y = component_signature(ys_n)
            sig_z = component_signature(zs_n)
            sig_r = component_signature(r_n)

            x_digit_spans.append(sig_x["digit_sum_span"])
            y_digit_spans.append(sig_y["digit_sum_span"])
            z_digit_spans.append(sig_z["digit_sum_span"])
            r_digit_spans.append(sig_r["digit_sum_span"])

            x_rep_spans.append(sig_x["repetition_span"])
            y_rep_spans.append(sig_y["repetition_span"])
            z_rep_spans.append(sig_z["repetition_span"])
            r_rep_spans.append(sig_r["repetition_span"])

            writer.writerow(
                {
                    "step": idx,
                    "x": f"{x:.18f}",
                    "y": f"{y:.18f}",
                    "z": f"{z:.18f}",
                    "x_scaled": f"{xs_n:.18f}",
                    "y_scaled": f"{ys_n:.18f}",
                    "z_scaled": f"{zs_n:.18f}",
                    "radius": f"{r_raw:.18f}",
                    "radius_scaled": f"{r_n:.18f}",
                    "x_digit_sum_span": sig_x["digit_sum_span"],
                    "x_repetition_span": sig_x["repetition_span"],
                    "y_digit_sum_span": sig_y["digit_sum_span"],
                    "y_repetition_span": sig_y["repetition_span"],
                    "z_digit_sum_span": sig_z["digit_sum_span"],
                    "z_repetition_span": sig_z["repetition_span"],
                    "radius_digit_sum_span": sig_r["digit_sum_span"],
                    "radius_repetition_span": sig_r["repetition_span"],
                    "xyz_component_digit_sum_mean": mean(
                        [sig_x["digit_sum_span"], sig_y["digit_sum_span"], sig_z["digit_sum_span"]]
                    ),
                    "xyz_component_repetition_mean": mean(
                        [sig_x["repetition_span"], sig_y["repetition_span"], sig_z["repetition_span"]]
                    ),
                }
            )

    print("OMNIABASE LORENZ MULTIBASE V0")
    print("-" * 76)
    print(f"steps_written={len(xs)}")
    print(f"x_digit_sum_span_std={std(x_digit_spans):.6f}")
    print(f"y_digit_sum_span_std={std(y_digit_spans):.6f}")
    print(f"z_digit_sum_span_std={std(z_digit_spans):.6f}")
    print(f"radius_digit_sum_span_std={std(r_digit_spans):.6f}")
    print(f"x_repetition_span_std={std(x_rep_spans):.6f}")
    print(f"y_repetition_span_std={std(y_rep_spans):.6f}")
    print(f"z_repetition_span_std={std(z_rep_spans):.6f}")
    print(f"radius_repetition_span_std={std(r_rep_spans):.6f}")
    print("-" * 76)
    print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/lorenz_multibase_v0.csv"))