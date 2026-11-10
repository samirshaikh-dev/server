import json
import httpx
from typing import List, Optional
from app.core.config import settings
from app.core.logger import logger
from app.models.edit_plan import (
    EditPlan, TimelineCut, TargetPlatform, AspectRatio, Resolution,
    CaptionsConfig, CaptionWord, AudioConfig
)
from app.models.transcript import TranscriptResult, Segment


def build_deterministic_plan(
    project_id: str,
    transcript: TranscriptResult,
    platform: TargetPlatform,
    target_duration: Optional[float] = None
) -> EditPlan:
    """
    Fallback deterministic planner when LLM is unavailable:
    Removes silences, splits into cuts, alternates subtle punch-in zooms,
    and recalculates caption timestamps relative to edited timeline.
    """
    # 9:16 for Reels/Shorts, 1:1 for LinkedIn, 16:9 custom
    if platform in (TargetPlatform.INSTAGRAM_REEL, TargetPlatform.YOUTUBE_SHORT):
        res = Resolution(width=1080, height=1920)
        ratio = AspectRatio.RATIO_9_16
    elif platform == TargetPlatform.LINKEDIN_POST:
        res = Resolution(width=1080, height=1080)
        ratio = AspectRatio.RATIO_1_1
    else:
        res = Resolution(width=1920, height=1080)
        ratio = AspectRatio.RATIO_16_9

    cuts: List[TimelineCut] = []
    output_time_offset = 0.0
    timeline_words: List[CaptionWord] = []

    # Filter out empty/silent segments
    valid_segments = [s for s in transcript.segments if not s.is_silence and (s.end - s.start) > 0.3]

    for idx, seg in enumerate(valid_segments):
        duration = seg.end - seg.start

        # Check target duration constraint
        if target_duration and (output_time_offset + duration) > target_duration:
            break

        # Punch-in zoom every 3rd cut to maintain visual rhythm
        zoom = 1.15 if (idx % 3 == 1) else 1.0

        cuts.append(TimelineCut(
            cut_id=idx + 1,
            source_start=seg.start,
            source_end=seg.end,
            zoom_scale=zoom,
            focus_point="face_center"
        ))

        # Re-map word timestamps to edited timeline
        for w in seg.words:
            word_dur = w.end - w.start
            word_start = output_time_offset + (w.start - seg.start)
            timeline_words.append(CaptionWord(
                word=w.word,
                start=max(0.0, word_start),
                end=max(0.0, word_start + word_dur),
                is_highlight=(len(w.word) > 5)  # highlight salient words
            ))

        output_time_offset += duration

    return EditPlan(
        project_id=project_id,
        target_platform=platform,
        aspect_ratio=ratio,
        output_resolution=res,
        target_duration=output_time_offset,
        timeline_cuts=cuts,
        captions=CaptionsConfig(words=timeline_words),
        audio_config=AudioConfig()
    )


async def generate_edit_plan_llm(
    project_id: str,
    prompt: str,
    transcript: TranscriptResult,
    platform: TargetPlatform,
    target_duration: Optional[float] = None
) -> EditPlan:
    """
    Calls local Ollama or OpenAI compatible endpoint to generate an edit plan.
    Falls back gracefully to deterministic cuts if the LLM request fails.
    """
    system_instruction = (
        "You are an expert video editor. Analyze the transcript timestamps and generate "
        "a concise cut list removing filler words, pauses, and repetition. "
        "Return strictly valid JSON conforming to the EditPlan schema."
    )

    user_payload = {
        "prompt": prompt,
        "platform": platform.value,
        "target_duration": target_duration,
        "segments": [{"start": s.start, "end": s.end, "text": s.text} for s in transcript.segments[:50]]
    }

    try:
        if settings.LLM_PROVIDER == "ollama":
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": f"{system_instruction}\nInput:\n{json.dumps(user_payload)}",
                        "format": "json",
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    parsed = json.loads(data.get("response", "{}"))
                    if "timeline_cuts" in parsed:
                        logger.info("Successfully generated EditPlan via Ollama")
                        # Validate against EditPlan
                        return EditPlan.model_validate(parsed)
    except Exception as e:
        logger.warning(f"LLM generation failed or unavailable ({e}). Using deterministic planner fallback.")

    return build_deterministic_plan(project_id, transcript, platform, target_duration)
