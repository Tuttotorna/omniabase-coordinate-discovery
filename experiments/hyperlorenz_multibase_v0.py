from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

# 4D Lorenz-like hyperchaotic system (continuous-time)
# A common hyperchaotic extension is obtained by adding a fourth state w
# coupled into x/z dynamics and giving w its own unstable channel.
#
# dx/dt = a (y - x) + w
# dy/dt = c x - y - x z
# dz/dt = x y - b z
# dw/dt = -y z + r w
#
# This is not claimed here as a canonical universal hyperchaotic law.
# It is used as a controlled 4D continuous benchmark for multibase scaling.

A = Decimal("10.0")
B = Decimal("2.6666666666666667")   # 8/3
C = Decimal("28.0")
R = Decimal("1.0")

# Initial condition
X0 = Decimal("0.1")
Y0 = Decimal("0.0")
Z0 = Decimal("0.0")
W0 = Decimal("0.1")

# Integration settings
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


def generate_trajectory() -> list[tuple[Decimal, Decimal, Decimal, Decimal]]:
    x = X0
    y = Y0
    z = Z0
    w = W0
    out: list[tuple[Decimal, Decimal, Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        x, y, z, w = rk4_step(x, y, z, w, DT)
        out.append((x, y, z, w))

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


def joint_radius4(x: Decimal, y: Decimal, z: Decimal, w: Decimal) -> float:
    return math.sqrt(float(x * x + y * y + z * z + w * w))


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    trajectory = generate_trajectory()

    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    zs = [p[2] for p in trajectory]
    ws = [p[3] for p in trajectory]
    radii = [joint_radius4(x, y, z, w) for x, y, z, w in trajectory]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)
    zs_scaled = minmax_scale(zs)
    ws_scaled = minmax_scale(ws)
    radii_scaled = minmax_scale([Decimal(str(r)) for r in radii])

    fieldnames = [
        "step",
        "x",
        "y",
        "z",
        "w",
        "x_scaled",
        "y_scaled",
        "z_scaled",
        "w_scaled",
        "radius4",
        "radius4_scaled",
        "x_digit_sum_span",
        "y_digit_sum_span",
        "z_digit_sum_span",
        "w_digit_sum_span",
        "radius4_digit_sum_span",
        "x_repetition_span",
        "y_repetition_span",
        "z_repetition_span",
        "w_repetition_span",
        "radius4_repetition_span",
        "xyzw_component_digit_sum_mean",
        "xyzw_component_repetition_mean",
    ]

    x_digit_spans = []
    y_digit_spans = []
    z_digit_spans = []
    w_digit_spans = []
    r_digit_spans = []

    x_rep_spans = []
    y_rep_spans = []
    z_rep_spans = []
    w_rep_spans = []
    r_rep_spans = []

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, (x, y, z, w, xs_n, ys_n, zs_n, ws_n, r_raw, r_n) in enumerate(
            zip(xs, ys, zs, ws, xs_scaled, ys_scaled, zs_scaled, ws_scaled, radii, radii_scaled)
        ):
            sig_x = component_signature(xs_n)
            sig_y = component_signature(ys_n)
            sig_z = component_signature(zs_n)
            sig_w = component_signature(ws_n)
            sig_r = component_signature(r_n)

            x_digit_spans.append(sig_x["digit_sum_span"])
            y_digit_spans.append(sig_y["digit_sum_span"])
            z_digit_spans.append(sig_z["digit_sum_span"])
            w_digit_spans.append(sig_w["digit_sum_span"])
            r_digit_spans.append(sig_r["digit_sum_span"])

            x_rep_spans.append(sig_x["repetition_span"])
            y_rep_spans.append(sig_y["repetition_span"])
            z_rep_spans.append(sig_z["repetition_span"])
            w_rep_spans.append(sig_w["repetition_span"])
            r_rep_spans.append(sig_r["repetition_span"])

            writer.writerow(
                {
                    "step": idx,
                    "x": f"{x:.18f}",
                    "y": f"{y:.18f}",
                    "z": f"{z:.18f}",
                    "w": f"{w:.18f}",
                    "x_scaled": f"{xs_n:.18f}",
                    "y_scaled": f"{ys_n:.18f}",
                    "z_scaled": f"{zs_n:.18f}",
                    "w_scaled": f"{ws_n:.18f}",
                    "radius4": f"{r_raw:.18f}",
                    "radius4_scaled": f"{r_n:.18f}",
                    "x_digit_sum_span": sig_x["digit_sum_span"],
                    "y_digit_sum_span": sig_y["digit_sum_span"],
                    "z_digit_sum_span": sig_z["digit_sum_span"],
                    "w_digit_sum_span": sig_w["digit_sum_span"],
                    "radius4_digit_sum_span": sig_r["digit_sum_span"],
                    "x_repetition_span": sig_x["repetition_span"],
                    "y_repetition_span": sig_y["repetition_span"],
                    "z_repetition_span": sig_z["repetition_span"],
                    "w_repetition_span": sig_w["repetition_span"],
                    "radius4_repetition_span": sig_r["repetition_span"],
                    "xyzw_component_digit_sum_mean": mean(
                        [
                            sig_x["digit_sum_span"],
                            sig_y["digit_sum_span"],
                            sig_z["digit_sum_span"],
                            sig_w["digit_sum_span"],
                        ]
                    ),
                    "xyzw_component_repetition_mean": mean(
                        [
                            sig_x["repetition_span"],
                            sig_y["repetition_span"],
                            sig_z["repetition_span"],
                            sig_w["repetition_span"],
                        ]
                    ),
                }
            )

    print("OMNIABASE HYPERLORENZ MULTIBASE V0")
    print("-" * 80)
    print(f"steps_written={len(xs)}")
    print(f"x_digit_sum_span_std={std(x_digit_spans):.6f}")
    print(f"y_digit_sum_span_std={std(y_digit_spans):.6f}")
    print(f"z_digit_sum_span_std={std(z_digit_spans):.6f}")
    print(f"w_digit_sum_span_std={std(w_digit_spans):.6f}")
    print(f"radius4_digit_sum_span_std={std(r_digit_spans):.6f}")
    print(f"x_repetition_span_std={std(x_rep_spans):.6f}")
    print(f"y_repetition_span_std={std(y_rep_spans):.6f}")
    print(f"z_repetition_span_std={std(z_rep_spans):.6f}")
    print(f"w_repetition_span_std={std(w_rep_spans):.6f}")
    print(f"radius4_repetition_span_std={std(r_rep_spans):.6f}")
    print("-" * 80)
    print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/hyperlorenz_multibase_v0.csv"))