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
    Calls Google Gemini API (gemini-2.5-flash) to generate a structured edit plan.
    Enforces structured JSON output via response_mime_type.
    """
    if not settings.GEMINI_API_KEY:
        logger.info("GEMINI_API_KEY is not configured. Using deterministic planner.")
        return build_deterministic_plan(project_id, transcript, platform, target_duration)

    system_instruction = (
        "You are an expert short-form video editor for Instagram Reels and LinkedIn. "
        "Analyze the transcript segments with timestamps and user prompt to create a high-retention EditPlan. "
        "Select the strongest hook, cut filler/silences, alternate punch-in zooms (1.15x) for emphasis, "
        "and calculate accurate timeline cut intervals. Return ONLY valid JSON adhering strictly to the EditPlan schema."
    )

    user_payload = {
        "project_id": project_id,
        "user_prompt": prompt,
        "target_platform": platform.value,
        "target_duration": target_duration,
        "transcript_segments": [
            {"id": s.id, "start": s.start, "end": s.end, "text": s.text}
            for s in transcript.segments[:60]
        ]
    }

    gemini_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )

    body = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "parts": [{"text": json.dumps(user_payload)}]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(gemini_url, json=body)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    parsed = json.loads(content_text)
                    if "timeline_cuts" in parsed:
                        logger.info(f"Successfully generated EditPlan via Gemini ({settings.GEMINI_MODEL})")
                        parsed["project_id"] = project_id
                        return EditPlan.model_validate(parsed)
            else:
                logger.error(f"Gemini API returned status {res.status_code}: {res.text}")
    except Exception as e:
        logger.warning(f"Gemini generation error ({e}). Falling back to deterministic plan.")

    return build_deterministic_plan(project_id, transcript, platform, target_duration)

