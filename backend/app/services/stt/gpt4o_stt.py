"""
GPT-4o Audio Transcription implementation.
"""
import asyncio
from pathlib import Path
from typing import Optional

from openai import AsyncOpenAI

from app.core import STTError, logger, settings
from app.models import Transcription, TranscriptionSegment
from app.utils import FFmpegWrapper

from .base import STTStrategy


class GPT4oSTT(STTStrategy):
    """OpenAI GPT-4o Audioを使用した音声認識実装"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        language: Optional[str] = None,
    ):
        """
        Initialize GPT-4o STT.

        Args:
            api_key: OpenAI API key (デフォルトは設定から取得)
            language: Language code (ja/en/etc.)
        """
        self.api_key = api_key or settings.openai_api_key
        self.language = language or settings.whisper_language

        if not self.api_key:
            raise ValueError("OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定してください。")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.ffmpeg = FFmpegWrapper()

    async def transcribe(self, audio_path: Path, video_filename: str) -> Transcription:
        """音声認識を実行"""
        logger.info(
            f"Starting GPT-4o transcription for {video_filename} "
            f"(language={self.language})"
        )

        try:
            # 音声ファイルを開く
            with open(audio_path, "rb") as audio_file:
                # GPT-4o Transcriptionを実行
                # response_format="json"の場合、timestamp_granularitiesは使えない
                response = await self.client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    language=self.language if self.language != "auto" else None,
                    response_format="json"
                )

            logger.info(f"GPT-4o response received: {type(response)}")
            logger.info(f"Response attributes: {dir(response)}")

            # レスポンス内容をデバッグ出力
            if hasattr(response, 'model_dump'):
                logger.info(f"Response data: {response.model_dump()}")

            # セグメント変換
            segments = []

            # response_format="json"の場合、segmentsがない可能性があるため、
            # テキスト全体を1つのセグメントとして扱う
            if hasattr(response, 'segments') and response.segments:
                logger.info(f"Using segments from response: {len(response.segments)} segments")
                for seg in response.segments:
                    segments.append(
                        TranscriptionSegment(
                            start=seg.start,
                            end=seg.end,
                            speaker=None,
                            text=seg.text.strip(),
                        )
                    )
            else:
                # セグメント情報がない場合は、テキストを手動で分割
                logger.warning("No segments in response, using manual splitting")
                duration = self.ffmpeg.get_video_duration(audio_path)
                full_text = response.text if hasattr(response, 'text') else ""

                # 句読点や改行で分割してセグメントを作成
                import re
                sentences = re.split(r'[。．\n]+', full_text)
                sentences = [s.strip() for s in sentences if s.strip()]

                if sentences:
                    segment_duration = duration / len(sentences)
                    for i, sentence in enumerate(sentences):
                        segments.append(
                            TranscriptionSegment(
                                start=i * segment_duration,
                                end=(i + 1) * segment_duration,
                                speaker=None,
                                text=sentence,
                            )
                        )
                else:
                    # 分割できない場合は全体を1つのセグメントとする
                    segments.append(
                        TranscriptionSegment(
                            start=0.0,
                            end=duration,
                            speaker=None,
                            text=full_text,
                        )
                    )

            # 動画の長さを取得
            duration = self.ffmpeg.get_video_duration(audio_path)

            logger.info(f"GPT-4o transcription completed: {len(segments)} segments")

            return Transcription(
                video_filename=video_filename,
                duration_sec=duration,
                segments=segments,
            )

        except Exception as e:
            logger.error(f"GPT-4o transcription failed: {e}")
            raise STTError(f"音声認識に失敗しました: {e}")
