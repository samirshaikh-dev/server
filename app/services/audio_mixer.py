import subprocess
from pathlib import Path
from typing import Optional
from app.services.ffmpeg_bin import get_ffmpeg_executable
from app.core.logger import logger


def normalize_voice_audio(input_audio: Path, output_audio: Path, target_lufs: float = -16.0) -> Path:
    """Normalizes voice track loudness to target LUFS using loudnorm filter."""
    ffmpeg_exe = get_ffmpeg_executable()
    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(input_audio),
        "-af", f"loudnorm=I={target_lufs}:TP=-1.0:LRA=11",
        str(output_audio)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_audio


def mix_with_ducking(
    voice_audio: Path,
    bgm_audio: Path,
    output_audio: Path,
    duck_threshold: float = 0.08,
    duck_ratio: float = 4.0,
    bgm_volume: float = 0.25
) -> Path:
    """
    Ducks background music under speech using sidechaincompress filter and mixes down to final audio.
    """
    ffmpeg_exe = get_ffmpeg_executable()
    filter_complex = (
        f"[1:a]volume={bgm_volume}[bgm_init];"
        f"[bgm_init][0:a]sidechaincompress=threshold={duck_threshold}:ratio={duck_ratio}:attack=100:release=400[ducked_bgm];"
        f"[0:a][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
    )

    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(voice_audio),
        "-i", str(bgm_audio),
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-ac", "2",
        "-ar", "48000",
        str(output_audio)
    ]

    logger.info(f"Mixing voice with ducked BGM: {' '.join(cmd)}")
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_audio
