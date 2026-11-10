# AI Video Studio - Backend

A local-first, AI-powered video editing backend for turning raw talking-head videos into polished Instagram Reels (9:16), LinkedIn posts (1:1), and YouTube Shorts.

## 🚀 Architecture Highlights

- **FastAPI**: Asynchronous REST endpoints and Server-Sent Events (SSE) for live rendering progress.
- **FFmpeg Engine**: Silence detection, dynamic 9:16 reframing, 1.15x punch-in zooms, sidechain audio ducking, and H.264/AAC muxing.
- **Hormozi-Style Captions**: Word-by-word highlighted `.ass` subtitles with custom fonts and safe-zone positioning.
- **AI Edit Planner**: Converts natural language prompts into a strict JSON `EditPlan` via Google Gemini (`gemini-2.5-flash`) with structured output enforcement.
- **Local Data Storage**: All raw assets, transcripts, and exports stay 100% on your machine in `./data/projects/`.

---

## 🛠️ Prerequisites

1. **Python 3.10+** (Python 3.11 / 3.12 recommended for PyTorch/CUDA wheels)
2. **FFmpeg**:
   - Install via Chocolatey: `choco install ffmpeg`
   - Or install via winget: `winget install Gyan.FFmpeg`
   - Or download static binaries and put `ffmpeg.exe` on your system `PATH`.
3. **Gemini API Key**:
   - Obtain a free API key from [Google AI Studio](https://aistudio.google.com)
   - Add `GEMINI_API_KEY=your_key_here` to your `.env` file.

---

## 📦 Setup & Installation

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   copy .env.example .env
   ```

4. Start the backend server:
   ```bash
   python main.py
   # Or using uvicorn directly:
   uvicorn main:app --reload --port 8000
   ```

5. Verify server status:
   - Healthcheck: `http://localhost:8000/health`
   - Interactive API Docs (Swagger UI): `http://localhost:8000/docs`

---

## 📡 API Reference

### 1. Upload Video
- **Endpoint**: `POST /api/projects/upload`
- **Payload**: `multipart/form-data` with `file=@raw_video.mp4`
- **Response**:
  ```json
  {
    "project_id": "a1b2c3d4",
    "filename": "raw_video.mp4",
    "status": "idle"
  }
  ```

### 2. Generate Edit Plan
- **Endpoint**: `POST /api/projects/{project_id}/plan`
- **Body**:
  ```json
  {
    "prompt": "Cut pauses, punch-in on key points, and make an Instagram Reel under 45s",
    "platform": "instagram_reel",
    "target_duration": 45.0
  }
  ```
- **Response**: Validated `EditPlan` JSON (timeline cuts, zoom scales, caption words with timestamps).

### 3. Trigger Render
- **Endpoint**: `POST /api/projects/{project_id}/render`
- **Body**: `EditPlan` JSON (confirmed or edited by user)
- **Response**: `{"message": "Rendering job enqueued", "project_id": "a1b2c3d4"}`

### 4. Live Progress Stream (SSE)
- **Endpoint**: `GET /api/projects/{project_id}/progress`
- Yields SSE events: `{"project_id": "...", "status": "rendering", "progress": 75, "step": "Normalizing audio track"}`

### 5. Download Export
- **Endpoint**: `GET /api/projects/{project_id}/download`
- Returns the final `.mp4` video.

---

## 📂 Local Directory Structure

```
server/
├── app/
│   ├── api/                 # Endpoints (upload, plan, render, progress)
│   ├── core/                # App config & logging
│   ├── models/              # Pydantic schemas (EditPlan, Project, Transcript)
│   ├── services/            # Media engines (FFmpeg, Whisper, Captioner, AudioMixer)
│   └── workers/             # Async background job queue
├── data/                    # Project files and assets (git-ignored)
│   └── projects/{id}/       # raw/, audio/, transcripts/, intermediate/, exports/
├── main.py                  # Server entrypoint
├── requirements.txt         # Dependencies
└── .env.example             # Configuration defaults
```

