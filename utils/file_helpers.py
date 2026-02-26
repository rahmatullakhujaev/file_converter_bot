"""Temp-file helpers and cleanup utilities."""
from __future__ import annotations

import os
import uuid
import asyncio
import aiofiles
from pathlib import Path
from config import config
from utils.logger import log


def make_temp_path(suffix: str = "") -> Path:
    os.makedirs(config.temp_dir, exist_ok=True)
    return Path(config.temp_dir) / f"{uuid.uuid4().hex}{suffix}"


async def save_bytes(data: bytes, suffix: str = "") -> Path:
    path = make_temp_path(suffix)
    async with aiofiles.open(path, "wb") as f:
        await f.write(data)
    return path


async def cleanup(*paths: Path) -> None:
    for p in paths:
        try:
            if p and p.exists():
                p.unlink()
        except Exception as exc:
            log.warning("cleanup_failed", path=str(p), error=str(exc))


def file_size_ok(size_bytes: int) -> bool:
    return size_bytes <= config.max_file_size_bytes


SUPPORTED_INPUT_TYPES: dict[str, str] = {
    # ext → conversion type key
    ".docx": "docx_to_pdf",
    ".doc":  "docx_to_pdf",
    ".pptx": "pptx_to_pdf",
    ".ppt":  "pptx_to_pdf",
    ".jpg":  "image_to_pdf",
    ".jpeg": "image_to_pdf",
    ".png":  "image_to_pdf",
    ".heic": "heic_to_pdf",   # also offered: heic_to_jpg
}

MIME_TO_EXT: dict[str, str] = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.ms-powerpoint": ".ppt",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/heic": ".heic",
    "image/heif": ".heic",
}
