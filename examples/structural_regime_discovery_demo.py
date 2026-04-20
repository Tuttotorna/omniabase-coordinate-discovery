import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class DemoConfig:
    n_classes: int = 4
    samples_per_class: int = 250
    series_length: int = 256
    train_fraction: float = 0.7
    seed: int = 42


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    s = x.std()
    if s < 1e-12:
        return x - x.mean()
    return (x - x.mean()) / s


def minmax_scale(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    mn = x.min()
    mx = x.max()
    if mx - mn < 1e-12:
        return np.zeros_like(x)
    return (x - mn) / (mx - mn)


def autocorr(x: np.ndarray, lag: int) -> float:
    if lag <= 0 or lag >= len(x):
        return 0.0
    x0 = x[:-lag]
    x1 = x[lag:]
    s0 = x0.std()
    s1 = x1.std()
    if s0 < 1e-12 or s1 < 1e-12:
        return 0.0
    return float(np.corrcoef(x0, x1)[0, 1])


def skewness(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    m = x.mean()
    s = x.std()
    if s < 1e-12:
        return 0.0
    z = (x - m) / s
    return float(np.mean(z ** 3))


def kurtosis_excess(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    m = x.mean()
    s = x.std()
    if s < 1e-12:
        return 0.0
    z = (x - m) / s
    return float(np.mean(z ** 4) - 3.0)


def spectral_entropy(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    fft = np.fft.rfft(x)
    power = np.abs(fft) ** 2
    power_sum = power.sum()
    if power_sum < 1e-12:
        return 0.0
    p = power / power_sum
    p = np.clip(p, 1e-12, None)
    h = -np.sum(p * np.log(p))
    return float(h / np.log(len(p)))


def dominant_fft_amplitude(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    fft = np.fft.rfft(x)
    amp = np.abs(fft)
    if len(amp) <= 1:
        return 0.0
    return float(np.max(amp[1:]))


def generate_pure_noise(length: int, rng: np.random.Generator) -> np.ndarray:
    x = rng.normal(0.0, 1.0, size=length)
    return zscore(x)


def generate_weak_periodic(length: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(length)
    freq = rng.uniform(0.05, 0.11)
    phase = rng.uniform(0.0, 2.0 * math.pi)
    amp = rng.uniform(0.18, 0.30)
    noise = rng.normal(0.0, 1.0, size=length)
    x = noise + amp * np.sin(2.0 * math.pi * freq * t + phase)
    return zscore(x)


def generate_piecewise_switching(length: int, rng: np.random.Generator) -> np.ndarray:
    x = np.zeros(length, dtype=float)
    idx = 0
    state = rng.choice([-1.0, 1.0])
    while idx < length:
        seg_len = int(rng.integers(18, 48))
        end = min(length, idx + seg_len)
        local_mean = 0.38 * state
        local_noise = rng.normal(local_mean, 0.85, size=end - idx)
        x[idx:end] = local_noise
        if rng.random() < 0.85:
            state *= -1.0
        idx = end
    return zscore(x)


def generate_lagged_dependency(length: int, rng: np.random.Generator) -> np.ndarray:
    x = np.zeros(length, dtype=float)
    lag = int(rng.integers(3, 9))
    alpha = rng.uniform(0.45, 0.62)
    noise = rng.normal(0.0, 1.0, size=length)
    for i in range(length):
        back = x[i - lag] if i >= lag else 0.0
        x[i] = alpha * back + noise[i]
    return zscore(x)


def extract_baseline_features(x: np.ndarray) -> np.ndarray:
    return np.array(
        [
            float(np.mean(x)),
            float(np.std(x)),
            skewness(x),
            kurtosis_excess(x),
            autocorr(x, 1),
            autocorr(x, 2),
            autocorr(x, 5),
            dominant_fft_amplitude(x),
            spectral_entropy(x),
        ],
        dtype=float,
    )


def quantize_series(x: np.ndarray, base: int) -> np.ndarray:
    scaled = minmax_scale(x)
    q = np.floor(scaled * base).astype(int)
    q = np.clip(q, 0, base - 1)
    return q


def digit_transition_entropy(digits: np.ndarray, base: int) -> float:
    if len(digits) < 2:
        return 0.0
    counts = np.zeros((base, base), dtype=float)
    for a, b in zip(digits[:-1], digits[1:]):
        counts[a, b] += 1.0
    flat = counts.ravel()
    total = flat.sum()
    if total < 1e-12:
        return 0.0
    p = flat / total
    p = p[p > 0]
    h = -np.sum(p * np.log(p))
    return float(h / np.log(base * base))


def digit_run_length_mean(digits: np.ndarray) -> float:
    if len(digits) == 0:
        return 0.0
    runs = []
    current = 1
    for i in range(1, len(digits)):
        if digits[i] == digits[i - 1]:
            current += 1
        else:
            runs.append(current)
            current = 1
    runs.append(current)
    return float(np.mean(runs))


def digit_change_rate(digits: np.ndarray) -> float:
    if len(digits) < 2:
        return 0.0
    return float(np.mean(digits[1:] != digits[:-1]))


def digit_distribution_entropy(digits: np.ndarray, base: int) -> float:
    counts = np.bincount(digits, minlength=base).astype(float)
    total = counts.sum()
    if total < 1e-12:
        return 0.0
    p = counts / total
    p = p[p > 0]
    h = -np.sum(p * np.log(p))
    return float(h / np.log(base))


def multibase_signature(x: np.ndarray, bases: List[int]) -> np.ndarray:
    feats = []
    for base in bases:
        digits = quantize_series(x, base)
        feats.extend(
            [
                digit_distribution_entropy(digits, base),
                digit_transition_entropy(digits, base),
                digit_run_length_mean(digits),
                digit_change_rate(digits),
            ]
        )
    return np.array(feats, dtype=float)


def extract_coordinate_discovery_features(x: np.ndarray) -> np.ndarray:
    bases = [2, 3, 5, 7, 10]
    sig = multibase_signature(x, bases)

    grouped = sig.reshape(len(bases), 4)
    entropies = grouped[:, 0]
    transition_entropies = grouped[:, 1]
    run_lengths = grouped[:, 2]
    change_rates = grouped[:, 3]

    # Coordinate synthesis
    coord_periodicity = float(np.mean(run_lengths) - np.mean(change_rates))
    coord_transition_instability = float(np.std(transition_entropies))
    coord_multibase_entropy_slope = float(entropies[-1] - entropies[0])
    coord_crossbase_consistency = float(1.0 / (1.0 + np.std(grouped, axis=0).mean()))
    coord_lag_signature = float(np.mean([abs(autocorr(x, k)) for k in [3, 5, 7, 9]]))

    return np.concatenate(
        [
            sig,
            np.array(
                [
                    coord_periodicity,
                    coord_transition_instability,
                    coord_multibase_entropy_slope,
                    coord_crossbase_consistency,
                    coord_lag_signature,
                ],
                dtype=float,
            ),
        ]
    )


def standardize_from_train(
    X_train: np.ndarray,
    X_test: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    mu = X_train.mean(axis=0)
    sigma = X_train.std(axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    return (X_train - mu) / sigma, (X_test - mu) / sigma


def build_dataset(cfg: DemoConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(cfg.seed)

    generators = [
        generate_pure_noise,
        generate_weak_periodic,
        generate_piecewise_switching,
        generate_lagged_dependency,
    ]
    class_names = np.array(
        [
            "pure_noise",
            "weak_periodic",
            "piecewise_switching",
            "lagged_dependency",
        ]
    )

    series_list: List[np.ndarray] = []
    y_list: List[int] = []

    for class_id, gen in enumerate(generators):
        for _ in range(cfg.samples_per_class):
            series = gen(cfg.series_length, rng)
            series_list.append(series)
            y_list.append(class_id)

    X_series = np.stack(series_list, axis=0)
    y = np.array(y_list, dtype=int)
    return X_series, y, class_names


def stratified_split(
    y: np.ndarray,
    train_fraction: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    train_idx = []
    test_idx = []

    for cls in np.unique(y):
        cls_idx = np.where(y == cls)[0]
        rng.shuffle(cls_idx)
        n_train = int(len(cls_idx) * train_fraction)
        train_idx.extend(cls_idx[:n_train].tolist())
        test_idx.extend(cls_idx[n_train:].tolist())

    train_idx = np.array(train_idx, dtype=int)
    test_idx = np.array(test_idx, dtype=int)
    rng.shuffle(train_idx)
    rng.shuffle(test_idx)
    return train_idx, test_idx


def nearest_centroid_predict(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
) -> np.ndarray:
    centroids: Dict[int, np.ndarray] = {}
    for cls in np.unique(y_train):
        centroids[int(cls)] = X_train[y_train == cls].mean(axis=0)

    preds = []
    for x in X_test:
        best_cls = None
        best_dist = None
        for cls, c in centroids.items():
            d = float(np.linalg.norm(x - c))
            if best_dist is None or d < best_dist:
                best_dist = d
                best_cls = cls
        preds.append(int(best_cls))
    return np.array(preds, dtype=int)


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(y_true == y_pred))


def f1_macro(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    classes = np.unique(y_true)
    f1s = []

    for cls in classes:
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fp = np.sum((y_true != cls) & (y_pred == cls))
        fn = np.sum((y_true == cls) & (y_pred != cls))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        if precision + recall == 0.0:
            f1 = 0.0
        else:
            f1 = 2.0 * precision * recall / (precision + recall)
        f1s.append(f1)

    return float(np.mean(f1s))


def pairwise_centroid_separation(X: np.ndarray, y: np.ndarray) -> float:
    classes = np.unique(y)
    centroids = [X[y == cls].mean(axis=0) for cls in classes]
    dists = []
    for i in range(len(centroids)):
        for j in range(i + 1, len(centroids)):
            dists.append(float(np.linalg.norm(centroids[i] - centroids[j])))
    return float(np.mean(dists)) if dists else 0.0


def mean_within_class_dispersion(X: np.ndarray, y: np.ndarray) -> float:
    classes = np.unique(y)
    vals = []
    for cls in classes:
        xc = X[y == cls]
        c = xc.mean(axis=0)
        vals.append(float(np.mean(np.linalg.norm(xc - c, axis=1))))
    return float(np.mean(vals))


def evaluate_feature_space(
    name: str,
    X: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
) -> Dict[str, float]:
    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]

    X_train_z, X_test_z = standardize_from_train(X_train, X_test)
    y_pred = nearest_centroid_predict(X_train_z, y_train, X_test_z)

    full_X_train_z, full_X_test_z = standardize_from_train(X_train, X_test)
    full_X_z = np.zeros_like(X)
    full_X_z[train_idx] = full_X_train_z
    full_X_z[test_idx] = full_X_test_z

    separation = pairwise_centroid_separation(full_X_z, y)
    dispersion = mean_within_class_dispersion(full_X_z, y)
    ratio = separation / max(dispersion, 1e-12)

    return {
        "name": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "macro_f1": f1_macro(y_test, y_pred),
        "centroid_separation": separation,
        "within_dispersion": dispersion,
        "sep_disp_ratio": ratio,
    }


def print_result_table(results: List[Dict[str, float]]) -> None:
    print("\nFEATURE SPACE COMPARISON")
    print("-" * 120)
    print(
        f"{'space':<20} {'accuracy':>10} {'macro_f1':>10} "
        f"{'cent_sep':>12} {'within_disp':>14} {'sep/disp':>10}"
    )
    print("-" * 120)
    for r in results:
        print(
            f"{r['name']:<20} "
            f"{r['accuracy']:>10.4f} "
            f"{r['macro_f1']:>10.4f} "
            f"{r['centroid_separation']:>12.4f} "
            f"{r['within_dispersion']:>14.4f} "
            f"{r['sep_disp_ratio']:>10.4f}"
        )


def main() -> None:
    cfg = DemoConfig()

    X_series, y, class_names = build_dataset(cfg)

    X_baseline = np.stack([extract_baseline_features(x) for x in X_series], axis=0)
    X_discovered = np.stack(
        [extract_coordinate_discovery_features(x) for x in X_series],
        axis=0,
    )
    X_combined = np.concatenate([X_baseline, X_discovered], axis=1)

    train_idx, test_idx = stratified_split(
        y=y,
        train_fraction=cfg.train_fraction,
        seed=cfg.seed + 1,
    )

    results = [
        evaluate_feature_space("baseline", X_baseline, y, train_idx, test_idx),
        evaluate_feature_space("discovered", X_discovered, y, train_idx, test_idx),
        evaluate_feature_space("combined", X_combined, y, train_idx, test_idx),
    ]

    print("\nSTRUCTURAL REGIME DISCOVERY DEMO - STEP 2")
    print("=" * 120)
    print(f"seed                 : {cfg.seed}")
    print(f"classes              : {cfg.n_classes}")
    print(f"samples_per_class    : {cfg.samples_per_class}")
    print(f"series_length        : {cfg.series_length}")
    print(f"total_samples        : {len(y)}")
    print(f"train_size           : {len(train_idx)}")
    print(f"test_size            : {len(test_idx)}")

    print("\nCLASS COUNTS")
    print("-" * 120)
    for cls_id, cls_name in enumerate(class_names):
        count = int(np.sum(y == cls_id))
        print(f"{cls_id:>2} | {cls_name:<20} | count={count}")

    print_result_table(results)

    baseline = results[0]
    discovered = results[1]
    combined = results[2]

    print("\nDELTA VS BASELINE")
    print("-" * 120)
    print(
        f"discovered accuracy delta  : {discovered['accuracy'] - baseline['accuracy']:+.4f}"
    )
    print(
        f"discovered macro_f1 delta  : {discovered['macro_f1'] - baseline['macro_f1']:+.4f}"
    )
    print(
        f"discovered sep/disp delta  : {discovered['sep_disp_ratio'] - baseline['sep_disp_ratio']:+.4f}"
    )
    print(
        f"combined accuracy delta    : {combined['accuracy'] - baseline['accuracy']:+.4f}"
    )
    print(
        f"combined macro_f1 delta    : {combined['macro_f1'] - baseline['macro_f1']:+.4f}"
    )
    print(
        f"combined sep/disp delta    : {combined['sep_disp_ratio'] - baseline['sep_disp_ratio']:+.4f}"
    )

    print("\nREADING RULE")
    print("-" * 120)
    print("The claim survives only if discovered or combined clearly beats baseline.")
    print("If discovered does not improve separation or classification, Coordinate Discovery failed here.")
    print("If combined improves and discovered alone is competitive, the new coordinates are carrying usable structure.")


if __name__ == "__main__":
    main()