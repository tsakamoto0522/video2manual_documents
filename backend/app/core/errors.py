"""
Custom exceptions for the application.
"""


class VideoManualGeneratorError(Exception):
    """Base exception for all application errors."""

    pass


class VideoProcessingError(VideoManualGeneratorError):
    """動画処理中のエラー"""

    pass


class STTError(VideoManualGeneratorError):
    """音声認識エラー"""

    pass


class SceneDetectionError(VideoManualGeneratorError):
    """シーン検出エラー"""

    pass


class TemplateError(VideoManualGeneratorError):
    """テンプレート処理エラー"""

    pass


class ExportError(VideoManualGeneratorError):
    """エクスポートエラー"""

    pass


class ValidationError(VideoManualGeneratorError):
    """バリデーションエラー"""

    pass
