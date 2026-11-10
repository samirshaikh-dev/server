import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import subprocess
from app.core.config import settings
from app.core.logger import logger
from app.services.ffmpeg_bin import get_ffmpeg_executable
from app.services.audio_extractor import extract_audio
from app.services.silence_detector import detect_silence_ffmpeg, invert_silences_to_speech
from app.services.captioner import generate_ass_subtitles
from app.services.planner import build_deterministic_plan
from app.services.audio_mixer import normalize_voice_audio
from app.services.compositor import render_project
from app.models.transcript import TranscriptResult, Segment, WordTimestamp
from app.models.edit_plan import TargetPlatform


def generate_synthetic_raw_video(output_path: Path, duration: int = 12):
    """
    Generates a 1080p synthetic test video with audio tone for testing.
    """
    ffmpeg_exe = get_ffmpeg_executable()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", f"testsrc=size=1920x1080:rate=30:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        str(output_path)
    ]

    logger.info(f"Generating synthetic test video at: {output_path}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg synthetic video generation failed: {result.stderr}")
    return output_path


def run_demo():
    print("=" * 70)
    print("Running Local AI Video Editor End-to-End Pipeline Demo")
    print("=" * 70)

    demo_dir = settings.DATA_DIR / "projects" / "demo_run"
    demo_raw = demo_dir / "raw" / "raw_sample.mp4"
    demo_audio = demo_dir / "audio" / "speech.wav"
    demo_ass = demo_dir / "intermediate" / "captions.ass"
    demo_norm_audio = demo_dir / "intermediate" / "speech_norm.wav"
    demo_output = demo_dir / "exports" / "final_instagram_reel.mp4"

    # Step 1: Create sample video
    print("\n[1/6] Generating synthetic raw video...")
    generate_synthetic_raw_video(demo_raw)
    print(f"  -> Raw video generated: {demo_raw.name}")

    # Step 2: Extract 16kHz mono WAV
    print("\n[2/6] Extracting 16kHz audio for AI processing...")
    extract_audio(demo_raw, demo_audio)
    print(f"  -> Audio extracted: {demo_audio.name}")

    # Step 3: Detect silences
    print("\n[3/6] Detecting pauses and dead space with FFmpeg silencedetect...")
    silences = detect_silence_ffmpeg(demo_audio, noise_threshold_db=-30.0, min_silence_duration=0.5)
    speech_ranges = invert_silences_to_speech(silences, total_duration=12.0)
    print(f"  -> Detected {len(silences)} silences. Inverted into {len(speech_ranges)} speech chunks:")
    for s_start, s_end in speech_ranges:
        print(f"     * Speech: {s_start:.2f}s -> {s_end:.2f}s ({s_end - s_start:.2f}s)")

    # Step 4: Build transcript & Edit Plan
    print("\n[4/6] Synthesizing Edit Plan with 1.15x punch-in zooms & 9:16 vertical crop...")
    sample_segments = [
        Segment(
            id=0, start=0.0, end=3.0, text="Build local AI video applications.",
            words=[
                WordTimestamp(word="Build", start=0.2, end=0.8),
                WordTimestamp(word="local", start=0.9, end=1.5),
                WordTimestamp(word="AI", start=1.6, end=2.0),
                WordTimestamp(word="applications", start=2.1, end=2.9),
            ]
        ),
        Segment(
            id=1, start=5.0, end=9.0, text="High retention Instagram Reels and LinkedIn clips.",
            words=[
                WordTimestamp(word="High", start=5.1, end=5.8),
                WordTimestamp(word="retention", start=5.9, end=6.7),
                WordTimestamp(word="Instagram", start=6.8, end=7.6),
                WordTimestamp(word="Reels", start=7.7, end=8.7),
            ]
        ),
        Segment(
            id=2, start=10.0, end=12.0, text="Automate your entire editing workflow.",
            words=[
                WordTimestamp(word="Automate", start=10.1, end=10.7),
                WordTimestamp(word="your", start=10.8, end=11.1),
                WordTimestamp(word="workflow", start=11.2, end=11.9),
            ]
        ),
    ]

    transcript = TranscriptResult(
        duration=12.0,
        full_text="Build local AI video applications. High retention Instagram Reels. Automate your workflow.",
        segments=sample_segments,
        words=[w for s in sample_segments for w in s.words]
    )

    plan = build_deterministic_plan(
        project_id="demo_run",
        transcript=transcript,
        platform=TargetPlatform.INSTAGRAM_REEL,
        target_duration=30.0
    )
    print(f"  -> EditPlan generated: {len(plan.timeline_cuts)} cuts, Aspect Ratio: {plan.aspect_ratio.value}")
    for cut in plan.timeline_cuts:
        print(f"     * Cut {cut.cut_id}: {cut.source_start:.2f}s -> {cut.source_end:.2f}s (Zoom: {cut.zoom_scale}x)")

    # Step 5: Generate Hormozi-style ASS captions & normalize audio
    print("\n[5/6] Generating Hormozi ASS captions and normalizing audio to -16 LUFS...")
    generate_ass_subtitles(plan.captions, demo_ass)
    normalize_voice_audio(demo_audio, demo_norm_audio)
    print(f"  -> Subtitles compiled: {demo_ass.name}")
    print(f"  -> Audio normalized: {demo_norm_audio.name}")

    # Step 6: Render final video with FFmpeg
    print("\n[6/6] Executing FFmpeg composite filtergraph (crop 9:16, zoom, burn captions)...")
    render_project(
        raw_video_path=demo_raw,
        edit_plan=plan,
        ass_subtitle_path=demo_ass,
        final_audio_path=demo_norm_audio,
        output_video_path=demo_output
    )

    print("\n" + "=" * 70)
    print(f"SUCCESS! Rendered final MP4 export: {demo_output}")
    print(f"File size: {demo_output.stat().st_size / 1024:.1f} KB")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
