from __future__ import annotations

import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.file_record import ConversionType
from services.conversion_service import ConversionService
from utils.logger import log

router = Router()

# { media_group_id: { "photos": [...], "task": asyncio.Task, "message": Message } }
_groups: dict[str, dict] = {}


async def _flush_group(media_group_id: str, session: AsyncSession, bot: Bot) -> None:
    await asyncio.sleep(1.5)  # wait for remaining photos in the album

    group = _groups.pop(media_group_id, None)
    if not group:
        return

    photos = group["photos"]
    message = group["message"]
    user_id = message.from_user.id

    log.info("photo.flush", count=len(photos), user_id=user_id)

    primary_id, primary_size = photos[0]
    extra_ids = [fid for fid, _ in photos[1:]]
    total_size = sum(s for _, s in photos)

    await ConversionService(session, bot).handle(
        message,
        file_id=primary_id,
        filename="photos.jpg",
        mime_type="image/jpeg",
        file_size=total_size,
        conversion_type=ConversionType.IMAGE_TO_PDF,
        extra_file_ids=extra_ids,
    )


@router.message(F.photo)
async def handle_photo(message: Message, session: AsyncSession, bot: Bot) -> None:
    photo = message.photo[-1]
    media_group_id = message.media_group_id or f"single_{message.message_id}"

    if media_group_id not in _groups:
        _groups[media_group_id] = {"photos": [], "task": None, "message": message}
        if len(_groups[media_group_id]["photos"]) == 0:
            await message.answer("⏳ Receiving photos, please wait…")

    group = _groups[media_group_id]
    group["photos"].append((photo.file_id, photo.file_size or 0))

    # Cancel previous timer and restart it
    if group["task"] and not group["task"].done():
        group["task"].cancel()

    group["task"] = asyncio.create_task(
        _flush_group(media_group_id, session, bot)
    )