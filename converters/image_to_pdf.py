"""JPG / PNG (and pre-converted HEIC) → merged PDF converter."""
from __future__ import annotations

from pathlib import Path
from PIL import Image

from converters.base import BaseConverter
from utils.file_helpers import make_temp_path
from utils.logger import log


class ImageToPdfConverter(BaseConverter):
    name = "image_to_pdf"

    async def convert(self, input_path: Path, **kwargs) -> Path:
        """
        Accepts either a single image path or a list via kwargs['extra_paths'].
        All images are merged into a single PDF, one page per image.
        """
        paths: list[Path] = [input_path] + list(kwargs.get("extra_paths", []))
        output_path = make_temp_path(".pdf")

        log.info("image_to_pdf.start", count=len(paths))

        images: list[Image.Image] = []
        for p in paths:
            img = Image.open(p).convert("RGB")
            images.append(img)

        if not images:
            raise ValueError("No images to convert.")

        first, rest = images[0], images[1:]
        first.save(
            output_path,
            "PDF",
            save_all=True,
            append_images=rest,
            resolution=150,
        )

        log.info("image_to_pdf.done", output=output_path.name, pages=len(images))
        return output_path
