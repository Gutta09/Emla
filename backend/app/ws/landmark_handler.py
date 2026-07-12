import collections
import json
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ml.normalizer import normalize_body_relative, normalize_hands_only
from app.ml.pause_detector import PauseDetector
from app.config import settings

router = APIRouter()


@router.websocket("/ws/landmarks")
async def landmark_websocket(websocket: WebSocket):
    await websocket.accept()

    models = websocket.app.state.models
    frame_buffer: collections.deque = collections.deque(maxlen=settings.sequence_length)
    pause_detector = PauseDetector(confirm_frames=10, cooldown_frames=20)

    # Announce ready state
    await websocket.send_text(json.dumps({
        "type": "ready",
        "vocabulary_size": models.vocabulary_size,
        "models_loaded": models.loaded_names,
    }))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")

            if msg_type == "clear":
                frame_buffer.clear()
                pause_detector.reset()
                continue

            if msg_type == "mode_change":
                frame_buffer.clear()
                pause_detector.reset()
                continue

            if msg_type != "landmarks":
                continue

            frame_id = data.get("frame_id", 0)
            mode = data.get("mode", "fingerspell")
            payload = data.get("payload", {})

            pose = payload.get("pose") or []
            left_hand = payload.get("left_hand")
            right_hand = payload.get("right_hand")

            has_pose = len(pose) >= 33
            has_hands = left_hand is not None or right_hand is not None

            # Fingerspell works without pose — just hands needed
            if mode == "fingerspell" and not has_hands:
                await websocket.send_text(json.dumps({
                    "type": "prediction", "sign": "—", "confidence": 0.0,
                    "top3": [], "uncertain": True, "frame_id": frame_id, "mode": mode,
                    "hint": "Show your hand to the camera",
                }))
                pause_detector.update("—", False)
                continue

            # Word mode needs pose for body-relative normalization
            if mode != "fingerspell" and not has_pose:
                await websocket.send_text(json.dumps({
                    "type": "prediction", "sign": "—", "confidence": 0.0,
                    "top3": [], "uncertain": True, "frame_id": frame_id, "mode": mode,
                    "hint": "Step back so your upper body is visible",
                }))
                pause_detector.update("—", False)
                continue

            # --- Normalize ---
            try:
                if has_pose:
                    body_vec = normalize_body_relative(pose, left_hand, right_hand)
                    frame_buffer.append(body_vec)
            except Exception:
                continue

            # --- Inference ---
            prediction: dict | None = None

            if mode == "fingerspell":
                hand_vec = normalize_hands_only(left_hand, right_hand)
                if models.fingerspell and models.fingerspell.is_loaded:
                    prediction = models.fingerspell.predict(hand_vec, frame_id)
                else:
                    prediction = {"sign": "?", "confidence": 0.0,
                                  "top3": [], "uncertain": True, "frame_id": frame_id, "mode": mode}
            else:
                if len(frame_buffer) == settings.sequence_length:
                    seq = np.array(frame_buffer)
                    if models.word and models.word.is_loaded:
                        prediction = models.word.predict(seq, frame_id)
                    else:
                        prediction = {"sign": "?", "confidence": 0.0,
                                      "top3": [], "uncertain": True, "frame_id": frame_id, "mode": mode}

            if prediction is not None:
                prediction["type"] = "prediction"
                await websocket.send_text(json.dumps(prediction))

                # --- Auto-commit: same confident sign held for N frames ---
                sign = prediction.get("sign", "?")
                uncertain = prediction.get("uncertain", True)
                conf = prediction.get("confidence", 0.0)

                if pause_detector.update(sign, not uncertain):
                    await websocket.send_text(json.dumps({
                        "type": "word_committed",
                        "sign": sign,
                        "confidence": conf,
                    }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
