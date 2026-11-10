import subprocess
from pathlib import Path
from typing import List
from app.models.edit_plan import EditPlan, AspectRatio
from app.services.ffmpeg_bin import get_ffmpeg_executable
from app.core.logger import logger


def render_project(
    raw_video_path: Path,
    edit_plan: EditPlan,
    ass_subtitle_path: Path,
    final_audio_path: Path,
    output_video_path: Path
) -> Path:
    """
    Renders the complete timeline using FFmpeg filtergraphs:
    - Slices raw video into specified cuts.
    - Applies punch-in zoom transforms (1.15x).
    - Crops/pads to target aspect ratio (9:16 / 1:1).
    - Burns in animated ASS subtitles.
    - Muxes clean ducked audio track.
    """
    ffmpeg_exe = get_ffmpeg_executable()
    output_video_path.parent.mkdir(parents=True, exist_ok=True)

    target_w = edit_plan.output_resolution.width
    target_h = edit_plan.output_resolution.height

    # Build segment inputs and filter_complex chains
    filter_chains = []
    concat_inputs = []

    for idx, cut in enumerate(edit_plan.timeline_cuts):
        dur = cut.source_end - cut.source_start
        seg_tag = f"v{idx}"

        # Trim step
        trim_filter = f"[0:v]trim=start={cut.source_start}:end={cut.source_end},setpts=PTS-STARTPTS"

        # Punch-in zoom if requested
        if cut.zoom_scale > 1.0:
            zoom = cut.zoom_scale
            zoom_filter = f",crop=w=iw/{zoom}:h=ih/{zoom}:x=(iw-iw/{zoom})/2:y=(ih-ih/{zoom})/2"
            trim_filter += zoom_filter

        # Scale and crop to target aspect ratio
        aspect_filter = (
            f",scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
            f"crop={target_w}:{target_h}"
        )
        trim_filter += aspect_filter
        filter_chains.append(f"{trim_filter}[{seg_tag}]")
        concat_inputs.append(f"[{seg_tag}]")

    concat_chain = "".join(concat_inputs) + f"concat=n={len(edit_plan.timeline_cuts)}:v=1:a=0[vconcat]"
    filter_chains.append(concat_chain)

    # Subtitle burn-in
    escaped_sub_path = str(ass_subtitle_path).replace("\\", "/").replace(":", "\\:")
    subtitle_chain = f"[vconcat]subtitles='{escaped_sub_path}'[vfinal]"
    filter_chains.append(subtitle_chain)

    full_filter_complex = ";".join(filter_chains)

    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(raw_video_path),
        "-i", str(final_audio_path),
        "-filter_complex", full_filter_complex,
        "-map", "[vfinal]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_video_path)
    ]

    logger.info(f"Rendering final video: {output_video_path.name}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        logger.error(f"Render failed: {result.stderr}")
        raise RuntimeError(f"FFmpeg rendering failed: {result.stderr}")

    return output_video_path

