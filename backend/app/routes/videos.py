"""
Video upload and management endpoints.
"""
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core import ValidationError, logger, settings
from app.models import VideoUploadResponse
from app.utils import FFmpegWrapper

router = APIRouter()
ffmpeg = FFmpegWrapper()


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)) -> VideoUploadResponse:
    """
    Upload a video file for processing.

    Args:
        file: Video file upload

    Returns:
        VideoUploadResponse with video_id and metadata
    """
    # バリデーション: 拡張子
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が不正です")

    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.get_video_extensions():
        raise HTTPException(
            status_code=400,
            detail=f"対応していない形式です。許可: {settings.allowed_video_extensions}",
        )

    # UUID ベースの保存
    video_id = str(uuid.uuid4())
    video_dir = settings.upload_dir / video_id
    video_dir.mkdir(parents=True, exist_ok=True)

    video_path = video_dir / f"source.{ext}"

    # ファイル保存
    try:
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save video: {e}")
        raise HTTPException(status_code=500, detail="動画の保存に失敗しました")

    # サイズチェック
    size_mb = video_path.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_video_size_mb:
        video_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=f"ファイルサイズが大きすぎます。最大: {settings.max_video_size_mb}MB",
        )

    # 動画情報取得
    try:
        duration = ffmpeg.get_video_duration(video_path)
    except Exception as e:
        logger.warning(f"Failed to get duration: {e}")
        duration = None

    logger.info(f"Video uploaded: {video_id} ({file.filename}, {size_mb:.2f}MB)")

    return VideoUploadResponse(
        video_id=video_id,
        filename=file.filename or "unknown",
        size_bytes=video_path.stat().st_size,
        duration_sec=duration,
    )


@router.get("/{video_id}")
async def get_video_info(video_id: str):
    """
    Get video information.

    Args:
        video_id: Video UUID

    Returns:
        Video metadata
    """
    video_dir = settings.upload_dir / video_id
    if not video_dir.exists():
        raise HTTPException(status_code=404, detail="動画が見つかりません")

    # 動画ファイルを検索
    video_files = list(video_dir.glob("source.*"))
    if not video_files:
        raise HTTPException(status_code=404, detail="動画ファイルが見つかりません")

    video_path = video_files[0]

    return {
        "video_id": video_id,
        "filename": video_path.name,
        "size_bytes": video_path.stat().st_size,
        "path": str(video_path),
    }
