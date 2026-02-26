"""Handle photos sent directly (not as documents)."""
from __future__ import annotations

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.conversion_kb import add_more_images_keyboard
from utils.logger import log

router = Router()

_photo_batches: dict[int, list[tuple[str, int]]] = {}


@router.message(F.photo)
async def handle_photo(message: Message, session: AsyncSession, bot: Bot) -> None:
    """
    When users send a photo directly (compressed), treat as JPG.
    Use the largest available resolution.
    """
    photo = message.photo[-1]  # largest size
    user_id = message.from_user.id

    batch = _photo_batches.setdefault(user_id, [])
    batch.append((photo.file_id, photo.file_size or 0))
    count = len(batch)

    log.info("photo.received", count=count, user_id=user_id)
    await message.answer(
        f"🖼 Photo {count} received.\n"
        "Send more photos to merge, or tap the button below.",
        reply_markup=add_more_images_keyboard(),
    )
