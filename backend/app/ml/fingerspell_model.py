import os
import json
import numpy as np
import tensorflow as tf

from app.schemas.ws_protocol import TopKItem


class FingerspellModel:
    def __init__(self, model_dir: str, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold
        self._model: tf.keras.Model | None = None
        self._label_map: dict[str, str] = {}
        self._load(model_dir)

    def _load(self, model_dir: str):
        model_path = os.path.join(model_dir, "model.keras")
        label_path = os.path.join(model_dir, "label_map.json")

        if not os.path.exists(model_path):
            print(f"[FingerspellModel] No model at {model_path}, running in stub mode.")
            return

        self._model = tf.keras.models.load_model(model_path)
        with open(label_path) as f:
            raw = json.load(f)
        self._label_map = {int(k): v for k, v in raw.items()}
        print(f"[FingerspellModel] Loaded {len(self._label_map)} classes from {model_dir}")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def num_classes(self) -> int:
        return len(self._label_map)

    def predict(self, hand_vec: np.ndarray, frame_id: int = 0) -> dict:
        """Predict from a (126,) hand feature vector."""
        if not self.is_loaded:
            return self._stub_result(frame_id)

        probs = self._model.predict(hand_vec[np.newaxis, :], verbose=0)[0]
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
            "mode": "fingerspell",
        }

    def _stub_result(self, frame_id: int) -> dict:
        return {
            "sign": "?",
            "confidence": 0.0,
            "top3": [],
            "uncertain": True,
            "frame_id": frame_id,
            "mode": "fingerspell",
        }
