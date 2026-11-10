from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.services.ffmpeg_bin import get_ffmpeg_executable

app = FastAPI(
    title="AI Video Studio Backend",
    description="Local-first AI video editing backend for Instagram Reels, LinkedIn videos, and YouTube Shorts.",
    version="0.1.0",
)

# Enable CORS for local Next.js frontend (default http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "ffmpeg_bin": get_ffmpeg_executable(),
        "data_dir": str(settings.DATA_DIR),
        "llm_provider": settings.LLM_PROVIDER,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.py:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

