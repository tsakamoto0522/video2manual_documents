"""
Video processing endpoints (STT, scene detection).
"""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core import logger, settings
from app.models import ProcessStatusResponse, SceneDetectionResult, Transcription
from app.services.scenes import OpenCVSceneDetector
from app.services.stt import get_stt_engine
from app.services.summarizer import get_summarizer
from app.utils import FFmpegWrapper

router = APIRouter()
ffmpeg = FFmpegWrapper()


@router.post("/transcribe/{video_id}", response_model=ProcessStatusResponse)
async def transcribe_video(video_id: str) -> ProcessStatusResponse:
    """
    Perform speech-to-text on uploaded video.

    Args:
        video_id: Video UUID

    Returns:
        ProcessStatusResponse with transcription status
    """
    logger.info(f"Starting transcription for video: {video_id}")

    # 動画パス取得
    video_dir = settings.upload_dir / video_id
    video_files = list(video_dir.glob("source.*"))
    if not video_files:
        raise HTTPException(status_code=404, detail="動画が見つかりません")

    video_path = video_files[0]

    try:
        # 音声抽出
        audio_path = settings.intermediate_dir / video_id / "audio.wav"
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg.extract_audio(video_path, audio_path)

        # STT 実行
        stt_engine = get_stt_engine()
        transcription = await stt_engine.transcribe(audio_path, video_path.name)

        # 文字起こしテキストを結合
        full_text = " ".join([seg.text for seg in transcription.segments])

        # GPTで要約を実行
        if settings.openai_api_key:
            try:
                logger.info(f"Starting summarization for video: {video_id}")
                summarizer = get_summarizer()
                summary = await summarizer.summarize(full_text)
                transcription.summary = summary
                logger.info(f"Summarization completed: {video_id}")
            except Exception as e:
                logger.warning(f"Summarization failed, continuing without summary: {e}")
                transcription.summary = None
        else:
            logger.info("OpenAI API key not configured, skipping summarization")
            transcription.summary = None

        # 結果を保存
        output_path = settings.intermediate_dir / video_id / "transcription.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(transcription.model_dump_json(indent=2), encoding="utf-8")

        logger.info(f"Transcription completed: {video_id}")

        message = f"{len(transcription.segments)} セグメントを認識しました"
        if transcription.summary:
            message += " (要約完了)"

        return ProcessStatusResponse(
            video_id=video_id,
            status="completed",
            message=message,
            output_path=str(output_path),
        )

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return ProcessStatusResponse(
            video_id=video_id,
            status="failed",
            message=str(e),
            output_path=None,
        )


@router.post("/scene-detect/{video_id}", response_model=ProcessStatusResponse)
async def detect_scenes(video_id: str) -> ProcessStatusResponse:
    """
    Detect scene changes and extract keyframes.

    Args:
        video_id: Video UUID

    Returns:
        ProcessStatusResponse with scene detection status
    """
    logger.info(f"Starting scene detection for video: {video_id}")

    # 動画パス取得
    video_dir = settings.upload_dir / video_id
    video_files = list(video_dir.glob("source.*"))
    if not video_files:
        raise HTTPException(status_code=404, detail="動画が見つかりません")

    video_path = video_files[0]

    try:
        # シーン検出
        detector = OpenCVSceneDetector()
        capture_dir = settings.capture_dir / video_id
        capture_dir.mkdir(parents=True, exist_ok=True)

        scene_result = await detector.detect_scenes(video_path, capture_dir)

        # 結果を保存
        output_path = settings.intermediate_dir / video_id / "scenes.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(scene_result.model_dump_json(indent=2), encoding="utf-8")

        logger.info(f"Scene detection completed: {video_id}")

        return ProcessStatusResponse(
            video_id=video_id,
            status="completed",
            message=f"{len(scene_result.scenes)} シーンを検出しました",
            output_path=str(output_path),
        )

    except Exception as e:
        logger.error(f"Scene detection failed: {e}")
        return ProcessStatusResponse(
            video_id=video_id,
            status="failed",
            message=str(e),
            output_path=None,
        )


@router.get("/transcribe/{video_id}", response_model=Transcription)
async def get_transcription(video_id: str) -> Transcription:
    """
    Get transcription result.

    Args:
        video_id: Video UUID

    Returns:
        Transcription data
    """
    transcription_path = settings.intermediate_dir / video_id / "transcription.json"
    if not transcription_path.exists():
        raise HTTPException(status_code=404, detail="文字起こし結果が見つかりません")

    return Transcription.model_validate_json(transcription_path.read_text(encoding="utf-8"))


@router.get("/scene-detect/{video_id}", response_model=SceneDetectionResult)
async def get_scenes(video_id: str) -> SceneDetectionResult:
    """
    Get scene detection result.

    Args:
        video_id: Video UUID

    Returns:
        SceneDetectionResult data
    """
    scenes_path = settings.intermediate_dir / video_id / "scenes.json"
    if not scenes_path.exists():
        raise HTTPException(status_code=404, detail="シーン検出結果が見つかりません")

    return SceneDetectionResult.model_validate_json(scenes_path.read_text(encoding="utf-8"))
