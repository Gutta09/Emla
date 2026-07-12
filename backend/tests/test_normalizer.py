import numpy as np

from app.ml.normalizer import normalize_body_relative, normalize_hands_only, FEATURE_DIM


def _pose(n=33):
    # shoulders at indices 11 and 12; give them a known 1.0 separation on x
    p = [[0.0, 0.0, 0.0] for _ in range(n)]
    p[11] = [0.0, 1.0, 0.0]  # left shoulder
    p[12] = [1.0, 1.0, 0.0]  # right shoulder
    return p


def _hand(x=0.0):
    return [[x + i * 0.01, 0.0, 0.0] for i in range(21)]


def test_body_relative_returns_225_dims():
    v = normalize_body_relative(_pose(), _hand(), _hand())
    assert v.shape == (FEATURE_DIM,)
    assert v.dtype == np.float32


def test_body_relative_centres_on_shoulder_midpoint():
    # midpoint of shoulders is (0.5, 1.0, 0); scale is shoulder width = 1.0.
    v = normalize_body_relative(_pose(), None, None)
    pose_norm = v[: 33 * 3].reshape(33, 3)
    # left shoulder (idx 11) relative to midpoint → x = -0.5
    assert np.isclose(pose_norm[11][0], -0.5, atol=1e-4)
    assert np.isclose(pose_norm[12][0], 0.5, atol=1e-4)


def test_body_relative_zero_fills_missing_hands():
    v = normalize_body_relative(_pose(), None, None)
    hands = v[33 * 3 :]
    assert np.allclose(hands, 0.0)


def test_hands_only_returns_126_dims_and_zero_fills():
    v = normalize_hands_only(_hand(), None)
    assert v.shape == (126,)
    # right hand (missing) is the second half → all zeros
    assert np.allclose(v[63:], 0.0)
    # left hand wrist-relative: index 0 (wrist) maps to origin
    assert np.allclose(v[0:3], 0.0)


def test_scale_never_divides_by_zero():
    # degenerate pose with coincident shoulders — the 1e-6 epsilon guards it
    p = [[0.0, 0.0, 0.0] for _ in range(33)]
    v = normalize_body_relative(p, None, None)
    assert np.all(np.isfinite(v))
