"""
Pydantic models for API requests/responses and data schemas.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# Transcription Schemas (RQ-001)
# ============================================================================


class TranscriptionSegment(BaseModel):
    """音声認識セグメント"""

    start: float = Field(description="開始時刻 (秒)")
    end: float = Field(description="終了時刻 (秒)")
    speaker: Optional[str] = Field(default=None, description="話者ID (オプション)")
    text: str = Field(description="認識テキスト")


class Transcription(BaseModel):
    """音声認識結果"""

    video_filename: str = Field(description="動画ファイル名")
    duration_sec: float = Field(description="動画の長さ (秒)")
    segments: list[TranscriptionSegment] = Field(description="認識セグメントリスト")
    summary: Optional[str] = Field(default=None, description="GPTによる要約テキスト")


# ============================================================================
# Scene Detection Schemas (RQ-002)
# ============================================================================


class SceneInfo(BaseModel):
    """シーン情報"""

    time: float = Field(description="シーン切替時刻 (秒)")
    frame_path: str = Field(description="キャプチャ画像のパス")


class SceneDetectionResult(BaseModel):
    """シーン検出結果"""

    video_filename: str = Field(description="動画ファイル名")
    scenes: list[SceneInfo] = Field(description="シーンリスト")


# ============================================================================
# Manual Plan Schemas (RQ-003, RQ-004)
# ============================================================================


class ManualStep(BaseModel):
    """マニュアルの手順"""

    title: str = Field(description="手順タイトル")
    narration: str = Field(description="ナレーション (セリフ)")
    note: Optional[str] = Field(default=None, description="注意事項・メモ")
    image: Optional[str] = Field(default=None, description="キャプチャ画像パス")
    start: float = Field(description="開始時刻 (秒)")
    end: float = Field(description="終了時刻 (秒)")
    selected: bool = Field(default=True, description="採用フラグ")


class ManualPlan(BaseModel):
    """マニュアル生成計画"""

    title: str = Field(description="マニュアルタイトル")
    source_video: str = Field(description="元動画ファイル名")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    steps: list[ManualStep] = Field(description="手順リスト")


# ============================================================================
# API Request/Response Models
# ============================================================================


class VideoUploadResponse(BaseModel):
    """動画アップロードレスポンス"""

    video_id: str = Field(description="動画ID (UUID)")
    filename: str = Field(description="ファイル名")
    size_bytes: int = Field(description="ファイルサイズ")
    duration_sec: Optional[float] = Field(default=None, description="動画の長さ")


class ProcessStatusResponse(BaseModel):
    """処理ステータスレスポンス"""

    video_id: str = Field(description="動画ID")
    status: str = Field(description="ステータス (processing, completed, failed)")
    message: str = Field(description="ステータスメッセージ")
    output_path: Optional[str] = Field(default=None, description="出力ファイルパス")


class CaptureSelectionRequest(BaseModel):
    """キャプチャ選択リクエスト"""

    video_id: str = Field(description="動画ID")
    selections: dict[int, bool] = Field(
        description="手順インデックス → 採用フラグのマッピング"
    )


class ExportRequest(BaseModel):
    """エクスポートリクエスト"""

    video_id: str = Field(description="動画ID")
    format: str = Field(default="markdown", description="出力形式 (markdown, pdf)")
    template: Optional[str] = Field(default=None, description="テンプレート名")


class ExportResponse(BaseModel):
    """エクスポートレスポンス"""

    video_id: str = Field(description="動画ID")
    format: str = Field(description="出力形式")
    output_path: str = Field(description="出力ファイルパス")
    download_url: str = Field(description="ダウンロードURL")
