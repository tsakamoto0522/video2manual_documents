"""
Structured logging configuration.
"""
import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from .config import settings


def setup_logger(name: str = "video_manual_generator") -> logging.Logger:
    """構造化ロガーのセットアップ"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level))

    # ハンドラーが既に存在する場合はスキップ
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)

    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            timestamp=True,
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()
