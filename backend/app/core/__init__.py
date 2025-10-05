"""
Core module exports.
"""
from .config import settings
from .errors import (
    ExportError,
    SceneDetectionError,
    STTError,
    TemplateError,
    ValidationError,
    VideoManualGeneratorError,
    VideoProcessingError,
)
from .logger import logger

__all__ = [
    "settings",
    "logger",
    "VideoManualGeneratorError",
    "VideoProcessingError",
    "STTError",
    "SceneDetectionError",
    "TemplateError",
    "ExportError",
    "ValidationError",
]
