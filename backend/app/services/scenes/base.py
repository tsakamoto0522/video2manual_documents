"""
Base interface for scene detection strategies.
"""
from abc import ABC, abstractmethod
from pathlib import Path

from app.models import SceneDetectionResult


class SceneDetectionStrategy(ABC):
    """シーン検出の基底クラス (Strategy パターン)"""

    @abstractmethod
    async def detect_scenes(self, video_path: Path, output_dir: Path) -> SceneDetectionResult:
        """
        Detect scene changes in video and extract keyframes.

        Args:
            video_path: Path to video file
            output_dir: Directory to save captured frames

        Returns:
            SceneDetectionResult with scene timestamps and frame paths
        """
        pass
