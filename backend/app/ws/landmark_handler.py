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
    pause_detector = PauseDetector(
        threshold_frames=settings.pause_frames,
        motion_threshold=0.02,
    )
    last_committed: str | None = None

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
                last_committed = None
                continue

            if msg_type == "mode_change":
                frame_buffer.clear()
                pause_detector.reset()
                continue

            if msg_type != "landmarks":
                continue

            frame_id = data.get("frame_id", 0)
            mode = data.get("mode", "word")
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
                continue

            # Word mode needs pose for body-relative normalization
            if mode != "fingerspell" and not has_pose:
                await websocket.send_text(json.dumps({
                    "type": "prediction", "sign": "—", "confidence": 0.0,
                    "top3": [], "uncertain": True, "frame_id": frame_id, "mode": mode,
                    "hint": "Step back so your upper body is visible",
                }))
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
                    prediction = {"type": "prediction", "sign": "?", "confidence": 0.0,
                                  "top3": [], "uncertain": True, "frame_id": frame_id, "mode": mode}
            else:
                if len(frame_buffer) == settings.sequence_length:
                    seq = np.array(frame_buffer)  # (30, 225)
                    if models.word and models.word.is_loaded:
                        prediction = models.word.predict(seq, frame_id)
                    else:
                        prediction = {"type": "prediction", "sign": "?", "confidence": 0.0,
                                      "top3": [], "uncertain": True, "frame_id": frame_id, "mode": mode}

            if prediction is not None:
                prediction["type"] = "prediction"
                await websocket.send_text(json.dumps(prediction))

            # --- Pause / word boundary ---
            if pause_detector.update(body_vec) and prediction:
                sign = prediction.get("sign", "?")
                conf = prediction.get("confidence", 0.0)
                uncertain = prediction.get("uncertain", True)

                # Only commit a confident, non-duplicate sign
                if not uncertain and sign != "?" and sign != last_committed:
                    last_committed = sign
                    await websocket.send_text(json.dumps({
                        "type": "word_committed",
                        "sign": sign,
                        "confidence": conf,
                    }))
                else:
                    last_committed = None  # reset so next different sign commits

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
