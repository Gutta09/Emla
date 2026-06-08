"""Train the fingerspell (A-Z) model.

Run: python 4_train_fingerspell.py
Expected: >97% top-1 accuracy on 26 classes (A-Z).
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.dataset_utils import load_split, load_label_map

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models", "fingerspell")


def build_fingerspell_model(num_classes: int = 26) -> tf.keras.Model:
    return tf.keras.Sequential([
        tf.keras.Input(shape=(126,)),
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(num_classes, activation="softmax"),
    ], name="fingerspell_model")


def main():
    print("Loading data...")
    X_train, X_val, y_train, y_val = load_split(PROCESSED_DIR, "fingerspell")
    print(f"  Train: {X_train.shape}, Val: {X_val.shape}")

    label_map = load_label_map(os.path.join(MODELS_DIR, "label_map.json"))
    num_classes = len(label_map)
    print(f"  Classes: {num_classes}")

    model = build_fingerspell_model(num_classes)
    model.summary()

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True, monitor="val_accuracy"),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6, monitor="val_loss"),
        tf.keras.callbacks.ModelCheckpoint(
            os.path.join(MODELS_DIR, "model.keras"),
            save_best_only=True,
            monitor="val_accuracy",
        ),
    ]

    print("\nTraining...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        batch_size=256,
        epochs=100,
        callbacks=callbacks,
        verbose=1,
    )

    best_val_acc = max(history.history["val_accuracy"])
    print(f"\nBest val accuracy: {best_val_acc:.4f}")

    metadata = {
        "model_type": "fingerspell",
        "num_classes": num_classes,
        "input_shape": [126],
        "best_val_accuracy": float(best_val_acc),
        "train_samples": len(X_train),
    }
    with open(os.path.join(MODELS_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model saved to {MODELS_DIR}/model.keras")


if __name__ == "__main__":
    main()
