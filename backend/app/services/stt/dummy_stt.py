"""
Dummy STT implementation for testing without Whisper.
"""
import asyncio
from pathlib import Path

from app.core import logger
from app.models import Transcription, TranscriptionSegment
from app.utils import FFmpegWrapper

from .base import STTStrategy


class DummySTT(STTStrategy):
    """ダミー音声認識実装 (テスト用)"""

    async def transcribe(self, audio_path: Path, video_filename: str) -> Transcription:
        """ダミーの文字起こし結果を生成"""
        logger.info(f"Dummy STT: Generating fake transcription for {video_filename}")

        # 動画の長さを取得
        ffmpeg = FFmpegWrapper()
        # 音声ファイルから動画パスを推測 (実際は別途渡すべき)
        duration = 60.0  # デフォルト値

        try:
            # 実際の長さを取得する場合
            import subprocess

            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            duration = float(result.stdout.strip())
        except Exception:
            pass

        # ダミーセグメントを生成
        segments = [
            TranscriptionSegment(
                start=0.0,
                end=5.0,
                speaker=None,
                text="こんにちは、このビデオでは操作手順を説明します。",
            ),
            TranscriptionSegment(
                start=5.0,
                end=10.0,
                speaker=None,
                text="まず、画面左上のメニューボタンをクリックしてください。",
            ),
            TranscriptionSegment(
                start=10.0,
                end=15.0,
                speaker=None,
                text="次に、設定メニューから言語設定を選択します。",
            ),
            TranscriptionSegment(
                start=15.0,
                end=20.0,
                speaker=None,
                text="日本語を選択して、保存ボタンをクリックしてください。",
            ),
            TranscriptionSegment(
                start=20.0,
                end=25.0,
                speaker=None,
                text="設定が完了しました。これで操作は終了です。",
            ),
        ]

        # ダミー処理時間をシミュレート
        await asyncio.sleep(1.0)

        return Transcription(
            video_filename=video_filename,
            duration_sec=duration,
            segments=segments,
        )
