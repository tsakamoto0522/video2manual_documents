"""
Manual planning and editing endpoints.
"""
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core import logger, settings
from app.models import CaptureSelectionRequest, ManualPlan, SceneDetectionResult, Transcription
from app.services.capture import ManualPlanner

router = APIRouter()


class CreatePlanRequest(BaseModel):
    """マニュアル計画作成リクエスト"""

    video_id: str
    title: Optional[str] = None


@router.post("/plan", response_model=ManualPlan)
async def create_manual_plan(request: CreatePlanRequest) -> ManualPlan:
    """
    Create manual plan from transcription and scene detection.

    Args:
        request: CreatePlanRequest with video_id

    Returns:
        ManualPlan with auto-generated steps
    """
    video_id = request.video_id
    logger.info(f"Creating manual plan for video: {video_id}")

    # 文字起こし結果を取得
    transcription_path = settings.intermediate_dir / video_id / "transcription.json"
    if not transcription_path.exists():
        raise HTTPException(status_code=404, detail="文字起こし結果が見つかりません")

    transcription = Transcription.model_validate_json(
        transcription_path.read_text(encoding="utf-8")
    )

    # シーン検出結果を取得
    scenes_path = settings.intermediate_dir / video_id / "scenes.json"
    if not scenes_path.exists():
        raise HTTPException(status_code=404, detail="シーン検出結果が見つかりません")

    scene_result = SceneDetectionResult.model_validate_json(
        scenes_path.read_text(encoding="utf-8")
    )

    # マニュアル計画を作成
    planner = ManualPlanner()
    plan = await planner.create_plan(transcription, scene_result, request.title)

    # 結果を保存
    output_path = settings.intermediate_dir / video_id / "manual_plan.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    logger.info(f"Manual plan created: {len(plan.steps)} steps")

    return plan


@router.post("/apply-selection", response_model=ManualPlan)
async def apply_capture_selection(request: CaptureSelectionRequest) -> ManualPlan:
    """
    Apply user's capture selection to manual plan.

    Args:
        request: CaptureSelectionRequest with selections

    Returns:
        Updated ManualPlan
    """
    video_id = request.video_id
    logger.info(f"Applying capture selection for video: {video_id}")

    # マニュアル計画を取得
    plan_path = settings.intermediate_dir / video_id / "manual_plan.json"
    if not plan_path.exists():
        raise HTTPException(status_code=404, detail="マニュアル計画が見つかりません")

    plan = ManualPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))

    # 選択を適用
    for step_index, selected in request.selections.items():
        if 0 <= step_index < len(plan.steps):
            plan.steps[step_index].selected = selected

    # 更新を保存
    plan_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    logger.info(f"Capture selection applied: {len(request.selections)} changes")

    return plan


@router.get("/plan/{video_id}", response_model=ManualPlan)
async def get_manual_plan(video_id: str) -> ManualPlan:
    """
    Get manual plan.

    Args:
        video_id: Video UUID

    Returns:
        ManualPlan data
    """
    plan_path = settings.intermediate_dir / video_id / "manual_plan.json"
    if not plan_path.exists():
        raise HTTPException(status_code=404, detail="マニュアル計画が見つかりません")

    return ManualPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))


@router.put("/plan/{video_id}", response_model=ManualPlan)
async def update_manual_plan(video_id: str, plan: ManualPlan) -> ManualPlan:
    """
    Update manual plan (for manual editing).

    Args:
        video_id: Video UUID
        plan: Updated ManualPlan

    Returns:
        Updated ManualPlan
    """
    logger.info(f"Updating manual plan for video: {video_id}")

    # 保存
    plan_path = settings.intermediate_dir / video_id / "manual_plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    logger.info("Manual plan updated")

    return plan
