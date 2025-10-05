# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Video Manual Generator は、操作説明動画から自動的にステップバイステップのマニュアルを生成するシステムです。

**Tech Stack:**
- Backend: FastAPI (Python 3.11+)
- Frontend: React + Vite + TypeScript
- Deployment: Docker Compose
- AI Services: OpenAI GPT-4o Transcribe, GPT-5

## Development Commands

### Docker (Primary Development Method)

```bash
# Initial setup
docker-compose up -d --build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a specific service
docker-compose restart backend
docker-compose restart frontend

# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Clean rebuild
docker-compose down -v
docker-compose up -d --build

# Execute commands in container
docker exec video_manual_backend sh -c "command"
```

### Backend Development

```bash
# Code formatting
cd backend
black app/
ruff check app/

# Type checking
mypy app/

# Run tests
pytest tests/ -v
pytest tests/test_api.py -v  # Single test file
```

### Frontend Development

```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Build
npm run build
```

## Architecture

### Processing Pipeline

1. **Video Upload** → `POST /videos/upload`
   - Stores video in `data/uploads/{video_id}/`
   - Returns `video_id` UUID

2. **Transcription** → `POST /process/transcribe/{video_id}`
   - Extracts audio using FFmpeg
   - Transcribes using GPT-4o Transcribe API
   - Summarizes transcription using GPT-5
   - Saves to `data/intermediate/{video_id}/transcription.json`

3. **Scene Detection** → `POST /process/scene-detect/{video_id}`
   - OpenCV histogram/SSIM comparison
   - Extracts keyframes as JPG
   - Saves to `data/captures/{video_id}/scene_*.jpg`
   - Saves metadata to `data/intermediate/{video_id}/scenes.json`

4. **Manual Plan** → `POST /manual/plan`
   - Combines transcription + scenes
   - Uses `ManualPlanner` to merge segments
   - Saves to `data/intermediate/{video_id}/manual_plan.json`

5. **Export** → `POST /export/markdown` or `/export/pdf`
   - Renders Jinja2 template
   - PDF uses Playwright

### Strategy Pattern Implementation

The codebase uses Strategy pattern for pluggable engines:

**STT Engines** (`app/services/stt/`):
- `WhisperSTT` - Local Whisper model
- `GPT4oSTT` - OpenAI GPT-4o Transcribe API
- `DummySTT` - Mock for testing
- Configured via `STT_ENGINE` env var (`whisper`, `gpt4o`, `dummy`)
- Factory: `get_stt_engine()` in `app/services/stt/__init__.py`

**Scene Detection** (`app/services/scenes/`):
- `OpenCVSceneDetector` - Histogram or SSIM methods
- Configured via `SCENE_DETECTION_METHOD` env var

**Summarization** (`app/services/summarizer/`):
- `OpenAISummarizer` - GPT-5 summarization
- Prompt location: `app/services/summarizer/openai_summarizer.py:47-59`

### Adding New Strategy Implementations

**Example: New STT Engine**

1. Create `app/services/stt/new_stt.py`:
```python
from .base import STTStrategy

class NewSTT(STTStrategy):
    async def transcribe(self, audio_path: Path, video_filename: str) -> Transcription:
        # Implementation
        pass
```

2. Register in `app/services/stt/__init__.py`:
```python
from .new_stt import NewSTT

def get_stt_engine() -> STTStrategy:
    if settings.stt_engine == "new":
        return NewSTT()
    # ... existing code
```

3. Update `app/core/config.py`:
```python
stt_engine: Literal["whisper", "gpt4o", "new", "dummy"] = Field(default="gpt4o")
```

## Configuration

### Environment Variables

All configuration is in `backend/.env`. Key variables:

```bash
# OpenAI API (Required)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5

# STT Engine Selection
STT_ENGINE=gpt4o  # Options: whisper, gpt4o, dummy

# Scene Detection Tuning
SCENE_THRESHOLD=30.0  # 0-100, higher = more strict
SCENE_DETECTION_METHOD=histogram  # Options: histogram, ssim
MIN_SCENE_DURATION_SEC=2.0
```

Configuration class: `app/core/config.py` (Pydantic Settings)

### Static File Serving

FastAPI serves static files from `data/` directory:
- Location: `app/main.py:81`
- Mount point: `/data`
- Example: `http://localhost:8000/data/captures/{video_id}/scene_0001.jpg`

## Data Flow & File Locations

```
data/
├── uploads/{video_id}/source.mp4          # Uploaded video
├── intermediate/{video_id}/
│   ├── audio.wav                          # Extracted audio
│   ├── transcription.json                 # STT result + summary
│   ├── scenes.json                        # Scene metadata
│   └── manual_plan.json                   # Generated plan
├── captures/{video_id}/scene_*.jpg        # Keyframe images
└── exports/{video_id}/manual.{md,pdf}     # Final output
```

## OpenAI Integration

**Two LLMs are used:**

1. **GPT-4o Transcribe** (`app/services/stt/gpt4o_stt.py`)
   - Model: `gpt-4o-transcribe`
   - Format: `response_format="json"`
   - Manual segment splitting using punctuation if needed

2. **GPT-5 Summarizer** (`app/services/summarizer/openai_summarizer.py`)
   - Model: Configured via `OPENAI_MODEL` env var
   - Temperature: 0.3
   - Max tokens: 2000 (parameter: `max_completion_tokens` for GPT-5)
   - System prompt: Lines 47-59

**Important:** GPT-5 requires `max_completion_tokens` instead of `max_tokens`.

## Hot Reload

Docker volumes are configured for hot reload:
- Backend: Changes in `backend/app/` auto-reload via uvicorn
- Frontend: Changes in `frontend/src/` auto-reload via Vite

## Common Issues

**Transcription fails with 404:**
- Check model name is `gpt-4o-transcribe` in `gpt4o_stt.py`
- Verify `OPENAI_API_KEY` is set in `.env`

**Images not loading (404):**
- Verify static files mount in `app/main.py:81`
- Check files exist: `docker exec video_manual_backend ls /app/data/captures/{video_id}/`

**Summarization fails with max_tokens error:**
- GPT-5 uses `max_completion_tokens` instead of `max_tokens`
- Update in `openai_summarizer.py:56`

## API Endpoints

Key routes (`app/routes/`):
- `videos.py` - Upload/list videos
- `process.py` - Transcription & scene detection
- `manual.py` - Plan creation & editing
- `export.py` - Markdown/PDF generation

OpenAPI docs: http://localhost:8000/docs
