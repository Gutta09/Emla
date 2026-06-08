from typing import Optional
from pydantic import BaseModel


class TranslateRequest(BaseModel):
    signs: list[str]


class TranslateResponse(BaseModel):
    sentence: str
    signs: list[str]


class SignInfo(BaseModel):
    id: str
    label: str
    category: str = "general"
    type: str = "dynamic"  # "dynamic" | "static"
    description: Optional[str] = None
    handshape: Optional[str] = None


class VocabularyResponse(BaseModel):
    total: int
    signs: list[SignInfo]


class ReferenceResponse(BaseModel):
    sign: str
    description: str
    handshape: Optional[str] = None
    movement: Optional[str] = None
    reference_url: Optional[str] = None


class SessionEntry(BaseModel):
    id: str
    timestamp: str
    start_ms: int
    end_ms: int
    signs: list[str]
    sentence: str
    mode: str


class HistoryResponse(BaseModel):
    sessions: list[SessionEntry]
