import numpy as np
from collections import deque


class PauseDetector:
    """Commits a sign when the same label is predicted confidently for N consecutive frames.

    No deliberate pause needed — just hold the sign and it auto-commits.
    """

    def __init__(self, confirm_frames: int = 10, cooldown_frames: int = 20):
        self.confirm_frames = confirm_frames   # frames of same confident sign to commit
        self.cooldown_frames = cooldown_frames # frames to wait before committing same sign again
        self._recent: deque = deque(maxlen=confirm_frames)
        self._last_committed: str | None = None
        self._cooldown: int = 0

    def update(self, sign: str, confident: bool) -> bool:
        """Feed current prediction. Returns True when a sign should be committed."""
        if self._cooldown > 0:
            self._cooldown -= 1

        if not confident or not sign or sign in ("?", "—"):
            self._recent.clear()
            return False

        self._recent.append(sign)

        if len(self._recent) < self.confirm_frames:
            return False

        # All recent frames agree on the same sign
        if len(set(self._recent)) != 1:
            return False

        # Don't re-commit the same sign during cooldown
        if sign == self._last_committed and self._cooldown > 0:
            return False

        self._last_committed = sign
        self._cooldown = self.cooldown_frames
        self._recent.clear()
        return True

    def reset(self):
        self._recent.clear()
        self._last_committed = None
        self._cooldown = 0
