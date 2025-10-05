"""
Scene detection services.
"""
from .base import SceneDetectionStrategy
from .opencv_detector import OpenCVSceneDetector

__all__ = ["SceneDetectionStrategy", "OpenCVSceneDetector"]
