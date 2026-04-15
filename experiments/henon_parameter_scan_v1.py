from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import math

getcontext().prec = 50

# Hénon map parameter scan
A_START = Decimal("1.000")
A_END = Decimal("1.400")
A_STEP = Decimal("0.020")
B = Decimal("0.3")

X0 = Decimal("0.1")
Y0 = Decimal("0.1")

TOTAL_STEPS = 1400
BURN_IN = 500

BASES = list(range(2, 17))
DECIMAL_DIGITS = 12


def henon_step(x: Decimal, y: Decimal, a: Decimal, b: Decimal) -> tuple[Decimal, Decimal]:
    x_next = Decimal("1") - a * x * x + y
    y_next = b * x
    return x_next, y_next


def generate_trajectory(a: Decimal) -> list[tuple[Decimal, Decimal]]:
    x = X0
    y = Y0
    out: list[tuple[Decimal, Decimal]] = []

    for _ in range(TOTAL_STEPS):
        x, y = henon_step(x, y, a, B)
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


def joint_radius(x: Decimal, y: Decimal) -> float:
    return math.sqrt(float(x * x + y * y))


def joint_product(x: Decimal, y: Decimal) -> Decimal:
    return x * y


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


def summarize_for_a(a: Decimal) -> dict[str, float]:
    trajectory = generate_trajectory(a)

    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    radii = [joint_radius(x, y) for x, y in trajectory]
    products = [joint_product(x, y) for x, y in trajectory]

    xs_scaled = minmax_scale(xs)
    ys_scaled = minmax_scale(ys)
    radii_scaled = minmax_scale([Decimal(str(v)) for v in radii])
    products_scaled = minmax_scale(products)

    x_digit_spans = []
    x_rep_spans = []
    y_digit_spans = []
    y_rep_spans = []
    r_digit_spans = []
    r_rep_spans = []
    p_digit_spans = []
    p_rep_spans = []

    for xs_n, ys_n, rs_n, ps_n in zip(xs_scaled, ys_scaled, radii_scaled, products_scaled):
        sig_x = component_signature(xs_n)
        sig_y = component_signature(ys_n)
        sig_r = component_signature(rs_n)
        sig_p = component_signature(ps_n)

        x_digit_spans.append(sig_x["digit_sum_span"])
        x_rep_spans.append(sig_x["repetition_span"])
        y_digit_spans.append(sig_y["digit_sum_span"])
        y_rep_spans.append(sig_y["repetition_span"])
        r_digit_spans.append(sig_r["digit_sum_span"])
        r_rep_spans.append(sig_r["repetition_span"])
        p_digit_spans.append(sig_p["digit_sum_span"])
        p_rep_spans.append(sig_p["repetition_span"])

    component_digit_mean = mean([std(x_digit_spans), std(y_digit_spans)])
    component_rep_mean = mean([std(x_rep_spans), std(y_rep_spans)])

    radius_digit_std = std(r_digit_spans)
    radius_rep_std = std(r_rep_spans)
    product_digit_std = std(p_digit_spans)
    product_rep_std = std(p_rep_spans)

    unique_x = len({round(float(x), 10) for x in xs})
    unique_y = len({round(float(y), 10) for y in ys})
    unique_xy_pairs = len({(round(float(x), 8), round(float(y), 8)) for x, y in trajectory})

    return {
        "a": float(a),
        "unique_x": float(unique_x),
        "unique_y": float(unique_y),
        "unique_xy_pairs": float(unique_xy_pairs),
        "x_std": std([float(x) for x in xs]),
        "y_std": std([float(y) for y in ys]),
        "component_digit_mean": component_digit_mean,
        "component_rep_mean": component_rep_mean,
        "radius_digit_std": radius_digit_std,
        "radius_rep_std": radius_rep_std,
        "product_digit_std": product_digit_std,
        "product_rep_std": product_rep_std,
    }


def generate_a_values() -> list[Decimal]:
    values = []
    a = A_START
    while a <= A_END:
        values.append(a)
        a += A_STEP
    return values


def attach_scores(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    product_digit_vals = [row["product_digit_std"] for row in rows]
    product_rep_vals = [row["product_rep_std"] for row in rows]
    radius_digit_vals = [row["radius_digit_std"] for row in rows]
    radius_rep_vals = [row["radius_rep_std"] for row in rows]
    component_digit_vals = [row["component_digit_mean"] for row in rows]
    component_rep_vals = [row["component_rep_mean"] for row in rows]
    unique_pair_vals = [row["unique_xy_pairs"] for row in rows]

    rel_product_digit = build_relative_deltas(product_digit_vals)
    rel_product_rep = build_relative_deltas(product_rep_vals)
    rel_component_digit = build_relative_deltas(component_digit_vals)
    rel_component_rep = build_relative_deltas(component_rep_vals)

    up_lo, up_hi = minmax_params(unique_pair_vals)
    cd_lo, cd_hi = minmax_params(component_digit_vals)
    cr_lo, cr_hi = minmax_params(component_rep_vals)
    rd_lo, rd_hi = minmax_params(radius_digit_vals)
    rr_lo, rr_hi = minmax_params(radius_rep_vals)
    pd_lo, pd_hi = minmax_params(product_digit_vals)
    pr_lo, pr_hi = minmax_params(product_rep_vals)
    rpd_lo, rpd_hi = minmax_params(rel_product_digit)
    rpr_lo, rpr_hi = minmax_params(rel_product_rep)
    rcd_lo, rcd_hi = minmax_params(rel_component_digit)
    rcr_lo, rcr_hi = minmax_params(rel_component_rep)

    out = []
    for row, d_pd, d_pr, d_cd, d_cr in zip(
        rows, rel_product_digit, rel_product_rep, rel_component_digit, rel_component_rep
    ):
        norm_unique_pairs = minmax_norm(row["unique_xy_pairs"], up_lo, up_hi)
        norm_component_digit = minmax_norm(row["component_digit_mean"], cd_lo, cd_hi)
        norm_component_rep = minmax_norm(row["component_rep_mean"], cr_lo, cr_hi)
        norm_radius_digit = minmax_norm(row["radius_digit_std"], rd_lo, rd_hi)
        norm_radius_rep = minmax_norm(row["radius_rep_std"], rr_lo, rr_hi)
        norm_product_digit = minmax_norm(row["product_digit_std"], pd_lo, pd_hi)
        norm_product_rep = minmax_norm(row["product_rep_std"], pr_lo, pr_hi)
        norm_rel_product_digit = minmax_norm(d_pd, rpd_lo, rpd_hi)
        norm_rel_product_rep = minmax_norm(d_pr, rpr_lo, rpr_hi)
        norm_rel_component_digit = minmax_norm(d_cd, rcd_lo, rcd_hi)
        norm_rel_component_rep = minmax_norm(d_cr, rcr_lo, rcr_hi)

        # Hierarchical order:
        # stable global geometry + stable component behavior + low state occupancy complexity
        order_score = (
            0.25 * (1.0 - norm_unique_pairs)
            + 0.25 * (1.0 - norm_component_digit)
            + 0.15 * (1.0 - norm_component_rep)
            + 0.20 * (1.0 - norm_radius_digit)
            + 0.15 * (1.0 - norm_radius_rep)
        )

        # Hierarchical event:
        # product is strongest relational tension carrier, plus local deltas
        event_score = (
            0.20 * norm_product_digit
            + 0.15 * norm_product_rep
            + 0.25 * norm_rel_product_digit
            + 0.20 * norm_rel_product_rep
            + 0.10 * norm_rel_component_digit
            + 0.10 * norm_rel_component_rep
        )

        out.append(
            {
                **row,
                "rel_product_digit_std": d_pd,
                "rel_product_rep_std": d_pr,
                "rel_component_digit_mean": d_cd,
                "rel_component_rep_mean": d_cr,
                "order_score_v1": order_score,
                "event_score_v1": event_score,
            }
        )

    return out


def run(output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = [summarize_for_a(a) for a in generate_a_values()]
    rows = attach_scores(rows)

    fieldnames = [
        "a",
        "unique_x",
        "unique_y",
        "unique_xy_pairs",
        "x_std",
        "y_std",
        "component_digit_mean",
        "component_rep_mean",
        "radius_digit_std",
        "radius_rep_std",
        "product_digit_std",
        "product_rep_std",
        "rel_product_digit_std",
        "rel_product_rep_std",
        "rel_component_digit_mean",
        "rel_component_rep_mean",
        "order_score_v1",
        "event_score_v1",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("OMNIABASE HENON PARAMETER SCAN V1")
        print("-" * 88)

        for row in rows:
            writer.writerow(
                {
                    "a": f"{row['a']:.3f}",
                    "unique_x": int(row["unique_x"]),
                    "unique_y": int(row["unique_y"]),
                    "unique_xy_pairs": int(row["unique_xy_pairs"]),
                    "x_std": row["x_std"],
                    "y_std": row["y_std"],
                    "component_digit_mean": row["component_digit_mean"],
                    "component_rep_mean": row["component_rep_mean"],
                    "radius_digit_std": row["radius_digit_std"],
                    "radius_rep_std": row["radius_rep_std"],
                    "product_digit_std": row["product_digit_std"],
                    "product_rep_std": row["product_rep_std"],
                    "rel_product_digit_std": row["rel_product_digit_std"],
                    "rel_product_rep_std": row["rel_product_rep_std"],
                    "rel_component_digit_mean": row["rel_component_digit_mean"],
                    "rel_component_rep_mean": row["rel_component_rep_mean"],
                    "order_score_v1": row["order_score_v1"],
                    "event_score_v1": row["event_score_v1"],
                }
            )

            print(
                f"a={row['a']:.3f} | "
                f"pairs={int(row['unique_xy_pairs'])} | "
                f"order={row['order_score_v1']:.6f} | "
                f"event={row['event_score_v1']:.6f}"
            )

        print("-" * 88)
        print(f"Done. Wrote {output_csv}")


if __name__ == "__main__":
    run(Path("outputs/henon_parameter_scan_v1.csv"))