"""Structured logging setup."""
import logging
import structlog
from config import config


def setup_logging() -> None:
    logging.basicConfig(
        level=config.log_level,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("/app/logs/bot.log", encoding="utf-8"),
        ],
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer() if config.log_level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(config.log_level)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
    )


log = structlog.get_logger()
