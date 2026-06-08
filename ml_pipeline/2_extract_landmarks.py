"""Extract MediaPipe landmarks from images (fingerspell) and videos (word signs).

Uses MediaPipe Tasks API (mediapipe 0.10+).
Run: python 2_extract_landmarks.py
Supports resume: saves a checkpoint every CHECKPOINT_INTERVAL videos.
"""

import os
import sys
import json
import numpy as np
import cv2
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.landmark_utils import (
    make_hand_landmarker,
    make_pose_landmarker,
    detect_hands,
    detect_pose,
    normalize_hand_relative,
    normalize_body_relative,
    resample_sequence,
    FEATURE_DIM,
)
from utils.dataset_utils import split_and_save, save_label_map

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "data", "checkpoints")

ASL_TRAIN_DIR = os.path.expanduser(
    "~/.cache/kagglehub/datasets/grassknoted/asl-alphabet/versions/1"
    "/asl_alphabet_train/asl_alphabet_train"
)
WLASL_VIDEO_DIR = os.path.join(BASE_DIR, "data", "raw", "wlasl", "processed", "videos")
WLASL_META_JSON = os.path.join(BASE_DIR, "data", "raw", "wlasl", "processed", "nslt_100.json")
WLASL_CLASS_LIST = os.path.join(BASE_DIR, "data", "raw", "wlasl", "processed", "wlasl_class_list.txt")

SEQUENCE_LENGTH = 30
MAX_IMAGES_PER_LETTER = 500
CHECKPOINT_INTERVAL = 50  # save progress every N videos


def extract_fingerspell():
    """Extract hand landmarks from ASL Alphabet images (A–Z)."""
    # Skip if already done
    if os.path.exists(os.path.join(PROCESSED_DIR, "fingerspell_train.npy")):
        print("Fingerspell data already extracted, skipping.")
        return

    if not os.path.exists(ASL_TRAIN_DIR):
        print(f"ASL Alphabet not found at {ASL_TRAIN_DIR}")
        return

    letters = sorted([
        d for d in os.listdir(ASL_TRAIN_DIR)
        if os.path.isdir(os.path.join(ASL_TRAIN_DIR, d)) and len(d) == 1 and d.isalpha()
    ])
    print(f"Found {len(letters)} letter classes: {letters}")

    label_map = {i: letter.upper() for i, letter in enumerate(letters)}
    os.makedirs(os.path.join(MODELS_DIR, "fingerspell"), exist_ok=True)
    save_label_map(label_map, os.path.join(MODELS_DIR, "fingerspell", "label_map.json"))
    reverse_map = {v: k for k, v in label_map.items()}

    hand_landmarker = make_hand_landmarker(num_hands=2)
    all_X, all_y = [], []
    skipped = 0

    for letter in tqdm(letters, desc="Fingerspell extraction"):
        letter_dir = os.path.join(ASL_TRAIN_DIR, letter)
        label = reverse_map[letter.upper()]
        files = [f for f in os.listdir(letter_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        files = files[:MAX_IMAGES_PER_LETTER]

        for fname in files:
            img = cv2.imread(os.path.join(letter_dir, fname))
            if img is None:
                continue
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            try:
                left_hand, right_hand = detect_hands(hand_landmarker, rgb)
            except Exception:
                skipped += 1
                continue

            if left_hand is None and right_hand is None:
                skipped += 1
                continue

            hand1 = left_hand if left_hand is not None else right_hand
            hand2 = right_hand if (left_hand is not None and right_hand is not None) else np.zeros((21, 3), dtype=np.float32)

            feat = np.concatenate([normalize_hand_relative(hand1), normalize_hand_relative(hand2)])
            all_X.append(feat)
            all_y.append(label)

    hand_landmarker.close()
    print(f"Fingerspell: {len(all_X)} samples, {skipped} skipped")
    X = np.array(all_X, dtype=np.float32)
    y = np.array(all_y, dtype=np.int32)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    split_and_save(X, y, PROCESSED_DIR, "fingerspell")


def extract_wlasl():
    """Extract MediaPipe landmarks from WLASL videos with checkpoint/resume support."""
    if not os.path.exists(WLASL_META_JSON):
        print(f"WLASL metadata not found at {WLASL_META_JSON}")
        return

    # Skip if already fully done
    if os.path.exists(os.path.join(PROCESSED_DIR, "word_train.npy")):
        print("Word sign data already extracted, skipping.")
        return

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = os.path.join(CHECKPOINT_DIR, "wlasl_checkpoint.json")

    class_list = {}
    with open(WLASL_CLASS_LIST) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                class_list[int(parts[0])] = parts[1]

    with open(WLASL_META_JSON) as f:
        meta = json.load(f)

    existing_videos = set(os.path.splitext(fn)[0] for fn in os.listdir(WLASL_VIDEO_DIR))
    video_map = {
        vid_id: info["action"][0]
        for vid_id, info in meta.items()
        if vid_id in existing_videos
    }
    video_items = sorted(video_map.items())  # deterministic order

    present_classes = sorted(set(video_map.values()))
    label_map = {new_idx: class_list[old_idx].upper() for new_idx, old_idx in enumerate(present_classes)}
    old_to_new = {old: new for new, old in enumerate(present_classes)}

    os.makedirs(os.path.join(MODELS_DIR, "word_signs"), exist_ok=True)
    save_label_map(label_map, os.path.join(MODELS_DIR, "word_signs", "label_map.json"))
    vocab = {v: {"id": v, "label": v, "type": "dynamic"} for v in label_map.values()}
    with open(os.path.join(MODELS_DIR, "word_signs", "vocabulary.json"), "w") as f:
        json.dump(vocab, f, indent=2)

    # Load checkpoint if exists
    start_idx = 0
    all_X, all_y = [], []
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            ckpt = json.load(f)
        start_idx = ckpt.get("next_idx", 0)
        X_ckpt = np.load(os.path.join(CHECKPOINT_DIR, "wlasl_X.npy"))
        y_ckpt = np.load(os.path.join(CHECKPOINT_DIR, "wlasl_y.npy"))
        all_X = list(X_ckpt)
        all_y = list(y_ckpt)
        print(f"Resuming from video {start_idx}/{len(video_items)} ({len(all_X)} sequences already saved)")
    else:
        print(f"WLASL: {len(video_items)} videos, {len(present_classes)} classes")
        print("Classes:", list(label_map.values())[:10], "...")

    hand_landmarker = make_hand_landmarker(num_hands=2)
    pose_landmarker = make_pose_landmarker()
    skipped = 0

    remaining = video_items[start_idx:]
    for i, (vid_id, cls_idx) in enumerate(tqdm(remaining, desc="WLASL extraction", initial=start_idx, total=len(video_items))):
        video_path = os.path.join(WLASL_VIDEO_DIR, vid_id + ".mp4")
        cap = cv2.VideoCapture(video_path)
        frames = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            try:
                pose = detect_pose(pose_landmarker, rgb)
                left_hand, right_hand = detect_hands(hand_landmarker, rgb)
            except Exception:
                frames.append(np.zeros(FEATURE_DIM, dtype=np.float32))
                continue

            if pose is None:
                frames.append(np.zeros(FEATURE_DIM, dtype=np.float32))
            else:
                frames.append(normalize_body_relative(pose, left_hand, right_hand))

        cap.release()

        if len(frames) < 5:
            skipped += 1
        else:
            all_X.append(resample_sequence(frames, SEQUENCE_LENGTH))
            all_y.append(old_to_new[cls_idx])

        # Save checkpoint every CHECKPOINT_INTERVAL videos
        global_idx = start_idx + i + 1
        if (i + 1) % CHECKPOINT_INTERVAL == 0:
            np.save(os.path.join(CHECKPOINT_DIR, "wlasl_X.npy"), np.array(all_X, dtype=np.float32))
            np.save(os.path.join(CHECKPOINT_DIR, "wlasl_y.npy"), np.array(all_y, dtype=np.int32))
            with open(checkpoint_file, "w") as f:
                json.dump({"next_idx": global_idx, "sequences": len(all_X)}, f)
            print(f"  [checkpoint] {global_idx}/{len(video_items)} videos, {len(all_X)} sequences saved")

    hand_landmarker.close()
    pose_landmarker.close()
    print(f"WLASL complete: {len(all_X)} sequences, {skipped} skipped")

    X = np.array(all_X, dtype=np.float32)
    y = np.array(all_y, dtype=np.int32)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    split_and_save(X, y, PROCESSED_DIR, "word")

    # Clean up checkpoint
    for fname in ["wlasl_X.npy", "wlasl_y.npy", "wlasl_checkpoint.json"]:
        path = os.path.join(CHECKPOINT_DIR, fname)
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    os.makedirs(os.path.join(MODELS_DIR, "fingerspell"), exist_ok=True)
    os.makedirs(os.path.join(MODELS_DIR, "word_signs"), exist_ok=True)

    print("=== Extracting fingerspell landmarks ===")
    extract_fingerspell()

    print("\n=== Extracting WLASL word sign landmarks ===")
    extract_wlasl()

    print("\nDone. Run 4_train_fingerspell.py next.")
