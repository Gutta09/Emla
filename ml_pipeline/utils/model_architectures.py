"""Shared custom Keras layers used by training, evaluation, and backend inference."""

import numpy as np
import tensorflow as tf
import keras


def get_positional_encoding(seq_len: int, d_model: int) -> np.ndarray:
    positions = np.arange(seq_len)[:, np.newaxis]
    dims = np.arange(d_model)[np.newaxis, :]
    angles = positions / np.power(10000, (2 * (dims // 2)) / d_model)
    angles[:, 0::2] = np.sin(angles[:, 0::2])
    angles[:, 1::2] = np.cos(angles[:, 1::2])
    return angles.astype(np.float32)


@keras.saving.register_keras_serializable(package="emla")
class PositionalEncoding(tf.keras.layers.Layer):
    def __init__(self, seq_len: int, d_model: int, **kwargs):
        super().__init__(**kwargs)
        self.seq_len = seq_len
        self.d_model = d_model
        self.pos_enc = tf.constant(get_positional_encoding(seq_len, d_model))

    def call(self, x):
        return x + self.pos_enc

    def get_config(self):
        config = super().get_config()
        config.update({"seq_len": self.seq_len, "d_model": self.d_model})
        return config


@keras.saving.register_keras_serializable(package="emla")
class TransformerBlock(tf.keras.layers.Layer):
    def __init__(self, d_model: int, num_heads: int, dff: int, dropout: float = 0.1, **kwargs):
        super().__init__(**kwargs)
        self.d_model = d_model
        self.num_heads = num_heads
        self.dff = dff
        self.dropout_rate = dropout
        self.attn = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=d_model // num_heads, dropout=dropout)
        self.ff1 = tf.keras.layers.Dense(dff, activation="relu")
        self.ff2 = tf.keras.layers.Dense(d_model)
        self.norm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.norm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.drop1 = tf.keras.layers.Dropout(dropout)
        self.drop2 = tf.keras.layers.Dropout(dropout)

    def call(self, x, training=False):
        attn_out = self.attn(x, x, training=training)
        x = self.norm1(x + self.drop1(attn_out, training=training))
        ff_out = self.ff2(self.ff1(x))
        x = self.norm2(x + self.drop2(ff_out, training=training))
        return x

    def get_config(self):
        config = super().get_config()
        config.update({"d_model": self.d_model, "num_heads": self.num_heads,
                        "dff": self.dff, "dropout": self.dropout_rate})
        return config


CUSTOM_OBJECTS = {"PositionalEncoding": PositionalEncoding, "TransformerBlock": TransformerBlock}


def load_word_model(model_path: str):
    """Load word sign model with custom layer registration."""
    return tf.keras.models.load_model(model_path, custom_objects=CUSTOM_OBJECTS)
