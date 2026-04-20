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


def class_feature_summary(
    X_feat: np.ndarray,
    y: np.ndarray,
    class_names: np.ndarray,
    feature_names: List[str],
) -> None:
    print("\nCLASS FEATURE MEANS")
    print("-" * 100)
    for cls_id, cls_name in enumerate(class_names):
        mean_vec = X_feat[y == cls_id].mean(axis=0)
        preview = ", ".join(
            f"{fname}={mean_vec[i]:+.3f}" for i, fname in enumerate(feature_names)
        )
        print(f"{cls_id:>2} | {cls_name:<20} | {preview}")


def main() -> None:
    cfg = DemoConfig()

    X_series, y, class_names = build_dataset(cfg)
    X_baseline = np.stack([extract_baseline_features(x) for x in X_series], axis=0)

    feature_names = [
        "mean",
        "std",
        "skew",
        "kurtosis_excess",
        "autocorr_1",
        "autocorr_2",
        "autocorr_5",
        "dominant_fft_amp",
        "spectral_entropy",
    ]

    train_idx, test_idx = stratified_split(
        y=y,
        train_fraction=cfg.train_fraction,
        seed=cfg.seed + 1,
    )

    X_train = X_baseline[train_idx]
    y_train = y[train_idx]
    X_test = X_baseline[test_idx]
    y_test = y[test_idx]

    y_pred = nearest_centroid_predict(X_train, y_train, X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_macro(y_test, y_pred)

    print("\nSTRUCTURAL REGIME DISCOVERY DEMO - STEP 1")
    print("=" * 100)
    print(f"seed                 : {cfg.seed}")
    print(f"classes              : {cfg.n_classes}")
    print(f"samples_per_class    : {cfg.samples_per_class}")
    print(f"series_length        : {cfg.series_length}")
    print(f"total_samples        : {len(y)}")
    print(f"train_size           : {len(train_idx)}")
    print(f"test_size            : {len(test_idx)}")

    print("\nCLASS COUNTS")
    print("-" * 100)
    for cls_id, cls_name in enumerate(class_names):
        count = int(np.sum(y == cls_id))
        print(f"{cls_id:>2} | {cls_name:<20} | count={count}")

    class_feature_summary(X_baseline, y, class_names, feature_names)

    print("\nBASELINE CLASSIFIER RESULT")
    print("-" * 100)
    print("model                : nearest centroid")
    print("features             : standard baseline only")
    print(f"accuracy             : {acc:.4f}")
    print(f"macro_f1             : {f1:.4f}")

    print("\nINTERPRETATION")
    print("-" * 100)
    print("This step defines the battlefield.")
    print("If baseline performance is already near-perfect, the benchmark is too easy.")
    print("If baseline performance is only moderate, Coordinate Discovery has room to prove value.")


if __name__ == "__main__":
    main()