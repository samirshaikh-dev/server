from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TargetPlatform(str, Enum):
    INSTAGRAM_REEL = "instagram_reel"
    LINKEDIN_POST = "linkedin_post"
    YOUTUBE_SHORT = "youtube_short"
    CUSTOM = "custom"


class AspectRatio(str, Enum):
    RATIO_9_16 = "9:16"
    RATIO_1_1 = "1:1"
    RATIO_16_9 = "16:9"


class Resolution(BaseModel):
    width: int = 1080
    height: int = 1920


class TimelineCut(BaseModel):
    cut_id: int
    source_start: float = Field(..., description="Start timestamp in raw video (seconds)")
    source_end: float = Field(..., description="End timestamp in raw video (seconds)")
    transition_in: str = Field(default="cut", description="cut, crossfade, dip_to_black")
    zoom_scale: float = Field(default=1.0, description="1.0 = normal, 1.15 = punch-in zoom")
    focus_point: str = Field(default="face_center", description="face_center or frame_center")


class CaptionWord(BaseModel):
    word: str
    start: float = Field(..., description="Timestamp relative to edited timeline (seconds)")
    end: float = Field(..., description="Timestamp relative to edited timeline (seconds)")
    is_highlight: bool = False


class CaptionsConfig(BaseModel):
    enabled: bool = True
    style: str = "hormozi_bold"
    font_family: str = "Montserrat-ExtraBold"
    font_size: int = 64
    primary_color: str = "&H00FFFFFF"     # White (ASS format)
    highlight_color: str = "&H0000FFFF"   # Yellow (ASS format)
    stroke_color: str = "&H00000000"      # Black (ASS format)
    stroke_width: int = 4
    position_y_percent: float = 72.0
    words: List[CaptionWord] = Field(default_factory=list)


class Overlay(BaseModel):
    type: str = Field(..., description="lower_third, keyword_badge, title_card")
    text: str
    start: float
    duration: float
    style_preset: str = "tech_minimal"


class BackgroundMusic(BaseModel):
    enabled: bool = False
    track_id: Optional[str] = None
    volume_db: float = -22.0


class DuckingConfig(BaseModel):
    enabled: bool = True
    duck_volume_db: float = -28.0
    attack_ms: int = 100
    release_ms: int = 350


class AudioConfig(BaseModel):
    clean_speech: bool = True
    speech_loudness_lufs: float = -16.0
    background_music: Optional[BackgroundMusic] = Field(default_factory=BackgroundMusic)
    ducking: Optional[DuckingConfig] = Field(default_factory=DuckingConfig)


class EditPlan(BaseModel):
    project_id: str
    target_platform: TargetPlatform = TargetPlatform.INSTAGRAM_REEL
    aspect_ratio: AspectRatio = AspectRatio.RATIO_9_16
    output_resolution: Resolution = Field(default_factory=Resolution)
    target_duration: Optional[float] = None
    timeline_cuts: List[TimelineCut] = Field(default_factory=list)
    captions: CaptionsConfig = Field(default_factory=CaptionsConfig)
    overlays: List[Overlay] = Field(default_factory=list)
    audio_config: AudioConfig = Field(default_factory=AudioConfig)
