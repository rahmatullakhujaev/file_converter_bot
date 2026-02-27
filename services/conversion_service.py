"""Orchestrates download → convert → save → respond pipeline."""
from __future__ import annotations

import time
from pathlib import Path

from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from converters import get_converter
from database.models.file_record import ConversionType, ConversionStatus
from database.repositories.file_repo import FileRepository
from database.repositories.user_repo import UserRepository
from utils.file_helpers import save_bytes, cleanup
from utils.logger import log


class ConversionService:
    def __init__(self, session: AsyncSession, bot: Bot) -> None:
        self.session = session
        self.bot = bot
        self.file_repo = FileRepository(session)
        self.user_repo = UserRepository(session)

    async def handle(
        self,
        message: Message,
        *,
        file_id: str,
        filename: str,
        mime_type: str | None,
        file_size: int,
        conversion_type: ConversionType,
        extra_file_ids: list[str] | None = None,
    ) -> None:
        user = message.from_user

        # Upsert user
        await self.user_repo.upsert(user)

        # Ban check
        if await self.user_repo.is_banned(user.id):
            await message.answer("⛔ You are banned from using this bot.")
            return

        ext = Path(filename).suffix.lower() or ".bin"

        record = await self.file_repo.create(
            user_id=user.id,
            original_filename=filename,
            original_extension=ext,
            original_mime_type=mime_type,
            original_size_bytes=file_size,
            telegram_file_id=file_id,
            conversion_type=conversion_type,
        )
        await self.session.commit()

        status_msg = await message.answer("⏳ Converting your file…")
        input_path: Path | None = None
        extra_paths: list[Path] = []
        output_path: Path | None = None
        start = time.monotonic()

        try:
            # Download primary file
            file_obj = await self.bot.get_file(file_id)
            file_bytes = await self.bot.download_file(file_obj.file_path)
            input_path = await save_bytes(file_bytes.read(), ext)

            # Download extra files (for batch image merge)
            for eid in (extra_file_ids or []):
                ef = await self.bot.get_file(eid)
                eb = await self.bot.download_file(ef.file_path)
                ep = await save_bytes(eb.read(), ext)
                extra_paths.append(ep)

            # Run converter
            converter = get_converter(conversion_type.value)
            output_path = await converter.convert(input_path, extra_paths=extra_paths)

            output_bytes = output_path.read_bytes()
            duration = time.monotonic() - start

            # Persist result
            out_filename = Path(filename).stem + (
                ".pdf" if "pdf" in conversion_type.value else ".jpg"
            )
            await self.file_repo.mark_success(
                record,
                output_filename=out_filename,
                output_data=output_bytes,
                duration_seconds=duration,
            )
            await self.user_repo.increment_stats(user.id, file_size)

            # Send result
            from aiogram.types import BufferedInputFile
            await message.answer_document(
                BufferedInputFile(output_bytes, filename=out_filename),
                caption=f"Converted in {duration:.1f}s",
            )
            await status_msg.delete()

        except Exception as exc:
            duration = time.monotonic() - start
            log.error("conversion_failed", error=str(exc), user_id=user.id)
            await self.file_repo.mark_failed(
                record, error_message=str(exc), duration_seconds=duration
            )
            await status_msg.edit_text(
                f"Conversion failed: {exc}\n\nPlease try again or contact support."
            )

        finally:
            await cleanup(input_path, output_path, *extra_paths)
