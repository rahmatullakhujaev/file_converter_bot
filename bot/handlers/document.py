from __future__ import annotations
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards.conversion_kb import heic_choice_keyboard, add_more_images_keyboard, pop_heic_file_id
from config import config
from database.models.file_record import ConversionType
from services.conversion_service import ConversionService
from utils.file_helpers import MIME_TO_EXT, SUPPORTED_INPUT_TYPES, file_size_ok
from utils.logger import log

router = Router()
_image_batches: dict[int, list[tuple[str, str, int]]] = {}

def _ext_from_doc(doc) -> str:
    if doc.mime_type and doc.mime_type in MIME_TO_EXT:
        return MIME_TO_EXT[doc.mime_type]
    return Path(doc.file_name or "file.bin").suffix.lower()

@router.message(F.document)
async def handle_document(message: Message, session: AsyncSession, bot: Bot) -> None:
    doc = message.document
    user_id = message.from_user.id
    if not file_size_ok(doc.file_size):
        await message.answer(f"❌ File too large. Maximum size is {config.max_file_size_mb} MB.")
        return
    ext = _ext_from_doc(doc)
    conversion_key = SUPPORTED_INPUT_TYPES.get(ext)
    if conversion_key is None:
        await message.answer(
            f"❌ Unsupported file type `{ext}`.\nSupported: `.docx`, `.doc`, `.pptx`, `.ppt`, `.jpg`, `.png`, `.heic`",
            parse_mode="Markdown",
        )
        return
    log.info("document.received", ext=ext, size=doc.file_size, user_id=user_id)
    if ext == ".heic":
        await message.answer(
            "📷 I received your HEIC file. What format would you like?",
            reply_markup=heic_choice_keyboard(doc.file_id),
        )
        return
    if ext in (".jpg", ".jpeg", ".png"):
        batch = _image_batches.setdefault(user_id, [])
        batch.append((doc.file_id, doc.file_name or f"image{ext}", doc.file_size))
        await message.answer(
            f"🖼 Image {len(batch)} received.\nSend more images to merge, or tap the button below.",
            reply_markup=add_more_images_keyboard(),
        )
        return
    svc = ConversionService(session, bot)
    await svc.handle(
        message,
        file_id=doc.file_id,
        filename=doc.file_name or f"file{ext}",
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        conversion_type=ConversionType(conversion_key),
    )

@router.callback_query(F.data.startswith("heic_jpg:"))
async def cb_heic_to_jpg(call: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    await call.answer()
    file_id = pop_heic_file_id(call.data.split(":", 1)[1])
    if not file_id:
        await call.message.edit_text("❌ Session expired. Please resend the file.")
        return
    file_obj = await bot.get_file(file_id)
    await ConversionService(session, bot).handle(
        call.message, file_id=file_id, filename="image.heic",
        mime_type="image/heic", file_size=file_obj.file_size or 0,
        conversion_type=ConversionType.HEIC_TO_JPG,
    )
    await call.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("heic_pdf:"))
async def cb_heic_to_pdf(call: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    await call.answer()
    file_id = pop_heic_file_id(call.data.split(":", 1)[1])
    if not file_id:
        await call.message.edit_text("❌ Session expired. Please resend the file.")
        return
    file_obj = await bot.get_file(file_id)
    await ConversionService(session, bot).handle(
        call.message, file_id=file_id, filename="image.heic",
        mime_type="image/heic", file_size=file_obj.file_size or 0,
        conversion_type=ConversionType.HEIC_TO_PDF,
    )
    await call.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data == "img_done")
async def cb_img_done(call: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    await call.answer()
    batch = _image_batches.pop(call.from_user.id, [])
    if not batch:
        await call.message.edit_text("⚠️ No images found. Please resend.")
        return
    primary_id, primary_name, _ = batch[0]
    await call.message.edit_reply_markup(reply_markup=None)
    await ConversionService(session, bot).handle(
        call.message, file_id=primary_id, filename=primary_name,
        mime_type="image/jpeg", file_size=sum(s for _, _, s in batch),
        conversion_type=ConversionType.IMAGE_TO_PDF,
        extra_file_ids=[fid for fid, _, _ in batch[1:]],
    )

@router.callback_query(F.data == "img_cancel")
async def cb_img_cancel(call: CallbackQuery) -> None:
    await call.answer()
    _image_batches.pop(call.from_user.id, None)
    await call.message.edit_text("❌ Batch cancelled.")
