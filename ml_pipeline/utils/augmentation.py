import numpy as np


def time_warp(sequence: np.ndarray, sigma: float = 0.2) -> np.ndarray:
    """Stretch/compress temporal axis via cumulative random walk."""
    T = sequence.shape[0]
    steps = np.random.normal(loc=1.0, scale=sigma, size=T)
    steps = np.clip(steps, 0.1, 3.0)
    warp = np.cumsum(steps)
    warp = (warp / warp[-1]) * (T - 1)
    warped = np.array([sequence[int(np.clip(round(w), 0, T - 1))] for w in warp])
    return warped.astype(np.float32)


def mirror_sequence(sequence: np.ndarray) -> np.ndarray:
    """Swap left/right hands and negate x-coordinates (handles left-handed signers)."""
    seq = sequence.copy()
    # Layout: pose(99) | left_hand(63) | right_hand(63)
    pose = seq[:, :99].copy()
    lh = seq[:, 99:162].copy()
    rh = seq[:, 162:].copy()

    # Negate x in pose (every 3rd value starting at 0)
    pose[:, 0::3] *= -1
    lh[:, 0::3] *= -1
    rh[:, 0::3] *= -1

    # Swap left and right
    return np.concatenate([pose, rh, lh], axis=1).astype(np.float32)


def add_noise(sequence: np.ndarray, sigma: float = 0.01) -> np.ndarray:
    return (sequence + np.random.normal(0, sigma, sequence.shape)).astype(np.float32)


def random_scale(sequence: np.ndarray, scale_range=(0.9, 1.1)) -> np.ndarray:
    """Scale all coordinates by a random factor."""
    s = np.random.uniform(*scale_range)
    return (sequence * s).astype(np.float32)


def augment_sequence(sequence: np.ndarray) -> np.ndarray:
    """Apply random combination of augmentations."""
    if np.random.rand() < 0.5:
        sequence = time_warp(sequence)
    if np.random.rand() < 0.5:
        sequence = mirror_sequence(sequence)
    if np.random.rand() < 0.6:
        sequence = add_noise(sequence)
    if np.random.rand() < 0.4:
        sequence = random_scale(sequence)
    return sequence
