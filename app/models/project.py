from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.models.edit_plan import TargetPlatform, AspectRatio


class JobStatus(str, Enum):
    IDLE = "idle"
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    PLANNING = "planning"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class CreatePlanRequest(BaseModel):
    prompt: str = Field(..., description="Natural language editing instruction")
    platform: TargetPlatform = TargetPlatform.INSTAGRAM_REEL
    aspect_ratio: Optional[AspectRatio] = None
    target_duration: Optional[float] = None
    caption_style: str = "hormozi_bold"
    music_mood: Optional[str] = None
    keywords_to_keep: Optional[str] = None


class ProjectMetadata(BaseModel):
    project_id: str
    filename: str
    duration: float = 0.0
    width: int = 0
    height: int = 0
    fps: float = 30.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: JobStatus = JobStatus.IDLE
    progress_percentage: int = 0
    current_step: str = ""
    error_message: Optional[str] = None
    output_video_path: Optional[str] = None

