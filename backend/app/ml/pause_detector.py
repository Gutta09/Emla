import numpy as np


class PauseDetector:
    """Detects word boundaries by measuring inter-frame hand motion energy."""

    def __init__(self, threshold_frames: int = 15, motion_threshold: float = 0.02):
        self.threshold_frames = threshold_frames
        self.motion_threshold = motion_threshold
        self._still_count = 0
        self._prev_hand_vec: np.ndarray | None = None

    def update(self, frame_vec: np.ndarray) -> bool:
        """Feed a normalized frame vector. Returns True exactly once when a pause is detected."""
        # Use only the hand portion of the feature vector (indices 99:225)
        hand_vec = frame_vec[99:]

        if self._prev_hand_vec is None:
            self._prev_hand_vec = hand_vec.copy()
            return False

        motion = float(np.mean((hand_vec - self._prev_hand_vec) ** 2))
        self._prev_hand_vec = hand_vec.copy()

        if motion < self.motion_threshold:
            self._still_count += 1
        else:
            self._still_count = 0

        # Fire exactly once at the threshold crossing
        if self._still_count == self.threshold_frames:
            self._still_count = 0
            return True

        return False

    def reset(self):
        self._still_count = 0
        self._prev_hand_vec = None
