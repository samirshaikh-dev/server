# AI Video Studio — R&D & Implementation Plan

**Owner:** Samir (solo software engineer, non-video-editor)
**Goal:** A local-only tool that turns raw talking-head videos into polished Instagram Reels / LinkedIn / YouTube Shorts videos.
**Status of codebase:** A working backend skeleton already exists (FastAPI + SSE + FFmpeg services + Pydantic models). This plan covers both the R&D decisions and the build-out, and flags real bugs found in the current code.

---

## 1. Current State & Gap Analysis

What already works (in this repo):

| Piece | File | State |
|---|---|---|
| FastAPI app, CORS, health | `main.py` | ✅ Works |
| Upload / plan / render / progress / download endpoints | `app/api/routes_projects.py`, `routes_progress.py` | ✅ Works |
| Pydantic models (`EditPlan`, `TranscriptResult`, `ProjectMetadata`) | `app/models/` | ✅ Works (needs v2 extension) |
| FFmpeg silence detection | `app/services/silence_detector.py` | ✅ Works |
| ASS caption generator (Hormozi-style karaoke) | `app/services/captioner.py` | ✅ Works |
| Loudness normalization + sidechain ducking | `app/services/audio_mixer.py` | ✅ Works |
| Cut/zoom/crop/subtitle compositor | `app/services/compositor.py` | ⚠️ Works but has sync bug (below) |
| LLM planner (Ollama) + deterministic fallback | `app/services/planner.py` | ⚠️ Skeleton; prompt protocol too loose |
| In-process job queue + SSE broadcast | `app/workers/queue.py` | ✅ Works |

**Critical gaps / bugs to fix first (Week 1):**

1. **Mock transcript** — `routes_projects.py` builds fake "Sample speech segment N" segments instead of running a real transcription. `faster-whisper` is in `requirements.txt` but never called. No transcriber service exists.
2. **Hardcoded duration** — `invert_silences_to_speech(silences, total_duration=120.0)` uses a fixed 120 s. Must come from `ffprobe`.
3. **A/V desync bug** — `run_render_task` muxes the *full-length* normalized audio (`speech_norm.wav`) against *cut* video. Audio content does not match the cuts. Audio must be trimmed with the exact same cut list (`atrim`/`asetpts` + `concat`) in the same FFmpeg invocation.
4. **Filler words defined but unused** — `FILLER_WORDS` set exists in `silence_detector.py` but nothing consumes it.
5. **Overlays never rendered** — `Overlay` model exists (`title_card`, `keyword_badge`, `lower_third`) but the compositor ignores them.
6. **Music never mixed into the render** — `mix_with_ducking()` exists but the render task calls only `normalize_voice_audio()`.
7. **No face-aware reframing** — center crop only; `mediapipe`/`opencv` in requirements but unused.
8. **No filename sanitization on upload**; no `ffprobe` validation of codec/fps/_duration.
9. **Zoom is a static crop, transitions are modeled but not implemented** (no crossfade/dip).

---

## 2. Goals & Non-Goals

**Goals (MVP → v1)**
- Single user, single machine, browser UI at `localhost`.
- Raw talking-head MP4 in → platform-correct, captioned, punchy short video out.
- Natural-language prompt drives the edit; strict JSON edit plan is the single source of truth.
- Every intermediate artifact (transcript, plan, cuts, ASS, overlays) persisted to disk for debugging and manual re-runs.

**Non-goals (explicitly out of scope)**
- Cloud deployment, multi-user, auth, payments.
- Collaborative / visual timeline editor.
- Generic video editing (B-roll matching, multi-cam, color grading suites).
- Perfection on the first render — iterate via prompt + plan preview.

---

## 3. Architecture — Simplest Possible Local-First MVP

```
┌─────────────────────────┐        ┌──────────────────────────────────────┐
│  Next.js (web/)         │        │  FastAPI backend (app/)               │
│  - upload dropzone      │  HTTP  │  /api/projects/upload                 │
│  - platform + prompt    │ ────►  │  /api/projects/{id}/plan   (POST)     │
│  - constraints form     │        │  /api/projects/{id}/render (POST)     │
│  - SSE progress bar     │ ◄SSE── │  /api/projects/{id}/progress          │
│  - preview + download   │        │  /api/projects/{id}/download          │
└─────────────────────────┘        │           │                           │
                                   │           ▼                           │
                                   │  LocalJobQueue (asyncio, 1 job at a   │
                                   │  time) → pipeline stages:              │
                                   │   probe → extract → transcribe →      │
                                   │   analyze → plan → render → validate  │
                                   │           │                           │
                                   │           ▼                           │
                                   │  faster-whisper │ FFmpeg │ MediaPipe │
                                   │  (local)        │ (local) │ (local)   │
                                   │  Ollama (optional, for plan LLM)      │
                                   └──────────────────────────────────────┘
                                   All data: ./data/projects/{id}/
```

### 3.1 Why no Redis / Celery in the MVP (and the upgrade path)

You are one user on one machine rendering one video at a time. Every extra daemon (redis-server, Celery worker, flower) is another thing that breaks on Windows. Decision matrix:

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| FastAPI `BackgroundTasks` + asyncio queue (current) | Zero infra, already built, SSE works | Blocks the event loop if stages aren't careful; no persistence across restart | **MVP choice** (fix by running FFmpeg via `subprocess` + thread executor) |
| **RQ + Redis** | Real queue, retries, worker isolation, progress survives restart | Redis isn't native on Windows (needs Memurai / WSL / Docker); two processes to manage | **v1.1 upgrade** if renders ever block the API or you want crash recovery |
| Celery | Industry standard, rich features | Celery ≥4 officially dropped Windows support; heavy config for one user | Skip |

**RQ upgrade design (when needed):** `app/workers/rq_worker.py` (`rq Worker render-queue`), jobs = `render_job(project_id, plan_json)`, progress published to Redis key `progress:{project_id}` (JSON hash, TTL 24 h), SSE endpoint reads the key every 500 ms instead of the in-memory queue. The pipeline code itself does not change — only the scheduler wrapper. Keep this behind the `job_queue` interface so the swap is ~1 file.

### 3.2 Process & progress model

- One render at a time (semaphore). Queue further requests; SSE reports `queued`.
- Every pipeline stage reports `(stage_name, percent, message)` through `job_queue.update_progress` — already implemented; extend stage list.
- FFmpeg progress: run with `-progress pipe:1 -nostats` and parse `out_time_ms` to give real percent within the render stage.
- Run blocking FFmpeg/whisper calls via `asyncio.to_thread(...)` so SSE keeps flowing.

---

## 4. Backend Design (Python-first, FastAPI)

### 4.1 Module map (target state)

```
app/
├── api/
│   ├── router.py                 # mounts routers
│   ├── routes_projects.py        # upload, plan, render, status, download
│   └── routes_progress.py       # SSE stream
├── core/
│   ├── config.py                # Settings (exists)
│   ├── logger.py                # (exists)
│   └── ffmpeg.py                # ffprobe helpers: duration, streams, validate
├── models/
│   ├── edit_plan.py             # EditPlan v2 (extend — see §7)
│   ├── transcript.py            # (exists)
│   └── project.py               # (exists)
├── services/
│   ├── ffmpeg_bin.py            # (exists) locate ffmpeg
│   ├── prober.py                # NEW: ffprobe duration/codec/fps validation
│   ├── audio_extractor.py       # (exists) extract 16k mono wav + 48k wav
│   ├── transcriber.py           # NEW: faster-whisper → TranscriptResult
│   ├── analysis.py              # NEW: filler detect, takes, scoring, keep-ranges
│   ├── planner.py               # EXTEND: constraint extraction + LLM select (§6)
│   ├── captioner.py             # (exists) ASS karaoke captions
│   ├── framer.py                # NEW: MediaPipe face → per-cut crop boxes
│   ├── overlays.py              # NEW: Pillow → title cards / popups / lower-thirds PNGs
│   ├── audio_mixer.py           # (exists) loudnorm + ducking + SFX mix
│   └── compositor.py            # REWRITE: one-pass A/V cut + zoom + reframe +
│                                #   overlay + subtitle + mux (§8, §9)
├── pipeline/
│   └── runner.py                # NEW: stage orchestration + progress reporting
└── workers/
    └── queue.py                 # (exists) LocalJobQueue; RQ adapter later
```

### 4.2 API surface

Existing endpoints are correct; additions:

| Endpoint | Purpose |
|---|---|
| `GET /api/projects` | List projects (for a simple history view in the UI) |
| `GET /api/projects/{id}/plan` | Fetch last persisted plan (for re-render without re-planning) |
| `POST /api/projects/{id}/plan` | Body gains: `caption_style`, `tone`, `music_mood`, `keywords[]`, `keep_sections[]` (all optional) |
| `GET /api/projects/{id}/transcript` | Debug/verification view of word timestamps |
| `POST /api/projects/{id}/cancel` | Kill in-flight FFmpeg (track `subprocess.Popen` handle) |

### 4.3 Config additions (`core/config.py`)

```python
WHISPER_MODEL: str = "small"          # base → small → medium quality ladder
WHISPER_DEVICE: str = "auto"          # cuda / cpu
VAD_THRESHOLD: float = 0.35
MIN_CUT_SECONDS: float = 0.8         # don't create sub-second cuts (except filler)
MAX_OUTPUT_SECONDS: float = 180.0
SFX_ENABLED: bool = True
MUSIC_LIBRARY_DIR / SFX_LIBRARY_DIR  # default under data/assets/
```

---

## 5. Transcription (faster-whisper, word-level)

`app/services/transcriber.py` (new):

```python
from faster_whisper import WhisperModel

def transcribe(audio_path: Path, settings) -> TranscriptResult:
    model = WhisperModel(settings.WHISPER_MODEL,
                         device=settings.WHISPER_DEVICE,
                         compute_type=settings.WHISPER_COMPUTE_TYPE)
    segments, info = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        vad_filter=True,           # silero VAD built in — skips music/noise
        vad_parameters={"min_silence_duration_ms": 400},
        beam_size=5,
    )
    # map to TranscriptResult: segments[] with words[{word, start, end, probability}]
```

Key decisions:
- **Model ladder with fallback:** try configured model; on CUDA OOM or missing wheels, fall back `medium → small → base` and log. `base` on CPU transcribes ~0.5× realtime — a 5-min video ≈ 8–10 min. Recommend `small` (good word-timing accuracy) as default; `medium` if you have ≥8 GB VRAM.
- **`vad_filter=True`** gives cleaner word timestamps than raw whisper and aligns with silence removal (§9.1).
- **Keep `probability`** per word — words below 0.5 get flagged in the plan review UI (trust, but verify).
- Persist `transcripts/transcript.json` (full fidelity, machine-readable) **and** `transcript.srt` (human-readable diff/diff-check).
- Accent/dialect: if your English is non-native, test `small` vs `medium` on one real video in Week 1 and pick empirically.

---

## 6. Natural-Language Prompt → Strict JSON Edit Plan

**Core reliability principle: the LLM never invents timestamps.** It only selects and labels segment IDs from the transcript. All numbers, durations, and caption timings are computed deterministically by Python. This makes bad LLM output recoverable and the plan always physically valid.

### 6.1 Two-stage design

```
User prompt ("Make a punchy 40s reel about pricing, keep the story about
 the client call, Hormozi captions, upbeat music")
        │
        ▼
Stage 1 — DETERMINISTIC constraint extraction (regex/keyword rules, no LLM)
        │  target_duration=40s, style=hormozi_bold, music_mood=upbeat,
        │  must_include="client call" (fuzzy phrase match → segment ids)
        ▼
Stage 2 — LLM SEGMENT SELECTION (Ollama local, optional)
        │  Input: numbered segment list (id, text, duration, heuristic scores)
        │  Output: STRICT JSON → { keep_ids: [...], hook_id, title, overlays: [...] }
        ▼
Stage 3 — CODE ASSEMBLY (Python, always runs)
        │  Cuts + captions + zoom rhythm from keep_ids + constraints
        │  Pydantic validation → repair loop → deterministic fallback
        ▼
Validated EditPlan JSON (persisted to plans/edit_plan.json)
```

### 6.2 Stage 1 — constraint extraction rules (deterministic)

| Constraint | Example phrases | Rule |
|---|---|---|
| Duration | "under 45 s", "45 seconds", "1 minute", "half a minute" | regex → seconds, clamp 10–180 |
| Platform | "reel", "instagram", "linkedin", "youtube", "short" | maps to aspect preset |
| Caption style | "hormozi", "bold", "minimal", "clean", "no captions" | style presets |
| Tone | "punchy", "calm", "professional", "energetic" | → cut density, zoom frequency |
| Music mood | "upbeat", "chill", "corporate", "no music" | → music library tag |
| Keep sections | "keep the part about X", "keep from '...' to '...'" | fuzzy match (`difflib`) phrase → segment ids |
| Keywords | "highlight pricing, ROI" | → highlight words + scoring boost |

### 6.3 Stage 2 — LLM selection protocol

System prompt (kept short, structured, force JSON):

```
You are a short-form video editor. You receive a numbered transcript
segment list with durations and relevance scores for the user's goal.
Select the segments that best serve the user's request, ordered as they
should appear. Choose the strongest hook segment first.
Respond ONLY with JSON matching:
{"keep_ids": [int], "hook_id": int, "title": str,
 "overlays": [{"segment_id": int, "type": "title_card|keyword_badge|lower_third",
               "text": str}]}
Rules: total duration of keep_ids must fit target_duration.
Never invent segment ids. Prefer fewer, stronger segments.
```

- Ollama call with `"format": "json"` (structured output constraint).
- Give the LLM **pre-scored** segments (see §9.4) so it ranks rather than guesses.
- **Repair loop:** parse → `EditPlan.model_validate()`; on failure, re-send with the validation error message (max 2 retries).
- **Deterministic fallback** (existing `build_deterministic_plan`, improved): if Ollama is off or all retries fail, use heuristic top-K segments — the tool never hard-fails because of the LLM.

### 6.4 Plan preview (trust builder)

The `/plan` response is shown in the UI before render: total duration, cut list with text, caption style, music. One-click "Render" or "Regenerate with tweaks". This is what makes NL-driven editing usable for a non-editor — you *see* the edit before committing to a 2-minute render.

---

## 7. EditPlan JSON Schema (complete, v2)

Extend `app/models/edit_plan.py` to this shape (Pydantic remains the source of truth; this JSON Schema is the contract for the LLM, the frontend, and persisted files):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EditPlan",
  "type": "object",
  "required": ["version", "project_id", "platform", "output", "timeline", "captions", "audio", "export"],
  "properties": {
    "version":              { "type": "string", "const": "2.0" },
    "project_id":           { "type": "string" },
    "prompt":               { "type": "string" },
    "platform":             { "enum": ["instagram_reel", "linkedin_post", "youtube_short", "custom"] },

    "target_duration":      { "type": "number", "minimum": 5, "maximum": 180 },

    "output": {
      "type": "object",
      "required": ["aspect_ratio", "width", "height", "fps"],
      "properties": {
        "aspect_ratio":     { "enum": ["9:16", "1:1", "4:5", "16:9"] },
        "width":            { "type": "integer", "minimum": 720 },
        "height":           { "type": "integer", "minimum": 720 },
        "fps":              { "type": "integer", "minimum": 24, "maximum": 60 }
      }
    },

    "timeline": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["cut_id", "source_start", "source_end"],
        "properties": {
          "cut_id":          { "type": "integer" },
          "source_start":    { "type": "number", "minimum": 0 },
          "source_end":      { "type": "number", "minimum": 0 },
          "speed":           { "type": "number", "default": 1.0, "minimum": 0.5, "maximum": 1.5 },
          "transition_in": {
            "type": "object",
            "properties": {
              "type":        { "enum": ["cut", "crossfade", "dip_to_black"] },
              "duration_s":  { "type": "number", "default": 0.0, "maximum": 1.0 }
            }
          },
          "zoom": {
            "type": "object",
            "properties": {
              "mode":        { "enum": ["none", "punch_in", "slow_push"] },
              "start_scale": { "type": "number", "default": 1.0 },
              "end_scale":   { "type": "number", "default": 1.15, "maximum": 1.3 }
            }
          },
          "focus": {
            "type": "object",
            "properties": {
              "mode":        { "enum": ["face_center", "frame_center"] },
              "x":           { "type": "number", "description": "normalized 0-1 crop center (computed by framer.py)" },
              "y":           { "type": "number" }
            }
          },
          "reason":          { "type": "string", "description": "why this cut was kept (LLM label, for plan review UI)" }
        }
      }
    },

    "captions": {
      "type": "object",
      "required": ["enabled"],
      "properties": {
        "enabled":           { "type": "boolean" },
        "style":             { "enum": ["hormozi_bold", "clean_minimal", "karaoke_yellow", "none"] },
        "font_family":       { "type": "string", "default": "Montserrat-ExtraBold" },
        "font_size":         { "type": "integer", "default": 64 },
        "primary_color":     { "type": "string", "default": "&H00FFFFFF" },
        "highlight_color":   { "type": "string", "default": "&H0000FFFF" },
        "stroke_color":      { "type": "string", "default": "&H00000000" },
        "stroke_width":      { "type": "integer", "default": 4 },
        "position": {
          "type": "object",
          "properties": {
            "y_percent":    { "type": "number", "default": 72 },
            "max_line_width_percent": { "type": "number", "default": 80 }
          }
        },
        "max_words_per_line": { "type": "integer", "default": 3 },
        "words": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["word", "start", "end"],
            "properties": {
              "word":         { "type": "string" },
              "start":        { "type": "number", "description": "edited-timeline seconds" },
              "end":          { "type": "number" },
              "is_highlight": { "type": "boolean", "default": false },
              "is_filler":    { "type": "boolean", "default": false },
              "confidence":   { "type": "number", "default": 1.0 }
            }
          }
        }
      }
    },

    "overlays": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "text", "start", "duration"],
        "properties": {
          "type":            { "enum": ["title_card", "keyword_badge", "lower_third", "progress_bar"] },
          "text":            { "type": "string" },
          "subtext":         { "type": "string" },
          "start":           { "type": "number", "description": "edited-timeline seconds" },
          "duration":        { "type": "number", "minimum": 0.5, "maximum": 6.0 },
          "position": {
            "type": "object",
            "properties": {
              "anchor":      { "enum": ["top", "center", "bottom", "top_left", "bottom_left"] },
              "x_percent":   { "type": "number" },
              "y_percent":   { "type": "number" }
            }
          },
          "animation": {
            "type": "object",
            "properties": {
              "in":          { "enum": ["fade", "slide_up", "pop", "none"] },
              "out":         { "enum": ["fade", "slide_down", "none"] }
            }
          },
          "style_preset":    { "type": "string", "default": "tech_minimal" }
        }
      }
    },

    "audio": {
      "type": "object",
      "properties": {
        "speech": {
          "type": "object",
          "properties": {
            "clean_filler":  { "type": "boolean", "default": true },
            "target_lufs":   { "type": "number", "default": -16.0 }
          }
        },
        "music": {
          "type": "object",
          "properties": {
            "enabled":       { "type": "boolean", "default": false },
            "track_id":      { "type": "string" },
            "mood":          { "type": "string", "default": "upbeat" },
            "volume_db":     { "type": "number", "default": -22.0 },
            "fade_in_s":    { "type": "number", "default": 0.5 },
            "fade_out_s":    { "type": "number", "default": 1.0 }
          }
        },
        "ducking": {
          "type": "object",
          "properties": {
            "enabled":       { "type": "boolean", "default": true },
            "threshold":     { "type": "number", "default": 0.08 },
            "ratio":         { "type": "number", "default": 4.0 },
            "attack_ms":     { "type": "integer", "default": 100 },
            "release_ms":   { "type": "integer", "default": 350 }
          }
        },
        "sfx": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["type", "at"],
            "properties": {
              "type":        { "enum": ["whoosh", "pop", "click"] },
              "at":          { "type": "number", "description": "edited-timeline seconds" },
              "volume_db":   { "type": "number", "default": -18.0 }
            }
          }
        }
      }
    },

    "export": {
      "type": "object",
      "properties": {
        "container":        { "const": "mp4" },
        "video_codec":      { "const": "h264" },
        "crf":              { "type": "integer", "default": 18 },
        "preset":           { "type": "string", "default": "fast" },
        "pix_fmt":          { "const": "yuv420p" },
        "audio_codec":      { "const": "aac" },
        "audio_bitrate_k":  { "type": "integer", "default": 192 },
        "movflags":         { "const": "faststart" },
        "filename_hint":    { "type": "string" }
      }
    }
  },

  "validation_rules": [
    "timeline cuts are sorted by source_start, non-overlapping, and within [0, source_duration]",
    "sum((source_end - source_start) * speed) within ±10% of target_duration when set",
    "each cut >= 0.5s unless it is a filler-removal boundary",
    "caption word times are monotonically increasing and inside [0, total_duration]",
    "overlay start + duration <= total_duration",
    "output dimensions match aspect_ratio * platform preset"
  ]
}
```

**Enforcement:** all `validation_rules` are Pydantic validators / a `plan_validator.py` that runs after LLM assembly. A plan that fails validation never reaches FFmpeg.

---

## 8. Pipeline: Raw Upload → Final Export (step by step)

| # | Stage | Input → Output | Tool | Progress |
|---|---|---|---|---|
| 1 | **Validate & register** | uploaded file → `raw/raw.mp4` + `project.json` | ffprobe (codec, fps, duration, v/a streams); reject non-video | 5% |
| 2 | **Extract audio** | `raw.mp4` → `audio/speech16k.wav` (mono 16 kHz) + `audio/voice48k.wav` | FFmpeg | 10% |
| 3 | **Transcribe** | `speech16k.wav` → `transcripts/transcript.json` (+ `.srt`) | faster-whisper, word timestamps + silero VAD | 10→35% (parse whisper stage) |
| 4 | **Analyze** | transcript → `analysis.json`: speech ranges, filler words, repeated takes, per-segment scores | Python (rules + heuristics) | 40% |
| 5 | **Plan** | prompt + analysis + constraints → `plans/edit_plan.json` | regex extraction → Ollama select → Pydantic validation (repair loop) → fallback | 45→55% |
| 6 | *(user reviews plan in UI — render not started until confirmed)* | | | |
| 7 | **Prepare render assets** | plan → `intermediate/captions.ass`, `intermediate/overlay_*.png`, music pick | captioner, overlays.py (Pillow) | 60% |
| 8 | **Render composite** | raw + plan + assets → `exports/{id}_final.mp4` | one FFmpeg invocation: `atrim/vtrim` cut list (audio & video from same ranges) → per-cut reframe + zoom → concat → overlay PNGs → burn ASS → mix ducked audio | 60→95% (real % from `-progress pipe:1`) |
| 9 | **Post-validate** | export → ffprobe re-check: duration, 1080 width, aspect, streams; loudness spot-check | ffprobe | 97% |
| 10 | **Done** | update project metadata, SSE `completed`, download URL ready | | 100% |

Render is **one FFmpeg process** for step 8 whenever filter-graph length allows (~200 cuts max); for pathological cases, fall back to per-cut segments + concat demuxer (slower, more robust).

---

## 9. Feature Implementation Guides

### 9.1 Silence removal

- **Primary signal:** faster-whisper `vad_filter=True` word timestamps (silero VAD). Words carry the true speech boundaries.
- **Secondary:** FFmpeg `silencedetect` (already implemented) as a cross-check for long dead air.
- **Keep-range construction:** speech ranges minus filler words (§9.2), padded **±120 ms** into silence so consonants aren't clipped (current `padding=0.08` is tight; 0.12 is safer).
- **Rules of thumb:** remove silence > 400 ms; keep natural pauses of 150–300 ms *between sentences* (100% dead pacing sounds robotic); cap consecutive merged gap at 250 ms.
- Merge keep-ranges separated by < 300 ms into one cut (avoids micro-cuts).

### 9.2 Filler-word removal

- Word-level timestamps make this exact: cut `[word.start − 40 ms, word.end + 40 ms]`.
- **Word list with context rules** (critical: "like" and "actually" are often content):
  - Always filler: `um, uh, er, ah, hmm`
  - Filler only at segment start: `so, basically, actually, literally, right, okay so`
  - Phrase fillers (multi-word): `you know, I mean, sort of, kind of, like I said`
- Mark `is_filler` in transcript; plan drops them; captions never include them.
- **Audio safety:** cuts at filler boundaries get 10 ms micro-fades (`afade`) to prevent clicks; verify by ear on 3 test videos.

### 9.3 Repeated takes & low-value sections

- **Repeated n-gram detection:** `difflib.SequenceMatcher` between consecutive segment texts; ratio > 0.7 → repeated take. Keep the **last/fluent** take (fewest fillers per word, higher whisper probability) — the retake is usually the polished one.
- **False starts:** segment ends mid-sentence and next segment restarts the same phrase → drop the earlier one.
- **Explicit retake phrases:** "take two", "let me start again", "one more time" → LLM/regex flags, drop that segment.
- **Low-value:** intro rambling ("hey guys so today I wanted to..."), outro ("so yeah, that's pretty much it") — detect via first/last-segment heuristics + LLM label.

### 9.4 Highlight selection

Score every segment (feeds both LLM and deterministic fallback):

```
score = 2.0·keyword_match(prompt keywords, keep_sections)
      + 1.5·hook_signals (numbers, questions, "mistake", "secret", "why", "how", "never")
      + 1.0·specificity (named entities, dollar amounts, percentages)
      + 0.5·fluency (words/sec within 2.2–3.5 sweet spot)
      − 1.0·filler_rate
```

- **Hook-first ordering:** the highest-scored segment becomes the opening (Reels decide retention in the first 2 s). Option to prepend its text as a title card.
- **Duration fitting:** greedy knapsack — sort by score/second, add until target − 1.5 s, then fill remainder with best-fitting remaining segment; always end on a complete sentence (snap cut to sentence end, never mid-word).
- Aim 25–45 s for Reels (sweet spot ~30 s), 30–90 s for LinkedIn.

### 9.5 Captions

- Current `captioner.py` approach is right: ASS karaoke, 3 words/line, uppercase ExtraBold, yellow active word, thick black stroke.
- Improvements:
  - **Line breaking on 2–4 words**, breaking at punctuation rather than fixed count.
  - **Safe zones:** caption baseline at 72% height; keep clear of the bottom ~20% (IG UI: caption/username/buttons) and top ~10% (username overlay). Verify once on a real phone.
  - **Fonts:** ship `Montserrat-ExtraBold.ttf` in `data/assets/fonts/`, pass `fontsdir` to the `subtitles` filter so rendering is reproducible.
  - **Highlight color pop:** active word in `#FFD700`-ish yellow + secondary color for keyword badges words (`is_highlight` from prompt keywords).
  - Never show filler words (already cut) or words with `confidence < 0.4` (they're likely mis-transcribed → flag in UI instead).

### 9.6 Punch-ins, zooms, transitions

- **MVP: static punch-in** per cut (what `compositor.py` does today): crop `iw/zoom × ih/zoom` centered on focus point, then scale to output. Use 1.12–1.18 (not 1.15 everywhere — vary it).
- **Rhythm rule:** punch-in roughly every 3rd–4th cut or on topic change (existing `idx % 3` logic is a fine start); *avoid zoom changes mid-sentence* — snap to sentence boundaries.
- **Animated slow-push (polish, Week 4):** jitter-free `zoompan` requires pre-upscaling:
  `scale=2160:3840,zoompan=z='min(1+0.0008*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30`
  (upscale first, then zoompan at target size — the standard anti-jitter trick).
- **Transitions:** default hard cut. `dip_to_black` (0.15 s fade) only for topic jumps > 20 s apart. Crossfades (`xfade`) cost more filter-graph complexity — skip in MVP.
- **Never zoom during the hook's first 1.5 s** (motion in the first moment reads as instability).

### 9.7 Reframing (aspect ratio + face tracking)

- 16:9 source → 9:16 output: crop `w = ih·9/16, h = ih` around face x-center; → 1:1: crop `ih × ih` centered on face.
- `framer.py` (new): MediaPipe FaceDetection on frames sampled at 2 fps per cut → median face center → EMA smoothing → clamp so the crop box stays in frame → write `focus.x/y` into each cut (schema §7). If no face found in a cut → `frame_center` fallback. This is a **static per-cut crop** (not continuous tracking) — right for MVP and looks intentional.
- Continuous tracking (polish): per-frame crop x expression from a precomputed keyframe table via `sendcmd` — defer to post-MVP.

### 9.8 Title cards, keyword pop-ups, lower-thirds, motion graphics

- **MVP technique — Pillow → PNG → FFmpeg `overlay` filter:**
  - `overlays.py` renders each overlay as a transparent PNG (1080×1920 canvas) with rounded rectangles, bold text, brand color.
  - Composite: `[base][1:v]overlay=enable='between(t,start,end)'` with fade via `fade` filter on the PNG input (`-loop 1 -t duration`).
  - Animations: `fade` (alpha) and `slide_up` via overlay `y` expression (`y=H-…-(t-start)*speed`).
- **Title card:** first 2–3 s, hook text (≤ 6 words), fade in/out. **Keyword badge:** popup when a keyword is spoken (time = word.start), 1.5 s. **Lower-third:** your name/handle, first 5 s only on LinkedIn style.
- **Remotion (optional, post-MVP):** best for complex animated graphics. Integration pattern: render the overlay layer as a **transparent VP9 WebM** (`--codec=vp9 --pixel-format=yuva420p`), composite over the cut video with FFmpeg `overlay`. Benefits: real easing curves, spring physics, reusable React components, no jitter. Cost: Node toolchain + render time. **Recommendation: ship MVP with Pillow+FFmpeg; add Remotion only if overlays feel flat.**

### 9.9 Audio mixing

- **Speech chain:** cut audio with the *same* timeline (fix for the desync bug) → `loudnorm=I=-16:TP=-1.5:LRA=11` (two-pass for accuracy) → 10 ms micro-fades at cut boundaries.
- **Music:** local library `data/assets/music/{mood}/` (10–15 royalty-free tracks, tagged) — pick by `music_mood`, loop/trim to timeline length, `volume_db ≈ -22`, fade in/out. **Louder music is the #1 amateur tell — when in doubt, lower it 3 dB.**
- **Ducking:** existing `sidechaincompress` (threshold 0.08, ratio 4:1, attack 100 ms, release 350 ms) is correct. Speech should sit ~10–14 dB above music at all times.
- **SFX:** whoosh on section transitions, subtle pop on keyword badges — `volume -18 dB`, tasteful; default **off** for LinkedIn tone, on for Reels energy.
- **Target loudness:** -14 to -16 LUFS integrated, true peak ≤ -1.0 dBTP (platforms normalize to -14 anyway; going louder just gets re-compressed).

---

## 10. Local Folder Structure & File Formats

```
AI-Video-Editor/               (repo root — currently the server folder)
├── app/                       # FastAPI backend (§4.1)
├── web/                       # Next.js frontend (NEW — §11 Week 3)
├── data/                      # git-ignored, all local artifacts
│   ├── projects/{project_id}/
│   │   ├── project.json           # metadata, status, timestamps, prompt history
│   │   ├── raw/raw.mp4            # original upload, never modified
│   │   ├── audio/
│   │   │   ├── speech16k.wav      # whisper input (mono 16 kHz)
│   │   │   └── voice48k.wav       # pipeline audio
│   │   ├── transcripts/
│   │   │   ├── transcript.json    # words + timestamps + probabilities (source of truth)
│   │   │   └── transcript.srt    # human-readable
│   │   ├── analysis/
│   │   │   └── analysis.json     # speech ranges, fillers, takes, scores
│   │   ├── plans/
│   │   │   ├── edit_plan.json    # validated plan (rendered exactly)
│   │   │   └── edit_plan_v{n}.json # history per (re)generation
│   │   ├── intermediate/
│   │   │   ├── captions.ass
│   │   │   ├── overlay_{n}.png
│   │   │   └── speech_cuts.wav   # cut+normalized speech (debug)
│   │   └── exports/
│   │       └── {id}_{platform}_{n}.mp4   # final, faststart, H.264/AAC
│   └── assets/
│       ├── fonts/                 # Montserrat-ExtraBold.ttf etc.
│       ├── music/{mood}/*.mp3     # royalty-free, tagged
│       └── sfx/*.wav              # whoosh/pop/click
├── main.py / requirements.txt / PLAN.md / README.md
```

**Format rules:** JSON for every machine artifact (Pydantic-validated on read); ASS for captions (animatable, precise to centiseconds); PNG with alpha for overlays; WAV for intermediates; MP4 (H.264 High, `yuv420p`, AAC 192 k, `+faststart`) for exports — the one format every platform accepts without re-transcode warnings.

---

## 11. 4-Week Build Roadmap (solo, ~2–3 h/evening + weekend sessions)

### Week 1 — Real transcript + honest cuts (backend core)
- **D1:** Fix gap bugs: real `ffprobe` duration (`prober.py`), filename sanitization, upload validation. 
- **D2:** `transcriber.py` with faster-whisper (§5) → real `TranscriptResult`, persist JSON+SRT. Test `base` vs `small` on one real video.
- **D3:** `analysis.py`: filler-word marking (§9.2), keep-range construction (§9.1), merge rules.
- **D4:** Rewrite `compositor.py` render to cut **audio and video from the same range list in one FFmpeg command** (fixes desync); micro-fades at boundaries. Verify sync on 3 test videos.
- **D5–6:** Refactor into `pipeline/runner.py` stages with progress hooks; `asyncio.to_thread` for blocking calls; one-job semaphore; loudnorm in pipeline; export presets (Reel/LinkedIn/Short/custom); post-validate via ffprobe.
- **Acceptance:** 5-min raw video in → clean silent/filler-cut MP4 out (correct AR, synced A/V, burned captions from real words, progress visible in SSE, ≤ 6 min wall-clock on CPU).

### Week 2 — Smart planning + framing
- **D1–2:** EditPlan v2 schema (§7) + validators; prompt constraint extraction (§6.2); persist & GET plan.
- **D3–4:** LLM segment selection via Ollama (§6.3) with repair loop + improved deterministic fallback; highlight scoring (§9.4); duration-fitting knapsack; hook-first ordering.
- **D5–6:** `framer.py` face-aware crop (§9.7) + static punch-ins with rhythm rules (§9.6).
- **Acceptance:** "Make a 40 s reel about pricing, Hormozi captions" → valid plan (40 s ±10%, face-centered 9:16, punch-ins, correct caption words), reviewable JSON before render.

### Week 3 — Frontend + audio polish
- **D1–2:** Next.js app (§ below): upload dropzone, platform select, prompt + constraints form.
- **D3:** SSE progress bar + polling fallback; project history list.
- **D4:** Plan review screen (cuts, duration, caption style) → confirm & render; preview `<video>` (FileResponse supports Range → seekable) + download button.
- **D5–6:** Music library (10–15 tagged tracks) + ducking mix into render; SFX hooks; `overlays.py` title card + keyword badge (§9.8).
- **Acceptance:** Full browser flow on 2 real videos; music ducks under speech; title card + one keyword popup render; preview scrubs smoothly.

### Week 4 — Highlights + quality hardening
- **D1–2:** Repeated-take/false-start detection (§9.3); outro/intro trimming; caption polish (safe zones, punctuation breaking, color pop).
- **D3:** Failure handling pass (§13): model fallback chain, JSON repair, face-loss fallback, cancel endpoint; unit tests for cutters + validators; batch test script over `data/samples/`.
- **D4:** Quality checklist run (§14) on 3 real videos; tune thresholds (silence padding, zoom rhythm, music level).
- **D5–6:** Docs, README update, performance timing, cleanup. *(Stretch: Remotion overlay path, RQ+Redis extraction.)*
- **Acceptance:** 3 real talking-head videos → each output passes the §14 checklist; full pipeline ≤ 5 min per 5-min input; zero crashes across 10 consecutive runs.

**Frontend design (Week 3 detail):** Next.js 14 App Router, one page, no DB, minimal state. Components: `UploadCard` (drag-drop → `POST /upload`), `ConfigForm` (platform pills, prompt textarea, constraint chips: duration / caption style / tone / music mood / keywords), `PlanReview` (duration + cut list + caption preview), `ProgressBar` (`EventSource('/api/projects/{id}/progress')`), `PreviewPlayer` + `DownloadButton`. ~5 components, one `lib/api.ts` fetch wrapper. No auth, no styling framework needed beyond Tailwind.

---

## 12. Minimum Feature Set for v1 (MoSCoW)

| Must (v1, ship nothing without these) | Should (v1 if time allows) | Could (post-v1) | Won't |
|---|---|---|---|
| Upload + validate MP4 | Title card + keyword popup overlays | Remotion motion graphics | Cloud/deployment |
| faster-whisper word-level transcription | Repeated-take detection | Continuous face tracking | Multi-user / auth |
| Silence + filler removal (synced A/V) | BGM library with mood selection | Animated slow-push zooms | Timeline editor UI |
| 9:16 / 1:1 / custom presets | SFX (whoosh/pop) | RQ + Redis queue | B-roll matching |
| Prompt → validated EditPlan (deterministic fallback) | Plan review screen | Auto-posting | Color grading |
| ASS karaoke captions | Project history list | A/B render compare | |
| Face-aware static reframe + static punch-ins | Cancel render | | |
| Loudnorm + ducked music | | | |
| SSE progress + preview + download | | | |

The first *usable* version = the **Must** column ≈ end of Week 2.

---

## 13. Common Failure Cases & Handling

| # | Failure | Detection | Handling |
|---|---|---|---|
| 1 | Whisper mistranscribes (names, jargon, accent) | `word.probability < 0.5` | Flag low-confidence words in plan review UI (later: manual correction); never highlight uncertain words; keep `small`+ model |
| 2 | LLM returns invalid JSON / hallucinated ids | Pydantic validation | Repair loop (2 retries with error fed back) → deterministic heuristic plan (never hard-fail) |
| 3 | Ollama not running | Connection error | Same as #2 — tool works fully without LLM |
| 4 | Face detection fails (profile, hands, off-frame) | No face in sampled frames | `frame_center` fallback crop; log once |
| 5 | A/V drift after cuts | ffprobe duration mismatch vs plan sum | Cut audio & video from the same range list in one command (structural fix, §8 step 8); post-validate always |
| 6 | Audible clicks at cut boundaries | Ear test in Week 1 | 10 ms micro-fades + cut inside silence padding (±120 ms) |
| 7 | Zoompan jitter | Visual | Static punch-in crop (MVP); pre-upscale technique for animated zooms (§9.6) |
| 8 | GPU OOM / no CUDA wheels | Exception on model load | Model ladder fallback `medium→small→base` + CPU |
| 9 | Weird source codec (HEVC, 10-bit, VFR, .mov) | ffprobe validation | Re-encode to intermediate CFR H.264/yuv420p before pipeline |
| 10 | Output over/under target duration | Plan validation | Knapsack re-fit before render; hard clamp at export |
| 11 | FFmpeg hangs (huge filter graph) | Timeout watchdog | Kill + retry with per-segment rendering + concat demuxer fallback path |
| 12 | Render blocks API responsiveness | SSE stalls | Blocking work in `asyncio.to_thread`; one-job semaphore; queue status |
| 13 | Windows path escaping breaks `subtitles=` filter | FFmpeg parse error | Central `escape_for_ffmpeg()` helper (colon/backslash rules) — extend the existing one |
| 14 | Music library empty / mood not found | File check | Disable BGM gracefully, warn in plan review |
| 15 | Upload interrupted / partial file | Size + ffprobe check | Reject with clear error; checksum later |
| 16 | FFmpeg not installed / not on PATH | `ffmpeg_bin` check | Clear setup error message with install instructions (health endpoint already exposes binary path) |
| 17 | Project state lost after server restart | In-memory `job_queue` | Persist `project.json` per project; on boot, rescan `data/projects/` and mark interrupted jobs as `failed_recoverable` |

---

## 14. Quality Checklist (pre-publish, per output)

**Technical**
- [ ] ffprobe: correct resolution (1080×1920 / 1080×1080), fps, duration within target ±10%
- [ ] H.264 High `yuv420p`, AAC ≥ 128 k, `+faststart`, ≤ 60 MB/min
- [ ] A/V in sync at first and last cut (spot check)

**Captions**
- [ ] Every spoken (kept) word appears; none overlap; timing drift < 50 ms vs audio
- [ ] ≤ 4 words per screen, breaking at punctuation
- [ ] Inside safe zones (no IG UI collision top 10% / bottom 20%) — verified once on a real phone
- [ ] Active word highlight readable; stroke visible on white and busy backgrounds

**Pacing & structure**
- [ ] No silence > 400 ms; no gap < 80 ms (machine-gun cuts)
- [ ] Opens on the hook in the first 2 s; ends on a complete sentence
- [ ] Cut points on sentence boundaries; no mid-word cuts (ear test)
- [ ] Zoom/punch-in at most every 3rd–4th cut, never mid-sentence, never in the first 1.5 s

**Visual**
- [ ] Face centered in frame across cuts; no crop jitter
- [ ] Title card ≤ 6 words; keyword popups don't cover the face
- [ ] Consistent font/color family across captions and overlays

**Audio**
- [ ] Speech -14 to -16 LUFS, true peak ≤ -1 dB (measure with `loudnorm` print or `ffmpeg -af ebur128`)
- [ ] Music ≥ 10 dB below speech during talking; no music swell in gaps > 3 s; tasteful fades
- [ ] No clicks, no clipping, no room-tone jumps at cuts

**Platform sanity**
- [ ] Reel ≤ 60 s (sweet spot 25–45 s); Short ≤ 3 min; LinkedIn 1:1 or 4:5
- [ ] Upload to platform drafts and confirm no re-transcode warning before publishing

---

## Appendix A — Key FFmpeg Recipes (reference)

```bash
# Probe
ffprobe -v error -show_entries format=duration -of json raw.mp4

# Extract whisper audio
ffmpeg -i raw.mp4 -vn -ac 1 -ar 16000 speech16k.wav

# Cut A+V from same ranges, reframe 9:16, static punch-in, burn ASS (per cut n)
[0:v]trim=start=S:end=E,setpts=PTS-STARTPTS,crop=w=ih*9/16:h=ih:x=X:y=0, \
     scale=1080:1920[vN]
[0:a]trim=start=S:end=E,asetpts=PTS-STARTPTS[aN]
# concat all [vN] / [aN], then:
[vcat]subtitles='captions.ass':fontsdir='data/assets/fonts'[vfinal]
# overlay PNG (title card): -loop 1 -t 2.5 -i card.png
[vfinal][1:v]overlay=enable='between(t,0,2.5)':x=(W-w)/2:y=(H-h)/2
# music ducking mix
[1:a]volume=-22dB[m];[m][0:a]sidechaincompress=threshold=0.08:ratio=4:attack=100:release=350[md]; \
[0:a][md]amix=inputs=2:duration=first[outa]
# export
-map [vout] -map [outa] -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart final.mp4
```

## Appendix B — Performance Expectations (5-min 1080p source, CPU-only)

| Stage | Time |
|---|---|
| Extract audio + probe | ~10 s |
| faster-whisper `small` (CPU) | ~5–8 min (`base`: ~3 min; CUDA `small`: <1 min) |
| Analysis + plan | < 5 s |
| FFmpeg render (60 s output, CRF 18) | ~60–120 s |
| **Total** | **≈ 7–11 min CPU / ≈ 2–3 min with GPU** |
