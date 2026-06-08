from fastapi import APIRouter, HTTPException
from app.schemas.api_schemas import HistoryResponse
from app.services import history_service

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=HistoryResponse)
async def get_history():
    return HistoryResponse(sessions=history_service.get_all())


@router.delete("/history/{session_id}")
async def delete_session(session_id: str):
    if not history_service.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": session_id}


@router.delete("/history")
async def clear_history():
    history_service.clear_all()
    return {"cleared": True}
