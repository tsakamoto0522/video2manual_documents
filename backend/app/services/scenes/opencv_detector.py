"""
OpenCV-based scene detection implementation.
"""
import asyncio
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from app.core import SceneDetectionError, logger, settings
from app.models import SceneDetectionResult, SceneInfo
from app.utils import FFmpegWrapper

from .base import SceneDetectionStrategy


class OpenCVSceneDetector(SceneDetectionStrategy):
    """OpenCVを使用したシーン検出実装"""

    def __init__(
        self,
        threshold: Optional[float] = None,
        min_scene_duration: Optional[float] = None,
        method: Optional[str] = None,
    ):
        """
        Initialize OpenCV scene detector.

        Args:
            threshold: Scene change threshold (0-100)
            min_scene_duration: Minimum scene duration in seconds
            method: Detection method ('histogram' or 'ssim')
        """
        self.threshold = threshold or settings.scene_threshold
        self.min_scene_duration = min_scene_duration or settings.min_scene_duration_sec
        self.method = method or settings.scene_detection_method
        self.ffmpeg = FFmpegWrapper()

    async def detect_scenes(self, video_path: Path, output_dir: Path) -> SceneDetectionResult:
        """シーン検出を実行"""
        logger.info(
            f"Starting scene detection for {video_path.name} "
            f"(method={self.method}, threshold={self.threshold})"
        )

        # 非同期実行のため別スレッドで実行
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._detect_scenes_sync, video_path, output_dir
        )

        logger.info(f"Scene detection completed: {len(result.scenes)} scenes detected")
        return result

    def _detect_scenes_sync(self, video_path: Path, output_dir: Path) -> SceneDetectionResult:
        """同期的なシーン検出処理"""
        output_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise SceneDetectionError(f"動画を開けませんでした: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        min_frames = int(self.min_scene_duration * fps)

        scenes: list[SceneInfo] = []
        prev_frame: Optional[np.ndarray] = None
        frame_idx = 0
        last_scene_frame = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 最小シーン間隔チェック
                if frame_idx - last_scene_frame < min_frames:
                    frame_idx += 1
                    continue

                if prev_frame is not None:
                    # シーン変化を検出
                    is_scene_change = self._detect_change(prev_frame, frame)

                    if is_scene_change:
                        timestamp = frame_idx / fps
                        frame_path = output_dir / f"scene_{len(scenes):04d}_{timestamp:.2f}s.jpg"

                        # キーフレームを保存
                        cv2.imwrite(str(frame_path), frame)

                        # 相対パスを計算（クロスプラットフォーム対応）
                        try:
                            relative_path = frame_path.relative_to(Path.cwd())
                        except ValueError:
                            # relative_to が失敗する場合は絶対パスを使用
                            relative_path = frame_path

                        scenes.append(
                            SceneInfo(
                                time=timestamp,
                                frame_path=str(relative_path),
                            )
                        )

                        last_scene_frame = frame_idx
                        logger.debug(f"Scene change detected at {timestamp:.2f}s")

                prev_frame = frame.copy()
                frame_idx += 1

        finally:
            cap.release()

        # 最初のフレームを追加 (もし検出されていなければ)
        if not scenes or scenes[0].time > 0:
            first_frame_path = output_dir / "scene_0000_0.00s.jpg"
            cap = cv2.VideoCapture(str(video_path))
            ret, first_frame = cap.read()
            if ret:
                cv2.imwrite(str(first_frame_path), first_frame)

                # 相対パスを計算（クロスプラットフォーム対応）
                try:
                    relative_path = first_frame_path.relative_to(Path.cwd())
                except ValueError:
                    # relative_to が失敗する場合は絶対パスを使用
                    relative_path = first_frame_path

                scenes.insert(
                    0,
                    SceneInfo(
                        time=0.0,
                        frame_path=str(relative_path),
                    ),
                )
            cap.release()

        return SceneDetectionResult(
            video_filename=video_path.name,
            scenes=scenes,
        )

    def _detect_change(self, frame1: np.ndarray, frame2: np.ndarray) -> bool:
        """2フレーム間の変化を検出"""
        if self.method == "histogram":
            return self._histogram_diff(frame1, frame2) > self.threshold
        elif self.method == "ssim":
            return self._ssim_diff(frame1, frame2) < (100 - self.threshold)
        else:
            raise SceneDetectionError(f"Unknown detection method: {self.method}")

    def _histogram_diff(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """ヒストグラム差分による変化検出"""
        # グレースケール変換
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # ヒストグラム計算
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])

        # 正規化
        cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        # 相関係数を計算 (0-1、1が最も類似)
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        # 差分に変換 (0-100、100が最も異なる)
        diff = (1.0 - correlation) * 100
        return diff

    def _ssim_diff(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """構造的類似性による変化検出 (簡易版)"""
        # グレースケール変換
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # 平均と標準偏差
        mean1, std1 = cv2.meanStdDev(gray1)
        mean2, std2 = cv2.meanStdDev(gray2)

        # 簡易的な類似度計算
        mean_diff = abs(float(mean1[0]) - float(mean2[0]))
        std_diff = abs(float(std1[0]) - float(std2[0]))

        # 0-100スケールに変換
        similarity = max(0, 100 - (mean_diff + std_diff) / 2)
        return similarity
