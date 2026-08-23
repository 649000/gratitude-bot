import logging

from aws_lambda_powertools import Logger

from app.config import settings

_logger: Logger | None = None


def get_logger() -> Logger:
    global _logger
    if _logger is None:
        _logger = Logger(
            service="webhook",
            level=getattr(logging, settings.log_level.upper()),
        )
    return _logger


def configure_logging() -> None:
    get_logger()
