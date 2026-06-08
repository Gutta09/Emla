from typing import Optional
from pydantic import BaseModel


class LandmarkPayload(BaseModel):
    pose: list[list[float]]
    left_hand: Optional[list[list[float]]] = None
    right_hand: Optional[list[list[float]]] = None


class LandmarkMessage(BaseModel):
    type: str = "landmarks"
    frame_id: int
    mode: str = "word"  # "word" | "fingerspell"
    payload: LandmarkPayload


class TopKItem(BaseModel):
    sign: str
    confidence: float


class PredictionMessage(BaseModel):
    type: str = "prediction"
    frame_id: int
    sign: str
    confidence: float
    mode: str
    top3: list[TopKItem]
    uncertain: bool


class WordCommittedMessage(BaseModel):
    type: str = "word_committed"
    sign: str
    confidence: float


class ReadyMessage(BaseModel):
    type: str = "ready"
    vocabulary_size: int
    models_loaded: list[str]
