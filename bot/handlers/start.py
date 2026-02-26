"""Start, help, stats handlers."""
from __future__ import annotations

import humanize
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.user_repo import UserRepository
from database.repositories.file_repo import FileRepository

router = Router()

WELCOME = """
👋 *Welcome to FileConverter Bot!*

I can convert your files instantly:

📄 *Documents*
• `.docx` / `.doc` → PDF

📊 *Presentations*
• `.pptx` / `.ppt` → PDF

🖼 *Images*
• `.jpg`, `.png` → PDF *(send multiple to merge)*
• `.heic` → PDF or JPG *(your choice)*

📦 *Just send me a file and I'll handle the rest!*

Use /help for detailed instructions.
Use /stats for your conversion history.
"""


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    repo = UserRepository(session)
    await repo.upsert(message.from_user)
    await message.answer(WELCOME, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    text = (
        "📖 *How to use*\n\n"
        "1. Send any supported file\n"
        "2. For HEIC images, choose JPG or PDF output\n"
        "3. For multiple JPG/PNG images, send them all then tap *Done – merge to PDF*\n\n"
        f"*Supported formats:* `.docx`, `.doc`, `.pptx`, `.ppt`, `.jpg`, `.png`, `.heic`\n"
        f"*Max file size:* 50 MB per file\n\n"
        "Use /stats to see your conversion history."
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("stats"))
async def cmd_stats(message: Message, session: AsyncSession) -> None:
    user_repo = UserRepository(session)
    file_repo = FileRepository(session)

    user = await user_repo.get(message.from_user.id)
    if not user:
        await message.answer("No stats yet – send me a file to convert!")
        return

    history = await file_repo.get_user_history(message.from_user.id, limit=5)

    lines = [
        f"📊 *Your Stats*\n",
        f"Total conversions: *{user.total_conversions}*",
        f"Data processed: *{humanize.naturalsize(user.total_bytes_processed)}*\n",
        "🕓 *Recent conversions:*",
    ]

    for rec in history:
        icon = "✅" if rec.status.value == "success" else "❌"
        lines.append(
            f"{icon} `{rec.original_filename}` → `{rec.output_filename or 'n/a'}` "
            f"({rec.created_at.strftime('%d %b %H:%M')})"
        )

    if not history:
        lines.append("_None yet_")

    await message.answer("\n".join(lines), parse_mode="Markdown")
