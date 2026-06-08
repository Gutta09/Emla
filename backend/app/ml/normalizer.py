import numpy as np
from typing import Optional

POSE_COUNT = 33
HAND_COUNT = 21
FEATURE_DIM = POSE_COUNT * 3 + HAND_COUNT * 3 + HAND_COUNT * 3  # 225


def normalize_body_relative(
    pose: list[list[float]],
    left_hand: Optional[list[list[float]]],
    right_hand: Optional[list[list[float]]],
) -> np.ndarray:
    """Convert landmark lists (from WS payload) to normalized 225-d feature vector.

    Normalizes to shoulder midpoint as origin, shoulder width as scale.
    Missing hands are filled with zeros.
    """
    p = np.array(pose, dtype=np.float32)  # (33, 3+)

    left_shoulder = p[11, :3]
    right_shoulder = p[12, :3]
    origin = (left_shoulder + right_shoulder) / 2.0
    scale = float(np.linalg.norm(left_shoulder - right_shoulder)) + 1e-6

    pose_norm = (p[:, :3] - origin) / scale

    if left_hand is None:
        lh_norm = np.zeros((HAND_COUNT, 3), dtype=np.float32)
    else:
        lh = np.array(left_hand, dtype=np.float32)
        lh_norm = (lh[:, :3] - origin) / scale

    if right_hand is None:
        rh_norm = np.zeros((HAND_COUNT, 3), dtype=np.float32)
    else:
        rh = np.array(right_hand, dtype=np.float32)
        rh_norm = (rh[:, :3] - origin) / scale

    return np.concatenate([
        pose_norm.flatten(),
        lh_norm.flatten(),
        rh_norm.flatten(),
    ]).astype(np.float32)


def normalize_hands_only(
    left_hand: Optional[list[list[float]]],
    right_hand: Optional[list[list[float]]],
) -> np.ndarray:
    """Extract and normalize hands for fingerspelling. Returns (126,)."""
    def _norm(hand_data):
        h = np.array(hand_data, dtype=np.float32)
        wrist = h[0, :3]
        scale = float(np.linalg.norm(h[9, :3] - wrist)) + 1e-6
        return ((h[:, :3] - wrist) / scale).flatten()

    lh = _norm(left_hand) if left_hand is not None else np.zeros(HAND_COUNT * 3, dtype=np.float32)
    rh = _norm(right_hand) if right_hand is not None else np.zeros(HAND_COUNT * 3, dtype=np.float32)
    return np.concatenate([lh, rh]).astype(np.float32)
