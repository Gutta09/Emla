"""Train the dynamic word-sign Transformer model.

Run: python 5_train_word_model.py
Expected: 70-85% top-1 accuracy on 100 classes (WLASL).
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.dataset_utils import load_split, load_label_map
from utils.augmentation import augment_sequence, generate_augmented_dataset
from utils.model_architectures import PositionalEncoding, TransformerBlock, get_positional_encoding  # registers serializable decorators

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models", "word_signs")

SEQUENCE_LENGTH = 30
FEATURE_DIM = 225
D_MODEL = 128


# PositionalEncoding and TransformerBlock imported from utils.model_architectures above


def build_word_model(num_classes: int, seq_len: int = SEQUENCE_LENGTH, feature_dim: int = FEATURE_DIM) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(seq_len, feature_dim), name="sequence_input")
    x = tf.keras.layers.Dense(D_MODEL, name="projection")(inputs)
    x = PositionalEncoding(seq_len, D_MODEL, name="pos_encoding")(x)
    x = TransformerBlock(D_MODEL, num_heads=4, dff=256, dropout=0.1, name="transformer_1")(x)
    x = TransformerBlock(D_MODEL, num_heads=4, dff=256, dropout=0.1, name="transformer_2")(x)
    x = tf.keras.layers.GlobalAveragePooling1D(name="gap")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(64, activation="gelu", name="fc")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="output")(x)
    return tf.keras.Model(inputs, outputs, name="word_sign_transformer")


class AugmentedDataGenerator(tf.keras.utils.Sequence):
    def __init__(self, X: np.ndarray, y: np.ndarray, batch_size: int = 32, augment: bool = True):
        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.augment = augment
        self.indices = np.arange(len(X))

    def __len__(self):
        return int(np.ceil(len(self.X) / self.batch_size))

    def __getitem__(self, idx):
        batch_idx = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        X_batch = self.X[batch_idx].copy()
        y_batch = self.y[batch_idx]
        if self.augment:
            X_batch = np.array([augment_sequence(seq) for seq in X_batch])
        return X_batch, y_batch

    def on_epoch_end(self):
        np.random.shuffle(self.indices)


def main():
    print("Loading data...")
    X_train, X_val, y_train, y_val = load_split(PROCESSED_DIR, "word")
    print(f"  Raw train: {X_train.shape}, Val: {X_val.shape}")

    # Oversample each class to 80 samples via heavy augmentation
    print("  Augmenting training data to 80 samples per class...")
    X_train, y_train = generate_augmented_dataset(X_train, y_train, target_per_class=80)
    # Shuffle
    perm = np.random.permutation(len(X_train))
    X_train, y_train = X_train[perm], y_train[perm]
    print(f"  Augmented train: {X_train.shape}")

    label_map = load_label_map(os.path.join(MODELS_DIR, "label_map.json"))
    num_classes = len(label_map)
    print(f"  Classes: {num_classes}")

    model = build_word_model(num_classes)
    model.summary()

    model.compile(
        optimizer=tf.keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=1e-4),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    train_gen = AugmentedDataGenerator(X_train, y_train, batch_size=32, augment=True)
    val_gen = AugmentedDataGenerator(X_val, y_val, batch_size=32, augment=False)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=15, restore_best_weights=True, monitor="val_accuracy"),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=7, min_lr=1e-6, monitor="val_loss"),
        tf.keras.callbacks.ModelCheckpoint(
            os.path.join(MODELS_DIR, "model.keras"),
            save_best_only=True,
            monitor="val_accuracy",
        ),
    ]

    print("\nTraining...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=150,
        callbacks=callbacks,
        verbose=1,
    )

    best_val_acc = max(history.history["val_accuracy"])
    print(f"\nBest val accuracy: {best_val_acc:.4f}")

    metadata = {
        "model_type": "word_signs",
        "num_classes": num_classes,
        "input_shape": [SEQUENCE_LENGTH, FEATURE_DIM],
        "best_val_accuracy": float(best_val_acc),
        "train_samples": len(X_train),
        "d_model": D_MODEL,
        "transformer_blocks": 2,
        "attention_heads": 4,
    }
    with open(os.path.join(MODELS_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Save vocabulary.json for the API
    vocab = {v: {"id": v, "label": v, "type": "dynamic"} for v in label_map.values()}
    with open(os.path.join(MODELS_DIR, "vocabulary.json"), "w") as f:
        json.dump(vocab, f, indent=2)

    print(f"Model saved to {MODELS_DIR}/model.keras")


if __name__ == "__main__":
    main()
