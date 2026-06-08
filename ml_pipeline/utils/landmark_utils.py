import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

POSE_COUNT = 33
HAND_COUNT = 21
FEATURE_DIM = POSE_COUNT * 3 + HAND_COUNT * 3 + HAND_COUNT * 3  # 225

BASE_DIR = None  # set at runtime


def _models_dir():
    import os
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")


def make_hand_landmarker(num_hands: int = 2):
    import os
    model_path = os.path.join(_models_dir(), "hand_landmarker.task")
    base_options = mp_python.BaseOptions(model_asset_path=model_path)
    options = mp_vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.IMAGE,
        num_hands=num_hands,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return mp_vision.HandLandmarker.create_from_options(options)


def make_pose_landmarker():
    import os
    model_path = os.path.join(_models_dir(), "pose_landmarker_lite.task")
    base_options = mp_python.BaseOptions(model_asset_path=model_path)
    options = mp_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.IMAGE,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return mp_vision.PoseLandmarker.create_from_options(options)


def detect_hands(landmarker, rgb_frame: np.ndarray):
    """Returns (left_hand, right_hand) as (21,3) arrays or None."""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = landmarker.detect(mp_image)
    left_hand = None
    right_hand = None
    for i, handedness_list in enumerate(result.handedness):
        side = handedness_list[0].category_name.lower()
        lm = result.hand_landmarks[i]
        arr = np.array([[l.x, l.y, l.z] for l in lm], dtype=np.float32)
        if side == "left":
            left_hand = arr
        else:
            right_hand = arr
    return left_hand, right_hand


def detect_pose(landmarker, rgb_frame: np.ndarray):
    """Returns pose as (33,3) array or None."""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = landmarker.detect(mp_image)
    if not result.pose_landmarks:
        return None
    lm = result.pose_landmarks[0]
    return np.array([[l.x, l.y, l.z] for l in lm], dtype=np.float32)


def normalize_body_relative(pose: np.ndarray, left_hand, right_hand) -> np.ndarray:
    """Normalize all landmarks relative to shoulder midpoint and width.
    pose: (33,3), left_hand/right_hand: (21,3) or None
    Returns: (225,) float32
    """
    left_shoulder = pose[11, :3]
    right_shoulder = pose[12, :3]
    origin = (left_shoulder + right_shoulder) / 2.0
    scale = float(np.linalg.norm(left_shoulder - right_shoulder)) + 1e-6

    pose_norm = (pose[:, :3] - origin) / scale

    lh_norm = np.zeros((HAND_COUNT, 3), dtype=np.float32) if left_hand is None else (left_hand[:, :3] - origin) / scale
    rh_norm = np.zeros((HAND_COUNT, 3), dtype=np.float32) if right_hand is None else (right_hand[:, :3] - origin) / scale

    return np.concatenate([pose_norm.flatten(), lh_norm.flatten(), rh_norm.flatten()]).astype(np.float32)


def normalize_hand_relative(hand: np.ndarray) -> np.ndarray:
    """Normalize hand landmarks relative to wrist. Returns (63,) float32."""
    wrist = hand[0, :3]
    scale = float(np.linalg.norm(hand[9, :3] - wrist)) + 1e-6
    return ((hand[:, :3] - wrist) / scale).flatten().astype(np.float32)


def resample_sequence(frames: list, target_len: int = 30) -> np.ndarray:
    """Resample variable-length frame list to exactly target_len."""
    n = len(frames)
    if n == 0:
        return np.zeros((target_len, FEATURE_DIM), dtype=np.float32)
    indices = np.linspace(0, n - 1, target_len)
    return np.array([frames[int(round(i))] for i in indices], dtype=np.float32)
