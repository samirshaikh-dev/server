from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Storage paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # Gemini AI settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Whisper
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "auto"
    WHISPER_COMPUTE_TYPE: str = "auto"

    # Custom FFmpeg binary path
    FFMPEG_PATH: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Ensure base runtime data directories exist
(settings.DATA_DIR / "projects").mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "assets" / "music").mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "assets" / "sfx").mkdir(parents=True, exist_ok=True)

