import os
import json
import numpy as np
from sklearn.model_selection import train_test_split


def save_label_map(label_map: dict, path: str):
    with open(path, "w") as f:
        json.dump(label_map, f, indent=2)


def load_label_map(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def split_and_save(X: np.ndarray, y: np.ndarray, out_dir: str, prefix: str, val_size=0.15):
    os.makedirs(out_dir, exist_ok=True)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=val_size, stratify=y, random_state=42
    )
    np.save(os.path.join(out_dir, f"{prefix}_train.npy"), X_train)
    np.save(os.path.join(out_dir, f"{prefix}_val.npy"), X_val)
    np.save(os.path.join(out_dir, f"{prefix}_labels_train.npy"), y_train)
    np.save(os.path.join(out_dir, f"{prefix}_labels_val.npy"), y_val)
    print(f"Saved {prefix}: train={len(X_train)}, val={len(X_val)}")
    return X_train, X_val, y_train, y_val


def load_split(out_dir: str, prefix: str):
    X_train = np.load(os.path.join(out_dir, f"{prefix}_train.npy"))
    X_val = np.load(os.path.join(out_dir, f"{prefix}_val.npy"))
    y_train = np.load(os.path.join(out_dir, f"{prefix}_labels_train.npy"))
    y_val = np.load(os.path.join(out_dir, f"{prefix}_labels_val.npy"))
    return X_train, X_val, y_train, y_val
