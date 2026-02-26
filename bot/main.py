"""Bot entry point – registers routers, middleware, starts polling."""
from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers import document, photo, start
from bot.middlewares.db_middleware import DbSessionMiddleware
from bot.middlewares.rate_limit_middleware import RateLimitMiddleware
from config import config
from database.engine import init_db
from utils.logger import log, setup_logging


async def main() -> None:
    setup_logging()
    os.makedirs(config.temp_dir, exist_ok=True)

    log.info("bot.starting")
    await init_db()
    log.info("db.ready")

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Middleware (order matters – DB first, then rate limit)
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(RateLimitMiddleware())

    # Routers
    dp.include_router(start.router)
    dp.include_router(document.router)
    dp.include_router(photo.router)

    log.info("bot.polling_start")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
