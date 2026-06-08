from fastapi import APIRouter
from app.schemas.api_schemas import TranslateRequest, TranslateResponse
from app.services.claude_service import signs_to_sentence
from app.services import history_service
import time

router = APIRouter(prefix="/api", tags=["translate"])


@router.post("/translate", response_model=TranslateResponse)
async def translate_signs(req: TranslateRequest):
    start_ms = int(time.time() * 1000)
    sentence = await signs_to_sentence(req.signs)
    end_ms = int(time.time() * 1000)

    history_service.add_session(
        signs=req.signs,
        sentence=sentence,
        mode="word",
        start_ms=start_ms,
        end_ms=end_ms,
    )

    return TranslateResponse(sentence=sentence, signs=req.signs)
