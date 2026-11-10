from pydantic import BaseModel, Field
from typing import List, Optional


class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float
    probability: float = 1.0


class Segment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    words: List[WordTimestamp] = Field(default_factory=list)
    is_silence: bool = False
    is_filler: bool = False


class TranscriptResult(BaseModel):
    language: str = "en"
    duration: float
    full_text: str
    segments: List[Segment] = Field(default_factory=list)
    words: List[WordTimestamp] = Field(default_factory=list)
