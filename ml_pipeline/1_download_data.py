"""Download ASL datasets via kagglehub.

Run: python 1_download_data.py
Requires KAGGLE_USERNAME and KAGGLE_KEY env vars, or ~/.kaggle/kaggle.json.
"""

import os
import shutil
import kagglehub

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")


def download_asl_alphabet():
    print("Downloading ASL Alphabet dataset...")
    path = kagglehub.dataset_download("grassknoted/asl-alphabet")
    dest = os.path.join(RAW_DIR, "asl_alphabet")
    if not os.path.exists(dest):
        shutil.copytree(path, dest)
    print(f"  Saved to: {dest}")
    return dest


def download_wlasl_processed():
    print("Downloading WLASL pre-processed landmarks...")
    try:
        path = kagglehub.dataset_download("risangbaskoro/wlasl-processed")
        dest = os.path.join(RAW_DIR, "wlasl", "processed")
        if not os.path.exists(dest):
            shutil.copytree(path, dest)
        print(f"  Saved to: {dest}")
        return dest
    except Exception as e:
        print(f"  WLASL processed not available ({e}), will fall back to video dataset.")
        return None


def download_wlasl_videos():
    print("Downloading WLASL resized videos (fallback)...")
    path = kagglehub.dataset_download("sttaseen/wlasl2000-resized")
    dest = os.path.join(RAW_DIR, "wlasl", "videos")
    if not os.path.exists(dest):
        shutil.copytree(path, dest)
    print(f"  Saved to: {dest}")
    return dest


if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    download_asl_alphabet()
    result = download_wlasl_processed()
    if result is None:
        download_wlasl_videos()
    print("\nDownload complete. Run 2_extract_landmarks.py next.")
