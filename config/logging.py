import logging
import os
import sys
from types import FrameType
from typing import cast

from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(),
        )


def configure_loguru():
    log_file_path = os.path.join(BASE_DIR, "logs/ops_spider.log")
    err_log_file_path = os.path.join(BASE_DIR, "logs/ops_spider.err.log")

    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "level": "INFO",
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | "
                          "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            },
            {"sink": log_file_path, "rotation": "500 MB", "encoding": "utf-8"},
            {"sink": err_log_file_path, "serialize": True, "level": "ERROR", "rotation": "500 MB", "encoding": "utf-8"},
        ],
    )
