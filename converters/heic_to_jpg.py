"""HEIC → JPG converter."""
from __future__ import annotations

from pathlib import Path
from PIL import Image
import pillow_heif

from converters.base import BaseConverter
from utils.file_helpers import make_temp_path
from utils.logger import log

pillow_heif.register_heif_opener()


class HeicToJpgConverter(BaseConverter):
    name = "heic_to_jpg"

    async def convert(self, input_path: Path, **kwargs) -> Path:
        output_path = make_temp_path(".jpg")

        log.info("heic_to_jpg.start", file=input_path.name)
        img = Image.open(input_path).convert("RGB")
        img.save(output_path, "JPEG", quality=92)
        log.info("heic_to_jpg.done", output=output_path.name)
        return output_path
