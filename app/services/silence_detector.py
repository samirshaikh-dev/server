import re
import subprocess
from pathlib import Path
from typing import List, Tuple
from app.services.ffmpeg_bin import get_ffmpeg_executable
from app.core.logger import logger

FILLER_WORDS = {
    "um", "uh", "er", "ah", "like", "you know", "i mean", "actually",
    "basically", "sort of", "kind of"
}


def detect_silence_ffmpeg(
    audio_path: Path,
    noise_threshold_db: float = -32.0,
    min_silence_duration: float = 0.4
) -> List[Tuple[float, float]]:
    """
    Detects silent ranges in an audio file using FFmpeg silencedetect filter.
    Returns a list of (silence_start, silence_end) in seconds.
    """
    ffmpeg_exe = get_ffmpeg_executable()
    cmd = [
        ffmpeg_exe,
        "-i", str(audio_path),
        "-af", f"silencedetect=noise={noise_threshold_db}dB:d={min_silence_duration}",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stderr

    silence_ranges = []
    start_pattern = re.compile(r"silence_start:\s*([0-9\.]+)")
    end_pattern = re.compile(r"silence_end:\s*([0-9\.]+)")

    current_start = None
    for line in output.splitlines():
        start_match = start_pattern.search(line)
        if start_match:
            current_start = float(start_match.group(1))

        end_match = end_pattern.search(line)
        if end_match and current_start is not None:
            silence_ranges.append((current_start, float(end_match.group(1))))
            current_start = None

    logger.info(f"Detected {len(silence_ranges)} silence segments in {audio_path.name}")
    return silence_ranges


def invert_silences_to_speech(
    silences: List[Tuple[float, float]],
    total_duration: float,
    padding: float = 0.08
) -> List[Tuple[float, float]]:
    """
    Inverts silence ranges to obtain speech intervals, adding safe padding
    so speech isn't unnaturally cut off at syllable boundaries.
    """
    speech_ranges = []
    current_pos = 0.0

    for s_start, s_end in silences:
        speech_start = max(0.0, current_pos)
        speech_end = min(total_duration, s_start + padding)
        if speech_end - speech_start > 0.3:
            speech_ranges.append((speech_start, speech_end))
        current_pos = max(0.0, s_end - padding)

    if current_pos < total_duration:
        speech_ranges.append((current_pos, total_duration))

    return speech_ranges

