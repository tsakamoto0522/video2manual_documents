"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core import VideoManualGeneratorError, logger, settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションライフサイクル管理"""
    # Startup
    logger.info("Starting Video Manual Generator API...")
    settings.ensure_directories()
    logger.info(f"Data directories initialized at {settings.data_dir}")

    yield

    # Shutdown
    logger.info("Shutting down Video Manual Generator API...")


app = FastAPI(
    title="Video Manual Generator API",
    description="Video から自動マニュアル生成システム",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS設定 (開発用)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite/React default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# グローバルエラーハンドラー
@app.exception_handler(VideoManualGeneratorError)
async def video_manual_error_handler(request, exc: VideoManualGeneratorError):
    """アプリケーション固有のエラーハンドラー"""
    logger.error(f"Application error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": exc.__class__.__name__},
    )


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "service": "Video Manual Generator",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """詳細ヘルスチェック"""
    return {
        "status": "healthy",
        "config": {
            "stt_engine": settings.stt_engine,
            "scene_detection": settings.scene_detection_method,
            "pdf_engine": settings.pdf_engine,
        },
    }


# 静的ファイル配信の設定
app.mount("/data", StaticFiles(directory=str(settings.data_dir)), name="data")

# ルートの登録
from app.routes import export, manual, process, videos

app.include_router(videos.router, prefix="/videos", tags=["videos"])
app.include_router(process.router, prefix="/process", tags=["process"])
app.include_router(manual.router, prefix="/manual", tags=["manual"])
app.include_router(export.router, prefix="/export", tags=["export"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
