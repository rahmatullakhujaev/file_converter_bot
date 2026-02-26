"""Central configuration – loaded once at startup."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Required environment variable '{key}' is missing.")
    return value


@dataclass(frozen=True)
class Config:
    # Telegram
    bot_token: str = field(default_factory=lambda: _require("BOT_TOKEN"))
    bot_webhook_host: str = field(default_factory=lambda: os.getenv("BOT_WEBHOOK_HOST", ""))

    # PostgreSQL
    postgres_host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "db"))
    postgres_port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    postgres_db: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "filebot"))
    postgres_user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "filebot"))
    postgres_password: str = field(default_factory=lambda: _require("POSTGRES_PASSWORD"))

    # App
    max_file_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE_MB", "50")))
    temp_dir: str = field(default_factory=lambda: os.getenv("TEMP_DIR", "/tmp/filebot"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Rate limiting
    rate_limit_calls: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_CALLS", "5")))
    rate_limit_period: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PERIOD", "60")))

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


config = Config()
