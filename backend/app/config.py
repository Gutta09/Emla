import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Sentence assembly uses Gemini (Google AI Studio, free tier). Optional —
    # without a key the service falls back to a deterministic join.
    gemini_api_key: str = ""
    port: int = 8000
    frontend_url: str = "http://localhost:5173"
    confidence_threshold: float = 0.45
    pause_frames: int = 15
    sequence_length: int = 30

    @property
    def models_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), "..", "..", "models")


settings = Settings()
