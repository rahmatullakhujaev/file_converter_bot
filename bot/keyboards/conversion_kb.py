import uuid
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

_heic_store: dict[str, str] = {}

def store_heic_file_id(file_id: str) -> str:
    key = uuid.uuid4().hex[:16]
    _heic_store[key] = file_id
    return key

def pop_heic_file_id(key: str) -> str | None:
    return _heic_store.pop(key, None)

def heic_choice_keyboard(file_id: str) -> InlineKeyboardMarkup:
    key = store_heic_file_id(file_id)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🖼 Convert to JPG", callback_data=f"heic_jpg:{key}"),
        InlineKeyboardButton(text="📄 Convert to PDF", callback_data=f"heic_pdf:{key}"),
    )
    return builder.as_markup()

def add_more_images_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Done – merge to PDF", callback_data="img_done"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="img_cancel"),
    )
    return builder.as_markup()
