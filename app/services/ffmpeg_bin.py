import os
import shutil
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.core.logger import logger


def get_ffmpeg_executable() -> str:
    """
    Locates the FFmpeg binary on the host system.
    Searches config override, system PATH, imageio-ffmpeg, and common Windows locations.
    """
    # 1. Config override
    if settings.FFMPEG_PATH and os.path.isfile(settings.FFMPEG_PATH):
        return settings.FFMPEG_PATH

    # 2. System PATH
    system_path = shutil.which("ffmpeg")
    if system_path:
        return system_path

    # 3. imageio-ffmpeg fallback if installed
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.isfile(exe):
            return exe
    except ImportError:
        pass

    # 4. Common Windows default install paths
    common_windows_paths = [
        r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\tools\ffmpeg\bin\ffmpeg.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"),
    ]
    for p in common_windows_paths:
        if os.path.isfile(p):
            return p

    logger.warning("FFmpeg executable not found in PATH or standard directories.")
    return "ffmpeg"


def get_ffprobe_executable() -> str:
    """Locates ffprobe binary, adjacent to ffmpeg if possible."""
    ffmpeg_exe = get_ffmpeg_executable()
    if ffmpeg_exe != "ffmpeg":
        probe_candidate = Path(ffmpeg_exe).parent / "ffprobe.exe"
        if probe_candidate.is_file():
            return str(probe_candidate)

    system_probe = shutil.which("ffprobe")
    if system_probe:
        return system_probe

    return "ffprobe"

