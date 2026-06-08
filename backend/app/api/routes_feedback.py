"""POST /api/feedback — save unknown landmark sequences with user labels for retraining."""

import os
import json
import time
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

FEEDBACK_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "feedback"
)
os.makedirs(FEEDBACK_DIR, exist_ok=True)

INDEX_FILE = os.path.join(FEEDBACK_DIR, "index.json")


def _load_index() -> list:
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE) as f:
            return json.load(f)
    return []


def _save_index(index: list):
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


class FeedbackRequest(BaseModel):
    label: str                          # user-provided sign name
    mode: str                           # "word" or "fingerspell"
    sequence: list[list[float]]         # (30, 225) for word or (126,) wrapped in list for fingerspell
    confidence: float = 0.0
    model_guess: str = "?"


@router.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest):
    label = req.label.strip().upper()
    if not label:
        raise HTTPException(status_code=400, detail="Label cannot be empty")

    timestamp = int(time.time() * 1000)
    fname = f"{label}_{req.mode}_{timestamp}.npy"
    fpath = os.path.join(FEEDBACK_DIR, fname)

    arr = np.array(req.sequence, dtype=np.float32)
    np.save(fpath, arr)

    index = _load_index()
    index.append({
        "file": fname,
        "label": label,
        "mode": req.mode,
        "timestamp": timestamp,
        "model_guess": req.model_guess,
        "confidence": req.confidence,
    })
    _save_index(index)

    return {"saved": True, "label": label, "total_feedback": len(index)}


@router.get("/api/feedback/stats")
async def feedback_stats():
    index = _load_index()
    counts: dict[str, int] = {}
    for entry in index:
        counts[entry["label"]] = counts.get(entry["label"], 0) + 1
    return {"total": len(index), "by_label": counts}
