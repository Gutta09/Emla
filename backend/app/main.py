from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.ml.model_manager import ModelManager
from app.ws.landmark_handler import router as ws_router
from app.api.routes_translate import router as translate_router
from app.api.routes_vocabulary import router as vocabulary_router
from app.api.routes_history import router as history_router
from app.api.routes_feedback import router as feedback_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models = ModelManager()
    app.state.models.load_all()
    yield


app = FastAPI(
    title="Emla API",
    description="ASL Sign Language Recognition backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)
app.include_router(translate_router)
app.include_router(vocabulary_router)
app.include_router(history_router)
app.include_router(feedback_router)

# Serve reference sign assets if they exist
reference_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "reference")
if os.path.exists(reference_dir):
    app.mount("/reference", StaticFiles(directory=reference_dir), name="reference")


@app.get("/health")
async def health():
    models = app.state.models
    return {
        "status": "ok",
        "models": models.loaded_names,
        "vocabulary_size": models.vocabulary_size,
    }
