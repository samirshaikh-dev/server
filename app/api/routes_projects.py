import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.logger import logger
from app.models.project import ProjectMetadata, JobStatus, CreatePlanRequest
from app.models.edit_plan import EditPlan
from app.workers.queue import job_queue
from app.services.audio_extractor import extract_audio
from app.services.silence_detector import detect_silence_ffmpeg, invert_silences_to_speech
from app.services.captioner import generate_ass_subtitles
from app.services.planner import generate_edit_plan_llm
from app.services.audio_mixer import normalize_voice_audio
from app.services.compositor import render_project
from app.models.transcript import TranscriptResult, Segment, WordTimestamp

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/upload", response_model=ProjectMetadata)
async def upload_video(file: UploadFile = File(...)):
    """Uploads a raw video file to the project workspace."""
    project_id = str(uuid.uuid4())[:8]
    project_dir = settings.DATA_DIR / "projects" / project_id
    raw_dir = project_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    dest_path = raw_dir / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    metadata = ProjectMetadata(
        project_id=project_id,
        filename=file.filename,
        status=JobStatus.IDLE,
        current_step="Uploaded raw video"
    )
    job_queue.register_project(metadata)
    return metadata


@router.post("/{project_id}/plan", response_model=EditPlan)
async def create_plan(project_id: str, req: CreatePlanRequest):
    """
    Extracts audio, transcribes, and generates structured EditPlan.
    """
    proj = job_queue.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dir = settings.DATA_DIR / "projects" / project_id
    raw_video = next((project_dir / "raw").glob("*"), None)
    if not raw_video:
        raise HTTPException(status_code=400, detail="No video file found in project")

    await job_queue.update_progress(project_id, JobStatus.TRANSCRIBING, 15, "Extracting audio")
    audio_path = project_dir / "audio" / "speech.wav"
    extract_audio(raw_video, audio_path)

    await job_queue.update_progress(project_id, JobStatus.TRANSCRIBING, 30, "Detecting silence & speech boundaries")
    silences = detect_silence_ffmpeg(audio_path)
    speech_ranges = invert_silences_to_speech(silences, total_duration=120.0)

    # Build mock transcript segments from speech ranges for demonstration/local testing
    segments = []
    all_words = []
    for idx, (s, e) in enumerate(speech_ranges):
        seg_text = f"Sample speech segment {idx + 1}"
        words = [
            WordTimestamp(word=w, start=s + (i * 0.3), end=s + ((i + 1) * 0.3))
            for i, w in enumerate(seg_text.split())
        ]
        segments.append(Segment(id=idx, start=s, end=e, text=seg_text, words=words))
        all_words.extend(words)

    transcript = TranscriptResult(
        duration=120.0,
        full_text=" ".join(s.text for s in segments),
        segments=segments,
        words=all_words
    )

    await job_queue.update_progress(project_id, JobStatus.PLANNING, 50, "Generating Edit Plan")
    plan = await generate_edit_plan_llm(
        project_id=project_id,
        prompt=req.prompt,
        transcript=transcript,
        platform=req.platform,
        target_duration=req.target_duration
    )

    # Persist plan to disk
    plan_path = project_dir / "plans" / "edit_plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    await job_queue.update_progress(project_id, JobStatus.IDLE, 60, "Edit Plan Ready")
    return plan


async def run_render_task(project_id: str, edit_plan: EditPlan):
    """Background rendering worker pipeline."""
    try:
        project_dir = settings.DATA_DIR / "projects" / project_id
        raw_video = next((project_dir / "raw").glob("*"), None)
        audio_path = project_dir / "audio" / "speech.wav"

        await job_queue.update_progress(project_id, JobStatus.RENDERING, 65, "Generating subtitle styling")
        ass_path = project_dir / "intermediate" / "captions.ass"
        generate_ass_subtitles(edit_plan.captions, ass_path)

        await job_queue.update_progress(project_id, JobStatus.RENDERING, 75, "Normalizing audio track")
        norm_audio_path = project_dir / "intermediate" / "speech_norm.wav"
        normalize_voice_audio(audio_path, norm_audio_path)

        await job_queue.update_progress(project_id, JobStatus.RENDERING, 85, "Rendering cuts, zooms, & subtitles")
        export_path = project_dir / "exports" / f"{project_id}_final.mp4"
        render_project(
            raw_video_path=raw_video,
            edit_plan=edit_plan,
            ass_subtitle_path=ass_path,
            final_audio_path=norm_audio_path,
            output_video_path=export_path
        )

        proj = job_queue.get_project(project_id)
        if proj:
            proj.output_video_path = str(export_path)

        await job_queue.update_progress(project_id, JobStatus.COMPLETED, 100, "Render completed successfully")
    except Exception as e:
        logger.error(f"Render task failed: {e}", exc_info=True)
        await job_queue.update_progress(project_id, JobStatus.FAILED, 0, f"Error: {str(e)}")


@router.post("/{project_id}/render")
async def trigger_render(project_id: str, plan: EditPlan, bg_tasks: BackgroundTasks):
    """Triggers the video rendering pipeline in background."""
    proj = job_queue.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    bg_tasks.add_task(run_render_task, project_id, plan)
    return {"message": "Rendering job enqueued", "project_id": project_id}


@router.get("/{project_id}", response_model=ProjectMetadata)
async def get_project_status(project_id: str):
    """Retrieves current project metadata and progress status."""
    proj = job_queue.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj


@router.get("/{project_id}/download")
async def download_video(project_id: str):
    """Downloads the finalized MP4 export."""
    project_dir = settings.DATA_DIR / "projects" / project_id
    export_file = next((project_dir / "exports").glob("*.mp4"), None)
    if not export_file or not export_file.is_file():
        raise HTTPException(status_code=404, detail="Rendered video not found")
    return FileResponse(export_file, media_type="video/mp4", filename=export_file.name)

