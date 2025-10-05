"""
Base interface for STT (Speech-to-Text) strategies.
"""
from abc import ABC, abstractmethod
from pathlib import Path

from app.models import Transcription


class STTStrategy(ABC):
    """音声認識の基底クラス (Strategy パターン)"""

    @abstractmethod
    async def transcribe(self, audio_path: Path, video_filename: str) -> Transcription:
        """
        Transcribe audio to text with timestamps.

        Args:
            audio_path: Path to audio file
            video_filename: Original video filename for reference

        Returns:
            Transcription with segments
        """
        pass
