"""
Whisper-based STT implementation.
"""
import asyncio
from pathlib import Path
from typing import Optional

import whisper

from app.core import STTError, logger, settings
from app.models import Transcription, TranscriptionSegment
from app.utils import FFmpegWrapper

from .base import STTStrategy


class WhisperSTT(STTStrategy):
    """OpenAI Whisperを使用した音声認識実装"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        language: Optional[str] = None,
    ):
        """
        Initialize Whisper STT.

        Args:
            model_name: Whisper model size (tiny/base/small/medium/large)
            device: Device to use (cpu/cuda)
            language: Language code (ja/en/etc.)
        """
        self.model_name = model_name or settings.whisper_model
        self.device = device or settings.whisper_device
        self.language = language or settings.whisper_language
        self.model: Optional[whisper.Whisper] = None
        self.ffmpeg = FFmpegWrapper()

    def _load_model(self) -> whisper.Whisper:
        """Whisperモデルをロード (遅延ロード)"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")
            try:
                self.model = whisper.load_model(self.model_name, device=self.device)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise STTError(f"Whisperモデルのロードに失敗しました: {e}")
        return self.model

    async def transcribe(self, audio_path: Path, video_filename: str) -> Transcription:
        """音声認識を実行"""
        logger.info(
            f"Starting Whisper transcription for {video_filename} "
            f"(model={self.model_name}, language={self.language})"
        )

        # 非同期実行のため別スレッドで実行
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._transcribe_sync, audio_path, video_filename)

        logger.info(f"Transcription completed: {len(result.segments)} segments")
        return result

    def _transcribe_sync(self, audio_path: Path, video_filename: str) -> Transcription:
        """同期的な文字起こし処理"""
        try:
            model = self._load_model()

            # Whisper実行
            result = model.transcribe(
                str(audio_path),
                language=self.language if self.language != "auto" else None,
                verbose=False,
                word_timestamps=False,  # 単語レベルのタイムスタンプは不要
            )

            # セグメント変換
            segments = []
            for seg in result.get("segments", []):
                segments.append(
                    TranscriptionSegment(
                        start=seg["start"],
                        end=seg["end"],
                        speaker=None,  # Whisperは話者分離非対応
                        text=seg["text"].strip(),
                    )
                )

            # 動画の長さを取得
            duration = self.ffmpeg.get_video_duration(audio_path)

            return Transcription(
                video_filename=video_filename,
                duration_sec=duration,
                segments=segments,
            )

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise STTError(f"音声認識に失敗しました: {e}")
