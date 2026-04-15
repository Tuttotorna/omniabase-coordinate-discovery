from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

SIGMA = Decimal("10.0")
BETA = Decimal("2.6666666666666667")  # 8/3

# Reference library of known regimes
REFERENCE_RHOS = [
    Decimal("10.0"),
    Decimal("13.0"),
    Decimal("14.0"),
    Decimal("20.0"),
    Decimal("25.0"),
    Decimal("28.0"),
]

# Blind test set
BLIND_RHOS = [
    Decimal("11.0"),
    Decimal("15.0"),
    Decimal("18.0"),
    Decimal("24.0"),
    Decimal("27.0"),
]

X0 = Decimal("0.1")
Y0 = Decimal("0.0")
Z0 = Decimal("0.0")

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


def summarize_regime(rho: Decimal) -> dict[str, float]:
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

    component_digit_mean = mean([std(x_digit_spans), std(y_digit_spans), std(z_digit_spans)])
    component_rep_mean = mean([std(x_rep_spans), std(y_rep_spans), std(z_rep_spans)])
    radius_digit_std = std(r_digit_spans)
    radius_rep_std = std(r_rep_spans)

    return {
        "rho": float(rho),
        "unique_xyz_triplets": float(unique_xyz),
        "x_std": std([float(x) for x in xs]),
        "y_std": std([float(y) for y in ys]),
        "z_std": std([float(z) for z in zs]),
        "component_digit_mean": component_digit_mean,
        "component_rep_mean": component_rep_mean,
        "radius_digit_std": radius_digit_std,
        "radius_rep_std": radius_rep_std,
    }


def classify_reference(summary: dict[str, float]) -> str:
    if summary["unique_xyz_triplets"] <= 10:
        return "stable"
    if summary["radius_digit_std"] > 2.7 and summary["component_digit_mean"] > 2.4:
        return "high_chaotic"
    if summary["radius_digit_std"] > 2.3:
        return "transition_or_complex"
    return "complex"


def feature_vector(summary: dict[str, float]) -> list[float]:
    return [
        summary["unique_xyz_triplets"],
        summary["component_digit_mean"],
        summary["component_rep_mean"],
        summary["radius_digit_std"],
        summary["radius_rep_std"],
        summary["x_std"],
        summary["y_std"],
        summary["z_std"],
    ]


def zscore_normalize(
    reference_rows: list[dict[str, float]],
    blind_rows: list[dict[str, float]],
) -> tuple[list[list[float]], list[list[float]]]:
    ref_vectors = [feature_vector(r) for r in reference_rows]
    blind_vectors = [feature_vector(r) for r in blind_rows]

    means = [mean([v[i] for v in ref_vectors]) for i in range(len(ref_vectors[0]))]
    stds = [std([v[i] for v in ref_vectors]) for i in range(len(ref_vectors[0]))]  # population std

    def norm(vec: list[float]) -> list[float]:
        out = []
        for x, m, s in zip(vec, means, stds):
            if s == 0.0:
                out.append(0.0)
            else:
                out.append((x - m) / s)
        return out

    return [norm(v) for v in ref_vectors], [norm(v) for v in blind_vectors]


def euclidean_distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    reference_rows = [summarize_regime(rho) for rho in REFERENCE_RHOS]
    blind_rows = [summarize_regime(rho) for rho in BLIND_RHOS]

    reference_labels = [classify_reference(row) for row in reference_rows]
    ref_norm, blind_norm = zscore_normalize(reference_rows, blind_rows)

    fieldnames = [
        "mode",
        "rho_true",
        "predicted_reference_rho",
        "predicted_label",
        "distance_to_reference",
        "unique_xyz_triplets",
        "component_digit_mean",
        "component_rep_mean",
        "radius_digit_std",
        "radius_rep_std",
        "x_std",
        "y_std",
        "z_std",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE LORENZ BLIND REGIME CLASSIFICATION V1")
        print("-" * 92)

        for row, label in zip(reference_rows, reference_labels):
            writer.writerow(
                {
                    "mode": "reference",
                    "rho_true": row["rho"],
                    "predicted_reference_rho": row["rho"],
                    "predicted_label": label,
                    "distance_to_reference": 0.0,
                    **{k: row[k] for k in fieldnames if k in row},
                }
            )

        for blind_row, blind_vec in zip(blind_rows, blind_norm):
            distances = []
            for ref_row, ref_label, ref_vec in zip(reference_rows, reference_labels, ref_norm):
                d = euclidean_distance(blind_vec, ref_vec)
                distances.append((d, ref_row["rho"], ref_label))

            distances.sort(key=lambda x: x[0])
            best_d, best_rho, best_label = distances[0]

            writer.writerow(
                {
                    "mode": "blind",
                    "rho_true": blind_row["rho"],
                    "predicted_reference_rho": best_rho,
                    "predicted_label": best_label,
                    "distance_to_reference": best_d,
                    **{k: blind_row[k] for k in fieldnames if k in blind_row},
                }
            )

            print(
                f"blind_rho={blind_row['rho']:.1f} | "
                f"pred_ref_rho={best_rho:.1f} | "
                f"pred_label={best_label} | "
                f"distance={best_d:.6f}"
            )

        print("-" * 92)
        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/lorenz_blind_regime_classification_v1.csv"))