"""
Manual planning logic - merging transcription segments with scene changes.
"""
from typing import Optional

from app.core import logger, settings
from app.models import ManualPlan, ManualStep, SceneDetectionResult, Transcription


class ManualPlanner:
    """マニュアル手順の自動計画"""

    def __init__(
        self,
        auto_merge_threshold: Optional[float] = None,
        min_step_duration: Optional[float] = None,
    ):
        """
        Initialize manual planner.

        Args:
            auto_merge_threshold: Maximum gap between segments to auto-merge
            min_step_duration: Minimum duration for a step
        """
        self.auto_merge_threshold = auto_merge_threshold or settings.auto_merge_threshold_sec
        self.min_step_duration = min_step_duration or settings.min_step_duration_sec

    async def create_plan(
        self,
        transcription: Transcription,
        scene_result: SceneDetectionResult,
        manual_title: Optional[str] = None,
    ) -> ManualPlan:
        """
        Create manual plan by merging transcription and scene detection.

        Args:
            transcription: Speech-to-text result
            scene_result: Scene detection result
            manual_title: Manual title (optional)

        Returns:
            ManualPlan with steps
        """
        logger.info("Creating manual plan from transcription and scenes")

        # シーンタイムスタンプをセット化
        scene_times = {scene.time for scene in scene_result.scenes}

        # ステップを生成
        steps: list[ManualStep] = []
        current_step: Optional[dict] = None

        for i, segment in enumerate(transcription.segments):
            # シーン切替がこのセグメント内にあるか確認
            has_scene_change = any(
                segment.start <= scene_time <= segment.end for scene_time in scene_times
            )

            # 新しいステップを開始するか判定
            should_start_new = (
                current_step is None  # 最初
                or has_scene_change  # シーン切替
                or (
                    segment.start - current_step["end"] > self.auto_merge_threshold
                )  # 間隔が大きい
            )

            if should_start_new:
                # 現在のステップを完了
                if current_step is not None:
                    steps.append(self._finalize_step(current_step, scene_result))

                # 新しいステップを開始
                current_step = {
                    "start": segment.start,
                    "end": segment.end,
                    "texts": [segment.text],
                }
            else:
                # 既存のステップに追加
                current_step["end"] = segment.end
                current_step["texts"].append(segment.text)

        # 最後のステップを追加
        if current_step is not None:
            steps.append(self._finalize_step(current_step, scene_result))

        # タイトル生成
        if manual_title is None:
            manual_title = f"{transcription.video_filename} 操作マニュアル"

        plan = ManualPlan(
            title=manual_title,
            source_video=transcription.video_filename,
            steps=steps,
        )

        logger.info(f"Manual plan created with {len(steps)} steps")
        return plan

    def _finalize_step(self, step_data: dict, scene_result: SceneDetectionResult) -> ManualStep:
        """ステップデータを ManualStep に変換"""
        # ナレーションを結合
        narration = " ".join(step_data["texts"])

        # タイトルを生成 (最初の文または最初の20文字)
        title = step_data["texts"][0]
        if len(title) > 30:
            title = title[:30] + "..."

        # 対応するキャプチャ画像を検索
        image = self._find_matching_image(step_data["start"], step_data["end"], scene_result)

        return ManualStep(
            title=title,
            narration=narration,
            note=None,  # 後で手動で追加可能
            image=image,
            start=step_data["start"],
            end=step_data["end"],
            selected=True,  # デフォルトで採用
        )

    def _find_matching_image(
        self, start: float, end: float, scene_result: SceneDetectionResult
    ) -> Optional[str]:
        """ステップの時間範囲に対応するキャプチャ画像を検索"""
        # ステップの中間時刻
        mid_time = (start + end) / 2

        # 最も近いシーンを検索
        best_scene = None
        min_diff = float("inf")

        for scene in scene_result.scenes:
            # ステップの範囲内にあるシーンを優先
            if start <= scene.time <= end:
                diff = abs(scene.time - mid_time)
                if diff < min_diff:
                    min_diff = diff
                    best_scene = scene

        # 範囲内に見つからない場合は、最も近いシーンを使用
        if best_scene is None:
            for scene in scene_result.scenes:
                diff = abs(scene.time - mid_time)
                if diff < min_diff:
                    min_diff = diff
                    best_scene = scene

        return best_scene.frame_path if best_scene else None
