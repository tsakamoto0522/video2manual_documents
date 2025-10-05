"""
Application configuration using Pydantic Settings.
"""
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)

    # Storage
    data_dir: Path = Field(default=Path("./data"))
    upload_dir: Path = Field(default=Path("./data/uploads"))
    capture_dir: Path = Field(default=Path("./data/captures"))
    intermediate_dir: Path = Field(default=Path("./data/intermediate"))
    export_dir: Path = Field(default=Path("./data/exports"))

    # Video
    max_video_size_mb: int = Field(default=500)
    allowed_video_extensions: str = Field(default="mp4,mov,avi,mkv")

    # Scene Detection
    scene_threshold: float = Field(default=30.0, ge=0.0, le=100.0)
    min_scene_duration_sec: float = Field(default=2.0, ge=0.1)
    scene_detection_method: Literal["histogram", "ssim"] = Field(default="histogram")

    # STT
    stt_engine: Literal["whisper", "gpt4o", "dummy"] = Field(default="gpt4o")
    whisper_model: Literal["tiny", "base", "small", "medium", "large"] = Field(default="base")
    whisper_device: Literal["cpu", "cuda"] = Field(default="cpu")
    whisper_language: str = Field(default="ja")

    # Manual Generation
    auto_merge_threshold_sec: float = Field(default=5.0, ge=0.0)
    min_step_duration_sec: float = Field(default=3.0, ge=0.0)

    # Export
    pdf_engine: Literal["playwright", "weasyprint"] = Field(default="playwright")
    template_dir: Path = Field(default=Path("./templates"))
    default_template: str = Field(default="manual_default.md.j2")

    # OpenAI API
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-5")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(default="json")

    def get_video_extensions(self) -> list[str]:
        """許可される動画拡張子リストを取得"""
        return [ext.strip().lower() for ext in self.allowed_video_extensions.split(",")]

    def ensure_directories(self) -> None:
        """必要なディレクトリを作成"""
        for dir_path in [
            self.data_dir,
            self.upload_dir,
            self.capture_dir,
            self.intermediate_dir,
            self.export_dir,
            self.template_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
