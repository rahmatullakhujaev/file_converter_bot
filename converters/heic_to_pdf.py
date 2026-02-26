"""HEIC → PDF converter (decodes HEIC first, then reuses ImageToPdfConverter)."""
from __future__ import annotations

from pathlib import Path
from PIL import Image
import pillow_heif

from converters.base import BaseConverter
from converters.image_to_pdf import ImageToPdfConverter
from utils.file_helpers import make_temp_path
from utils.logger import log

pillow_heif.register_heif_opener()


class HeicToPdfConverter(BaseConverter):
    name = "heic_to_pdf"

    async def convert(self, input_path: Path, **kwargs) -> Path:
        log.info("heic_to_pdf.start", file=input_path.name)

        # Convert HEIC → temporary PNG first, then hand off to ImageToPdfConverter
        png_path = make_temp_path(".png")
        img = Image.open(input_path).convert("RGB")
        img.save(png_path, "PNG")

        extra_heic: list[Path] = kwargs.get("extra_paths", [])
        extra_pngs: list[Path] = []
        for heic in extra_heic:
            p = make_temp_path(".png")
            Image.open(heic).convert("RGB").save(p, "PNG")
            extra_pngs.append(p)

        output_path = await ImageToPdfConverter().convert(
            png_path, extra_paths=extra_pngs
        )

        # Clean up intermediary PNGs
        png_path.unlink(missing_ok=True)
        for p in extra_pngs:
            p.unlink(missing_ok=True)

        log.info("heic_to_pdf.done")
        return output_path
