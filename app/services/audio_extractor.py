import subprocess
from pathlib import Path
from app.services.ffmpeg_bin import get_ffmpeg_executable
from app.core.logger import logger


def extract_audio(video_path: Path, output_audio_path: Path) -> Path:
    """
    Extracts 16kHz, mono, 16-bit PCM WAV from a video file.
    This format is optimal for Whisper and VAD.
    """
    ffmpeg_exe = get_ffmpeg_executable()
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio_path)
    ]

    logger.info(f"Extracting audio: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg audio extraction failed: {result.stderr}")
        raise RuntimeError(f"Failed to extract audio from {video_path}: {result.stderr}")

    return output_audio_path
