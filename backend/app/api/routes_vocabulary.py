import os
import json
from fastapi import APIRouter, HTTPException, Request
from app.schemas.api_schemas import VocabularyResponse, SignInfo, ReferenceResponse

router = APIRouter(prefix="/api", tags=["vocabulary"])

_SIGN_DESCRIPTIONS = {
    "HELLO": ("Wave right hand at shoulder height", "B", "outward wave"),
    "THANK_YOU": ("Touch chin with flat hand, move forward", "B", "forward arc"),
    "PLEASE": ("Rub flat hand on chest in circular motion", "B", "circular"),
    "SORRY": ("Rub fist on chest in circular motion", "A", "circular"),
    "YES": ("Nod the fist up and down", "S", "nodding"),
    "NO": ("Extend index and middle fingers, tap thumb", "H", "snap"),
    "HELP": ("Flat hand on fist, lift upward", "A+B", "upward lift"),
    "WATER": ("W handshape tapping chin", "W", "tap chin"),
    "FOOD": ("Bring fingers to mouth", "O", "toward mouth"),
    "LOVE": ("Cross fists over heart", "S", "cross chest"),
}


@router.get("/vocabulary", response_model=VocabularyResponse)
async def get_vocabulary(request: Request):
    models = request.app.state.models
    signs = []

    if models.fingerspell and models.fingerspell.is_loaded:
        for i in range(models.fingerspell.num_classes):
            label = models.fingerspell._label_map.get(i, str(i))
            signs.append(SignInfo(
                id=label,
                label=label,
                category="fingerspell",
                type="static",
                description=f"ASL letter {label}",
            ))

    if models.word and models.word.is_loaded:
        for i in range(models.word.num_classes):
            label = models.word._label_map.get(i, str(i))
            desc_data = _SIGN_DESCRIPTIONS.get(label, (None, None, None))
            signs.append(SignInfo(
                id=label,
                label=label,
                category="word",
                type="dynamic",
                description=desc_data[0],
                handshape=desc_data[1],
            ))

    return VocabularyResponse(total=len(signs), signs=signs)


@router.get("/reference/{sign_id}", response_model=ReferenceResponse)
async def get_reference(sign_id: str):
    sign_id = sign_id.upper()
    desc_data = _SIGN_DESCRIPTIONS.get(sign_id)

    if desc_data:
        return ReferenceResponse(
            sign=sign_id,
            description=desc_data[0],
            handshape=desc_data[1],
            movement=desc_data[2],
            reference_url=f"/reference/{sign_id.lower()}.gif",
        )

    # Fallback for unlisted signs
    return ReferenceResponse(
        sign=sign_id,
        description=f"ASL sign for {sign_id.replace('_', ' ').lower()}",
        reference_url=None,
    )
