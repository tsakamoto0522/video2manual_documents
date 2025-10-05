"""
Export endpoints (Markdown, PDF).
"""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core import logger, settings
from app.models import ExportRequest, ExportResponse, ManualPlan
from app.services.export import PDFExporter
from app.services.template import TemplateRenderer

router = APIRouter()


@router.post("/markdown", response_model=ExportResponse)
async def export_markdown(request: ExportRequest) -> ExportResponse:
    """
    Export manual as Markdown.

    Args:
        request: ExportRequest with video_id

    Returns:
        ExportResponse with output path
    """
    video_id = request.video_id
    logger.info(f"Exporting manual as Markdown for video: {video_id}")

    # マニュアル計画を取得
    plan_path = settings.intermediate_dir / video_id / "manual_plan.json"
    if not plan_path.exists():
        raise HTTPException(status_code=404, detail="マニュアル計画が見つかりません")

    plan = ManualPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))

    # テンプレートレンダリング
    renderer = TemplateRenderer()
    # デフォルトテンプレートが存在しない場合は作成
    renderer.create_default_template()

    output_path = settings.export_dir / video_id / "manual.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await renderer.render(plan, request.template, output_path)

    logger.info(f"Markdown exported: {output_path}")

    return ExportResponse(
        video_id=video_id,
        format="markdown",
        output_path=str(output_path),
        download_url=f"/export/download/{video_id}/manual.md",
    )


@router.post("/pdf", response_model=ExportResponse)
async def export_pdf(request: ExportRequest) -> ExportResponse:
    """
    Export manual as PDF.

    Args:
        request: ExportRequest with video_id

    Returns:
        ExportResponse with output path
    """
    video_id = request.video_id
    logger.info(f"Exporting manual as PDF for video: {video_id}")

    # まず Markdown を生成
    md_path = settings.export_dir / video_id / "manual.md"
    if not md_path.exists():
        # Markdown が存在しない場合は先に生成
        await export_markdown(request)

    # PDF に変換
    pdf_exporter = PDFExporter()
    pdf_path = settings.export_dir / video_id / "manual.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    await pdf_exporter.markdown_to_pdf(md_path, pdf_path)

    logger.info(f"PDF exported: {pdf_path}")

    return ExportResponse(
        video_id=video_id,
        format="pdf",
        output_path=str(pdf_path),
        download_url=f"/export/download/{video_id}/manual.pdf",
    )


@router.get("/download/{video_id}/{filename}")
async def download_export(video_id: str, filename: str) -> FileResponse:
    """
    Download exported manual file.

    Args:
        video_id: Video UUID
        filename: Export filename

    Returns:
        FileResponse with exported file
    """
    export_path = settings.export_dir / video_id / filename
    if not export_path.exists():
        raise HTTPException(status_code=404, detail="エクスポートファイルが見つかりません")

    return FileResponse(
        path=export_path,
        filename=filename,
        media_type="application/octet-stream",
    )
