import os
import sys
import json
import numpy as np
import tensorflow as tf

# Register custom Keras layers before loading model
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml_pipeline"))
from utils.model_architectures import CUSTOM_OBJECTS  # noqa: F401 — side-effect: registers serializable layers

from app.schemas.ws_protocol import TopKItem


class WordModel:
    def __init__(self, model_dir: str, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold
        self._model: tf.keras.Model | None = None
        self._label_map: dict[int, str] = {}
        self._vocabulary: dict = {}
        self._load(model_dir)

    def _load(self, model_dir: str):
        model_path = os.path.join(model_dir, "model.keras")
        label_path = os.path.join(model_dir, "label_map.json")
        vocab_path = os.path.join(model_dir, "vocabulary.json")

        if not os.path.exists(model_path):
            print(f"[WordModel] No model at {model_path}, running in stub mode.")
            return

        self._model = tf.keras.models.load_model(model_path, custom_objects=CUSTOM_OBJECTS)
        with open(label_path) as f:
            raw = json.load(f)
        self._label_map = {int(k): v for k, v in raw.items()}

        if os.path.exists(vocab_path):
            with open(vocab_path) as f:
                self._vocabulary = json.load(f)

        print(f"[WordModel] Loaded {len(self._label_map)} classes from {model_dir}")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def num_classes(self) -> int:
        return len(self._label_map)

    @property
    def vocabulary(self) -> dict:
        return self._vocabulary

    def predict(self, sequence: np.ndarray, frame_id: int = 0) -> dict:
        """Predict from a (30, 225) landmark sequence."""
        if not self.is_loaded:
            return self._stub_result(frame_id)

        probs = self._model.predict(sequence[np.newaxis, :, :], verbose=0)[0]
        top3_idx = np.argsort(probs)[::-1][:3]
        top3 = [TopKItem(sign=self._label_map.get(i, "?"), confidence=float(probs[i])) for i in top3_idx]

        best_idx = int(top3_idx[0])
        best_conf = float(probs[best_idx])
        sign = self._label_map.get(best_idx, "?")

        return {
            "sign": sign,
            "confidence": best_conf,
            "top3": [t.model_dump() for t in top3],
            "uncertain": best_conf < self.confidence_threshold,
            "frame_id": frame_id,
            "mode": "word",
        }

    def _stub_result(self, frame_id: int) -> dict:
        return {
            "sign": "?",
            "confidence": 0.0,
            "top3": [],
            "uncertain": True,
            "frame_id": frame_id,
            "mode": "word",
        }
