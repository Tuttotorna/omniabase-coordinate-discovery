from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

# Fixed Lorenz parameters
SIGMA = Decimal("10.0")
BETA = Decimal("2.6666666666666667")  # 8/3

# Scan parameter
RHO_START = Decimal("10.0")
RHO_END = Decimal("28.0")
RHO_STEP = Decimal("1.0")

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


def generate_trajectory(rho: Decimal) -> list[tuple[Decimal, Decimal, Decimal]]:
    x = X0
    y = Y0
    z = Z0
    out: list[tuple[Decimal, Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        x, y, z = rk4_step(x, y, z, DT, SIGMA, rho, BETA)
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


def summarize_for_rho(rho: Decimal) -> dict[str, float]:
    trajectory = generate_trajectory(rho)

    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    zs = [p[2] for p in trajectory]
    radii = [joint_radius(x, y, z) for x, y, z in trajectory]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)
    zs_scaled = minmax_scale(zs)
    radii_scaled = minmax_scale([Decimal(str(r)) for r in radii])

    x_digit_spans = []
    x_rep_spans = []
    y_digit_spans = []
    y_rep_spans = []
    z_digit_spans = []
    z_rep_spans = []
    r_digit_spans = []
    r_rep_spans = []

    for xs_n, ys_n, zs_n, rs_n in zip(xs_scaled, ys_scaled, zs_scaled, radii_scaled):
        sig_x = component_signature(xs_n)
        sig_y = component_signature(ys_n)
        sig_z = component_signature(zs_n)
        sig_r = component_signature(rs_n)

        x_digit_spans.append(sig_x["digit_sum_span"])
        x_rep_spans.append(sig_x["repetition_span"])
        y_digit_spans.append(sig_y["digit_sum_span"])
        y_rep_spans.append(sig_y["repetition_span"])
        z_digit_spans.append(sig_z["digit_sum_span"])
        z_rep_spans.append(sig_z["repetition_span"])
        r_digit_spans.append(sig_r["digit_sum_span"])
        r_rep_spans.append(sig_r["repetition_span"])

    component_digit_mean = mean([std(x_digit_spans), std(y_digit_spans), std(z_digit_spans)])
    component_rep_mean = mean([std(x_rep_spans), std(y_rep_spans), std(z_rep_spans)])
    radius_digit_std = std(r_digit_spans)
    radius_rep_std = std(r_rep_spans)

    unique_x = len({round(float(x), 10) for x in xs})
    unique_y = len({round(float(y), 10) for y in ys})
    unique_z = len({round(float(z), 10) for z in zs})
    unique_xyz = len(
        {
            (
                round(float(x), 6),
                round(float(y), 6),
                round(float(z), 6),
            )
            for x, y, z in trajectory
        }
    )

    return {
        "rho": float(rho),
        "unique_x": float(unique_x),
        "unique_y": float(unique_y),
        "unique_z": float(unique_z),
        "unique_xyz_triplets": float(unique_xyz),
        "x_std": std([float(x) for x in xs]),
        "y_std": std([float(y) for y in ys]),
        "z_std": std([float(z) for z in zs]),
        "component_digit_mean": component_digit_mean,
        "component_rep_mean": component_rep_mean,
        "radius_digit_std": radius_digit_std,
        "radius_rep_std": radius_rep_std,
    }


def generate_rho_values() -> list[Decimal]:
    values = []
    rho = RHO_START
    while rho <= RHO_END:
        values.append(rho)
        rho += RHO_STEP
    return values


def attach_scores(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    unique_vals = [row["unique_xyz_triplets"] for row in rows]
    component_digit_vals = [row["component_digit_mean"] for row in rows]
    component_rep_vals = [row["component_rep_mean"] for row in rows]
    radius_digit_vals = [row["radius_digit_std"] for row in rows]
    radius_rep_vals = [row["radius_rep_std"] for row in rows]

    rel_component_digit = build_relative_deltas(component_digit_vals)
    rel_component_rep = build_relative_deltas(component_rep_vals)
    rel_radius_digit = build_relative_deltas(radius_digit_vals)
    rel_radius_rep = build_relative_deltas(radius_rep_vals)

    u_lo, u_hi = minmax_params(unique_vals)
    cd_lo, cd_hi = minmax_params(component_digit_vals)
    cr_lo, cr_hi = minmax_params(component_rep_vals)
    rd_lo, rd_hi = minmax_params(radius_digit_vals)
    rr_lo, rr_hi = minmax_params(radius_rep_vals)
    rcd_lo, rcd_hi = minmax_params(rel_component_digit)
    rcr_lo, rcr_hi = minmax_params(rel_component_rep)
    rrd_lo, rrd_hi = minmax_params(rel_radius_digit)
    rrr_lo, rrr_hi = minmax_params(rel_radius_rep)

    out = []
    for row, d_cd, d_cr, d_rd, d_rr in zip(
        rows, rel_component_digit, rel_component_rep, rel_radius_digit, rel_radius_rep
    ):
        norm_unique = minmax_norm(row["unique_xyz_triplets"], u_lo, u_hi)
        norm_component_digit = minmax_norm(row["component_digit_mean"], cd_lo, cd_hi)
        norm_component_rep = minmax_norm(row["component_rep_mean"], cr_lo, cr_hi)
        norm_radius_digit = minmax_norm(row["radius_digit_std"], rd_lo, rd_hi)
        norm_radius_rep = minmax_norm(row["radius_rep_std"], rr_lo, rr_hi)
        norm_rel_component_digit = minmax_norm(d_cd, rcd_lo, rcd_hi)
        norm_rel_component_rep = minmax_norm(d_cr, rcr_lo, rcr_hi)
        norm_rel_radius_digit = minmax_norm(d_rd, rrd_lo, rrd_hi)
        norm_rel_radius_rep = minmax_norm(d_rr, rrr_lo, rrr_hi)

        order_score = (
            0.25 * (1.0 - norm_unique)
            + 0.25 * (1.0 - norm_component_digit)
            + 0.15 * (1.0 - norm_component_rep)
            + 0.20 * (1.0 - norm_radius_digit)
            + 0.15 * (1.0 - norm_radius_rep)
        )

        event_score = (
            0.20 * norm_radius_digit
            + 0.15 * norm_radius_rep
            + 0.25 * norm_rel_radius_digit
            + 0.20 * norm_rel_radius_rep
            + 0.10 * norm_rel_component_digit
            + 0.10 * norm_rel_component_rep
        )

        out.append(
            {
                **row,
                "rel_component_digit_mean": d_cd,
                "rel_component_rep_mean": d_cr,
                "rel_radius_digit_std": d_rd,
                "rel_radius_rep_std": d_rr,
                "order_score_v1": order_score,
                "event_score_v1": event_score,
            }
        )

    return out


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = [summarize_for_rho(rho) for rho in generate_rho_values()]
    rows = attach_scores(rows)

    fieldnames = [
        "rho",
        "unique_x",
        "unique_y",
        "unique_z",
        "unique_xyz_triplets",
        "x_std",
        "y_std",
        "z_std",
        "component_digit_mean",
        "component_rep_mean",
        "radius_digit_std",
        "radius_rep_std",
        "rel_component_digit_mean",
        "rel_component_rep_mean",
        "rel_radius_digit_std",
        "rel_radius_rep_std",
        "order_score_v1",
        "event_score_v1",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE LORENZ RHO SCAN V1")
        print("-" * 88)

        for row in rows:
            writer.writerow(
                {
                    "rho": f"{row['rho']:.1f}",
                    "unique_x": int(row["unique_x"]),
                    "unique_y": int(row["unique_y"]),
                    "unique_z": int(row["unique_z"]),
                    "unique_xyz_triplets": int(row["unique_xyz_triplets"]),
                    "x_std": row["x_std"],
                    "y_std": row["y_std"],
                    "z_std": row["z_std"],
                    "component_digit_mean": row["component_digit_mean"],
                    "component_rep_mean": row["component_rep_mean"],
                    "radius_digit_std": row["radius_digit_std"],
                    "radius_rep_std": row["radius_rep_std"],
                    "rel_component_digit_mean": row["rel_component_digit_mean"],
                    "rel_component_rep_mean": row["rel_component_rep_mean"],
                    "rel_radius_digit_std": row["rel_radius_digit_std"],
                    "rel_radius_rep_std": row["rel_radius_rep_std"],
                    "order_score_v1": row["order_score_v1"],
                    "event_score_v1": row["event_score_v1"],
                }
            )

            print(
                f"rho={row['rho']:.1f} | "
                f"triplets={int(row['unique_xyz_triplets'])} | "
                f"order={row['order_score_v1']:.6f} | "
                f"event={row['event_score_v1']:.6f}"
            )

        print("-" * 88)
        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/lorenz_rho_scan_v1.csv"))