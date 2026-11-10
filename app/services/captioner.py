from pathlib import Path
from typing import List
from app.models.edit_plan import CaptionsConfig, CaptionWord


def format_ass_time(seconds: float) -> str:
    """Formats seconds into ASS timestamp: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"


def generate_ass_subtitles(
    captions_config: CaptionsConfig,
    output_ass_path: Path,
    words_per_batch: int = 3
) -> Path:
    """
    Generates an Advanced SubStation Alpha (.ass) subtitle file.
    Creates modern high-retention captions (Hormozi style) with word-by-word
    highlighting and strong outlines for mobile display.
    """
    output_ass_path.parent.mkdir(parents=True, exist_ok=True)
    words = captions_config.words

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{captions_config.font_family},{captions_config.font_size},{captions_config.primary_color},&H000000FF,{captions_config.stroke_color},&H80000000,-1,0,0,0,100,100,0,0,1,{captions_config.stroke_width},0,2,30,30,{int(1920 * (1 - captions_config.position_y_percent / 100))},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []

    # Group words into short 2-4 word batches so viewers read fast without visual clutter
    for i in range(0, len(words), words_per_batch):
        chunk = words[i:i + words_per_batch]
        if not chunk:
            continue

        for current_idx, current_word in enumerate(chunk):
            start_str = format_ass_time(current_word.start)
            end_str = format_ass_time(current_word.end)

            # Build line text highlighting current active word in yellow
            line_parts = []
            for idx, w in enumerate(chunk):
                clean_text = w.word.strip().upper()
                if idx == current_idx:
                    # Highlight color (yellow) + slight size emphasis
                    line_parts.append(r"{\c" + captions_config.highlight_color + r"}" + clean_text + r"{\c" + captions_config.primary_color + r"}")
                else:
                    line_parts.append(clean_text)

            line_text = " ".join(line_parts)
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")

    full_content = header + "\n".join(events) + "\n"
    output_ass_path.write_text(full_content, encoding="utf-8")
    return output_ass_path

