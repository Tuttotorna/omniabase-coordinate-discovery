from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math
import random

getcontext().prec = 50

SIGMA = Decimal("10.0")
RHO = Decimal("28.0")
BETA = Decimal("2.6666666666666667")  # 8/3

# Drive-response coupling on x
COUPLING_VALUES = [
    Decimal("0.00"),
    Decimal("1.00"),
    Decimal("3.00"),
    Decimal("5.00"),
    Decimal("8.00"),
]

# Drive initial state
X0_D = Decimal("0.1")
Y0_D = Decimal("0.0")
Z0_D = Decimal("0.0")

# Response initial state
X0_R = Decimal("5.0")
Y0_R = Decimal("5.0")
Z0_R = Decimal("5.0")

DT = Decimal("0.01")
TOTAL_STEPS = 14000
BURN_IN = 2000

BASES = list(range(2, 17))
DECIMAL_DIGITS = 12

# Sensor noise applied only to observed response state
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


def drive_response_derivatives(
    xd: Decimal,
    yd: Decimal,
    zd: Decimal,
    xr: Decimal,
    yr: Decimal,
    zr: Decimal,
    coupling: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    dxd, dyd, dzd = lorenz_derivatives(xd, yd, zd, SIGMA, RHO, BETA)

    dxr, dyr, dzr = lorenz_derivatives(xr, yr, zr, SIGMA, RHO, BETA)
    dxr = dxr + coupling * (xd - xr)

    return dxd, dyd, dzd, dxr, dyr, dzr


def rk4_coupled_step(
    xd: Decimal,
    yd: Decimal,
    zd: Decimal,
    xr: Decimal,
    yr: Decimal,
    zr: Decimal,
    coupling: Decimal,
    dt: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    k1 = drive_response_derivatives(xd, yd, zd, xr, yr, zr, coupling)

    s2 = [v + dt * kv / Decimal("2") for v, kv in zip([xd, yd, zd, xr, yr, zr], k1)]
    k2 = drive_response_derivatives(*s2, coupling)

    s3 = [v + dt * kv / Decimal("2") for v, kv in zip([xd, yd, zd, xr, yr, zr], k2)]
    k3 = drive_response_derivatives(*s3, coupling)

    s4 = [v + dt * kv for v, kv in zip([xd, yd, zd, xr, yr, zr], k3)]
    k4 = drive_response_derivatives(*s4, coupling)

    next_vals = []
    for v, a, b, c, d in zip([xd, yd, zd, xr, yr, zr], k1, k2, k3, k4):
        next_vals.append(v + dt * (a + Decimal("2") * b + Decimal("2") * c + d) / Decimal("6"))

    return tuple(next_vals)  # type: ignore[return-value]


def generate_trajectory(
    coupling: Decimal,
    noisy: bool,
    rng: random.Random,
) -> list[tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]]:
    xd, yd, zd = X0_D, Y0_D, Z0_D
    xr, yr, zr = X0_R, Y0_R, Z0_R

    out: list[tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        xd, yd, zd, xr, yr, zr = rk4_coupled_step(
            xd, yd, zd, xr, yr, zr, coupling, DT
        )

        xd_obs, yd_obs, zd_obs = xd, yd, zd
        xr_obs, yr_obs, zr_obs = xr, yr, zr

        if noisy:
            xr_obs = xr + Decimal(str(rng.gauss(0.0, NOISE_STD)))
            yr_obs = yr + Decimal(str(rng.gauss(0.0, NOISE_STD)))
            zr_obs = zr + Decimal(str(rng.gauss(0.0, NOISE_STD)))

        out.append((xd_obs, yd_obs, zd_obs, xr_obs, yr_obs, zr_obs))

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


def summarize_coupling(
    coupling: Decimal,
    noisy: bool,
    rng: random.Random,
) -> dict[str, float]:
    traj = generate_trajectory(coupling, noisy=noisy, rng=rng)

    xd = [row[0] for row in traj]
    yd = [row[1] for row in traj]
    zd = [row[2] for row in traj]
    xr = [row[3] for row in traj]
    yr = [row[4] for row in traj]
    zr = [row[5] for row in traj]

    err_x = [abs(float(a - b)) for a, b in zip(xd, xr)]
    err_y = [abs(float(a - b)) for a, b in zip(yd, yr)]
    err_z = [abs(float(a - b)) for a, b in zip(zd, zr)]
    err_mean = [(a + b + c) / 3.0 for a, b, c in zip(err_x, err_y, err_z)]

    err_x_scaled = minmax_scale([Decimal(str(v)) for v in err_x])
    err_y_scaled = minmax_scale([Decimal(str(v)) for v in err_y])
    err_z_scaled = minmax_scale([Decimal(str(v)) for v in err_z])
    err_mean_scaled = minmax_scale([Decimal(str(v)) for v in err_mean])

    errx_digit_spans = []
    erry_digit_spans = []
    errz_digit_spans = []
    errm_digit_spans = []

    errx_rep_spans = []
    erry_rep_spans = []
    errz_rep_spans = []
    errm_rep_spans = []

    for ex, ey, ez, em in zip(err_x_scaled, err_y_scaled, err_z_scaled, err_mean_scaled):
        sx = component_signature(ex)
        sy = component_signature(ey)
        sz = component_signature(ez)
        sm = component_signature(em)

        errx_digit_spans.append(sx["digit_sum_span"])
        erry_digit_spans.append(sy["digit_sum_span"])
        errz_digit_spans.append(sz["digit_sum_span"])
        errm_digit_spans.append(sm["digit_sum_span"])

        errx_rep_spans.append(sx["repetition_span"])
        erry_rep_spans.append(sy["repetition_span"])
        errz_rep_spans.append(sz["repetition_span"])
        errm_rep_spans.append(sm["repetition_span"])

    tail = max(1, len(err_mean) // 5)
    tail_err_mean = err_mean[-tail:]
    tail_err_x = err_x[-tail:]
    tail_err_y = err_y[-tail:]
    tail_err_z = err_z[-tail:]

    return {
        "condition": "noisy" if noisy else "clean",
        "coupling": float(coupling),
        "mean_abs_sync_error": mean(err_mean),
        "tail_mean_abs_sync_error": mean(tail_err_mean),
        "tail_x_error": mean(tail_err_x),
        "tail_y_error": mean(tail_err_y),
        "tail_z_error": mean(tail_err_z),
        "error_mean_digit_span_std": std(errm_digit_spans),
        "error_mean_repetition_span_std": std(errm_rep_spans),
        "error_component_digit_span_mean_std": mean(
            [std(errx_digit_spans), std(erry_digit_spans), std(errz_digit_spans)]
        ),
        "error_component_repetition_span_mean_std": mean(
            [std(errx_rep_spans), std(erry_rep_spans), std(errz_rep_spans)]
        ),
    }


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


def attach_scores(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    tail_err_vals = [row["tail_mean_abs_sync_error"] for row in rows]
    err_mean_digit_vals = [row["error_mean_digit_span_std"] for row in rows]
    err_mean_rep_vals = [row["error_mean_repetition_span_std"] for row in rows]
    err_comp_digit_vals = [row["error_component_digit_span_mean_std"] for row in rows]
    err_comp_rep_vals = [row["error_component_repetition_span_mean_std"] for row in rows]

    te_lo, te_hi = minmax_params(tail_err_vals)
    emd_lo, emd_hi = minmax_params(err_mean_digit_vals)
    emr_lo, emr_hi = minmax_params(err_mean_rep_vals)
    ecd_lo, ecd_hi = minmax_params(err_comp_digit_vals)
    ecr_lo, ecr_hi = minmax_params(err_comp_rep_vals)

    out = []
    for row in rows:
        norm_tail_err = minmax_norm(row["tail_mean_abs_sync_error"], te_lo, te_hi)
        norm_err_mean_digit = minmax_norm(row["error_mean_digit_span_std"], emd_lo, emd_hi)
        norm_err_mean_rep = minmax_norm(row["error_mean_repetition_span_std"], emr_lo, emr_hi)
        norm_err_comp_digit = minmax_norm(row["error_component_digit_span_mean_std"], ecd_lo, ecd_hi)
        norm_err_comp_rep = minmax_norm(row["error_component_repetition_span_mean_std"], ecr_lo, ecr_hi)

        synchronization_score = (
            0.40 * (1.0 - norm_tail_err)
            + 0.25 * (1.0 - norm_err_mean_digit)
            + 0.15 * (1.0 - norm_err_mean_rep)
            + 0.10 * (1.0 - norm_err_comp_digit)
            + 0.10 * (1.0 - norm_err_comp_rep)
        )

        divergence_score = (
            0.40 * norm_tail_err
            + 0.25 * norm_err_mean_digit
            + 0.15 * norm_err_mean_rep
            + 0.10 * norm_err_comp_digit
            + 0.10 * norm_err_comp_rep
        )

        out.append(
            {
                **row,
                "synchronization_score_v1": synchronization_score,
                "divergence_score_v1": divergence_score,
            }
        )
    return out


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    clean_rows = [summarize_coupling(c, noisy=False, rng=random.Random(RANDOM_SEED)) for c in COUPLING_VALUES]
    noisy_rows = [summarize_coupling(c, noisy=True, rng=random.Random(RANDOM_SEED)) for c in COUPLING_VALUES]

    clean_rows = attach_scores(clean_rows)
    noisy_rows = attach_scores(noisy_rows)

    fieldnames = [
        "condition",
        "coupling",
        "mean_abs_sync_error",
        "tail_mean_abs_sync_error",
        "tail_x_error",
        "tail_y_error",
        "tail_z_error",
        "error_mean_digit_span_std",
        "error_mean_repetition_span_std",
        "error_component_digit_span_mean_std",
        "error_component_repetition_span_mean_std",
        "synchronization_score_v1",
        "divergence_score_v1",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE LORENZ SYNCHRONIZATION NOISE V1")
        print("-" * 100)

        for rows in [clean_rows, noisy_rows]:
            print(rows[0]["condition"])
            for row in rows:
                writer.writerow(
                    {
                        "condition": row["condition"],
                        "coupling": f"{row['coupling']:.2f}",
                        "mean_abs_sync_error": row["mean_abs_sync_error"],
                        "tail_mean_abs_sync_error": row["tail_mean_abs_sync_error"],
                        "tail_x_error": row["tail_x_error"],
                        "tail_y_error": row["tail_y_error"],
                        "tail_z_error": row["tail_z_error"],
                        "error_mean_digit_span_std": row["error_mean_digit_span_std"],
                        "error_mean_repetition_span_std": row["error_mean_repetition_span_std"],
                        "error_component_digit_span_mean_std": row["error_component_digit_span_mean_std"],
                        "error_component_repetition_span_mean_std": row["error_component_repetition_span_mean_std"],
                        "synchronization_score_v1": row["synchronization_score_v1"],
                        "divergence_score_v1": row["divergence_score_v1"],
                    }
                )

                print(
                    f"coupling={row['coupling']:.2f} | "
                    f"tail_err={row['tail_mean_abs_sync_error']:.6f} | "
                    f"sync={row['synchronization_score_v1']:.6f} | "
                    f"div={row['divergence_score_v1']:.6f}"
                )
            print("-" * 100)

        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/lorenz_synchronization_noise_v1.csv"))