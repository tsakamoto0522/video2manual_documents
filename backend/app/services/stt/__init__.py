"""
STT (Speech-to-Text) services.
"""
from app.core import settings

from .base import STTStrategy
from .dummy_stt import DummySTT
from .gpt4o_stt import GPT4oSTT
from .whisper_stt import WhisperSTT

__all__ = ["STTStrategy", "WhisperSTT", "GPT4oSTT", "DummySTT", "get_stt_engine"]


def get_stt_engine() -> STTStrategy:
    """設定に基づいてSTTエンジンを取得"""
    if settings.stt_engine == "whisper":
        return WhisperSTT()
    elif settings.stt_engine == "gpt4o":
        return GPT4oSTT()
    elif settings.stt_engine == "dummy":
        return DummySTT()
    else:
        raise ValueError(f"Unknown STT engine: {settings.stt_engine}")
