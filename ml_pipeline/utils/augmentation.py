import numpy as np


def time_warp(sequence: np.ndarray, sigma: float = 0.25) -> np.ndarray:
    T = sequence.shape[0]
    steps = np.random.normal(loc=1.0, scale=sigma, size=T)
    steps = np.clip(steps, 0.1, 3.0)
    warp = np.cumsum(steps)
    warp = (warp / warp[-1]) * (T - 1)
    warped = np.array([sequence[int(np.clip(round(w), 0, T - 1))] for w in warp])
    return warped.astype(np.float32)


def mirror_sequence(sequence: np.ndarray) -> np.ndarray:
    seq = sequence.copy()
    pose = seq[:, :99].copy()
    lh = seq[:, 99:162].copy()
    rh = seq[:, 162:].copy()
    pose[:, 0::3] *= -1
    lh[:, 0::3] *= -1
    rh[:, 0::3] *= -1
    return np.concatenate([pose, rh, lh], axis=1).astype(np.float32)


def add_noise(sequence: np.ndarray, sigma: float = 0.015) -> np.ndarray:
    return (sequence + np.random.normal(0, sigma, sequence.shape)).astype(np.float32)


def random_scale(sequence: np.ndarray, scale_range=(0.85, 1.15)) -> np.ndarray:
    s = np.random.uniform(*scale_range)
    return (sequence * s).astype(np.float32)


def random_shift(sequence: np.ndarray, shift_range=0.05) -> np.ndarray:
    """Shift all coordinates by a small random offset (signer position variation)."""
    shift = np.random.uniform(-shift_range, shift_range, (1, sequence.shape[1]))
    return (sequence + shift).astype(np.float32)


def speed_variation(sequence: np.ndarray) -> np.ndarray:
    """Randomly speed up or slow down signing."""
    T = sequence.shape[0]
    factor = np.random.uniform(0.7, 1.4)
    new_T = int(T * factor)
    new_T = max(5, min(new_T, T * 2))
    indices = np.linspace(0, T - 1, new_T)
    resampled = np.array([sequence[int(np.clip(i, 0, T - 1))] for i in indices])
    # Resample back to original length
    final_indices = np.linspace(0, len(resampled) - 1, T)
    return np.array([resampled[int(np.clip(i, 0, len(resampled) - 1))] for i in final_indices]).astype(np.float32)


def dropout_frames(sequence: np.ndarray, p: float = 0.05) -> np.ndarray:
    """Randomly zero out a few frames to simulate missed detections."""
    seq = sequence.copy()
    mask = np.random.rand(len(seq)) < p
    seq[mask] = 0.0
    return seq.astype(np.float32)


def augment_sequence(sequence: np.ndarray, strong: bool = False) -> np.ndarray:
    """Apply random combination of augmentations. strong=True applies more transforms."""
    prob = 0.8 if strong else 0.5

    if np.random.rand() < prob:
        sequence = time_warp(sequence)
    if np.random.rand() < prob:
        sequence = mirror_sequence(sequence)
    if np.random.rand() < 0.8:
        sequence = add_noise(sequence)
    if np.random.rand() < prob:
        sequence = random_scale(sequence)
    if np.random.rand() < prob:
        sequence = random_shift(sequence)
    if np.random.rand() < (0.6 if strong else 0.3):
        sequence = speed_variation(sequence)
    if np.random.rand() < 0.3:
        sequence = dropout_frames(sequence)
    return sequence


def generate_augmented_dataset(X: np.ndarray, y: np.ndarray, target_per_class: int = 80) -> tuple:
    """Oversample each class to target_per_class via augmentation."""
    classes = np.unique(y)
    X_out, y_out = [X.copy()], [y.copy()]

    for cls in classes:
        idx = np.where(y == cls)[0]
        n_have = len(idx)
        n_need = target_per_class - n_have
        if n_need <= 0:
            continue
        for _ in range(n_need):
            src = X[idx[np.random.randint(n_have)]]
            X_out.append(augment_sequence(src, strong=True)[np.newaxis])
            y_out.append([cls])

    return (
        np.concatenate(X_out, axis=0).astype(np.float32),
        np.concatenate(y_out, axis=0).astype(np.int32),
    )
