"""
FFmpeg wrapper utilities for video processing.
"""
import subprocess
from pathlib import Path
from typing import Optional

from app.core import VideoProcessingError, logger


class FFmpegWrapper:
    """FFmpegのラッパークラス"""

    @staticmethod
    def get_video_duration(video_path: Path) -> float:
        """
        Get video duration in seconds.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds

        Raises:
            VideoProcessingError: If ffprobe fails
        """
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            duration = float(result.stdout.strip())
            logger.info(f"Video duration: {duration}s for {video_path.name}")
            return duration
        except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired) as e:
            logger.error(f"Failed to get video duration: {e}")
            raise VideoProcessingError(f"動画の長さを取得できませんでした: {e}")

    @staticmethod
    def extract_audio(video_path: Path, output_path: Path, sample_rate: int = 16000) -> Path:
        """
        Extract audio from video.

        Args:
            video_path: Path to input video
            output_path: Path to output audio file
            sample_rate: Audio sample rate (default: 16000 for Whisper)

        Returns:
            Path to extracted audio file

        Raises:
            VideoProcessingError: If extraction fails
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cmd = [
                "ffmpeg",
                "-i",
                str(video_path),
                "-vn",  # 映像を除外
                "-acodec",
                "pcm_s16le",
                "-ar",
                str(sample_rate),
                "-ac",
                "1",  # モノラル
                "-y",  # 上書き
                str(output_path),
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=300)
            logger.info(f"Audio extracted: {output_path}")
            return output_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(f"Failed to extract audio: {e}")
            raise VideoProcessingError(f"音声抽出に失敗しました: {e}")

    @staticmethod
    def extract_frame(
        video_path: Path, timestamp: float, output_path: Path, width: Optional[int] = 1280
    ) -> Path:
        """
        Extract a single frame at specified timestamp.

        Args:
            video_path: Path to video file
            timestamp: Time in seconds
            output_path: Path to output image
            width: Resize width (maintains aspect ratio)

        Returns:
            Path to extracted frame

        Raises:
            VideoProcessingError: If extraction fails
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cmd = [
                "ffmpeg",
                "-ss",
                str(timestamp),
                "-i",
                str(video_path),
                "-vframes",
                "1",
                "-q:v",
                "2",  # 高品質
            ]
            if width:
                cmd.extend(["-vf", f"scale={width}:-1"])
            cmd.extend(["-y", str(output_path)])

            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
            logger.debug(f"Frame extracted at {timestamp}s: {output_path}")
            return output_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(f"Failed to extract frame at {timestamp}s: {e}")
            raise VideoProcessingError(f"フレーム抽出に失敗しました: {e}")

    @staticmethod
    def get_video_info(video_path: Path) -> dict[str, any]:
        """
        Get comprehensive video information.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata
        """
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(video_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            import json

            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise VideoProcessingError(f"動画情報の取得に失敗しました: {e}")
