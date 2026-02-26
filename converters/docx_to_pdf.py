"""DOCX → PDF converter using LibreOffice headless."""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from converters.base import BaseConverter
from utils.file_helpers import make_temp_path
from utils.logger import log


class DocxToPdfConverter(BaseConverter):
    name = "docx_to_pdf"

    async def convert(self, input_path: Path, **kwargs) -> Path:
        output_dir = Path(input_path.parent)
        cmd = [
            "libreoffice",
            "--headless",
            "--norestore",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(input_path),
        ]

        log.info("docx_to_pdf.start", file=input_path.name)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(
                f"LibreOffice failed (code {proc.returncode}): {stderr.decode()}"
            )

        # LibreOffice names output <stem>.pdf in the outdir
        output_path = output_dir / f"{input_path.stem}.pdf"
        if not output_path.exists():
            raise FileNotFoundError(f"Expected output not found: {output_path}")

        log.info("docx_to_pdf.done", output=output_path.name)
        return output_path
