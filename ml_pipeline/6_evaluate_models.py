"""Evaluate trained models and generate confusion matrix plots.

Run: python 6_evaluate_models.py
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.dataset_utils import load_split, load_label_map
from utils.model_architectures import CUSTOM_OBJECTS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")


def evaluate_model(model_dir: str, prefix: str):
    model_path = os.path.join(model_dir, "model.keras")
    if not os.path.exists(model_path):
        print(f"No model found at {model_path}, skipping.")
        return

    print(f"\n=== Evaluating {prefix} model ===")
    model = tf.keras.models.load_model(model_path, custom_objects=CUSTOM_OBJECTS)
    label_map = load_label_map(os.path.join(model_dir, "label_map.json"))
    labels = [label_map[str(i)] for i in range(len(label_map))]

    try:
        X_val, _, y_val, _ = load_split(PROCESSED_DIR, prefix)
        # Actually we want val set:
        X_train, X_val, y_train, y_val = load_split.__wrapped__ if hasattr(load_split, '__wrapped__') else (None, None, None, None)
    except Exception:
        pass

    # Reload properly
    import numpy as np
    X_val = np.load(os.path.join(PROCESSED_DIR, f"{prefix}_val.npy"))
    y_val = np.load(os.path.join(PROCESSED_DIR, f"{prefix}_labels_val.npy"))

    print(f"Val set: {X_val.shape}")
    loss, acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"Val accuracy: {acc:.4f}, Loss: {loss:.4f}")

    y_pred = np.argmax(model.predict(X_val, verbose=0), axis=1)

    # Top-3 accuracy
    probs = model.predict(X_val, verbose=0)
    top3 = np.argsort(probs, axis=1)[:, -3:]
    top3_acc = np.mean([y_val[i] in top3[i] for i in range(len(y_val))])
    print(f"Top-3 accuracy: {top3_acc:.4f}")

    # Classification report
    print("\nClassification Report (top 20 classes):")
    report = classification_report(y_val, y_pred, target_names=labels, output_dict=True)
    # Print top 20 by support
    rows = [(cls, v["precision"], v["recall"], v["f1-score"], int(v["support"]))
            for cls, v in report.items() if cls not in ("accuracy", "macro avg", "weighted avg")]
    rows.sort(key=lambda r: r[4], reverse=True)
    for cls, prec, rec, f1, sup in rows[:20]:
        print(f"  {cls:20s} P={prec:.2f} R={rec:.2f} F1={f1:.2f} N={sup}")

    # Confusion matrix plot (max 26 classes for readability)
    n = min(len(labels), 30)
    cm = confusion_matrix(y_val, y_pred, labels=list(range(n)))
    fig, ax = plt.subplots(figsize=(max(10, n // 2), max(8, n // 2)))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels[:n], rotation=90, fontsize=7)
    ax.set_yticklabels(labels[:n], fontsize=7)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"{prefix} Confusion Matrix (val, {n} classes)")
    plt.colorbar(im)
    plt.tight_layout()
    out_path = os.path.join(model_dir, "confusion_matrix.png")
    plt.savefig(out_path, dpi=100)
    print(f"Confusion matrix saved to {out_path}")
    plt.close()


if __name__ == "__main__":
    evaluate_model(os.path.join(MODELS_DIR, "fingerspell"), "fingerspell")
    evaluate_model(os.path.join(MODELS_DIR, "word_signs"), "word")
