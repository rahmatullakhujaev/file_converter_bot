"""Per-user rate limiting middleware."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from config import config


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._calls: dict[int, deque] = defaultdict(deque)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.document and not event.photo:
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else None
        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        window = config.rate_limit_period
        limit = config.rate_limit_calls
        q = self._calls[user_id]

        # Purge old entries
        while q and now - q[0] > window:
            q.popleft()

        if len(q) >= limit:
            wait = int(window - (now - q[0])) + 1
            await event.answer(
                f"⏱ You're sending files too fast. Please wait {wait}s."
            )
            return

        q.append(now)
        return await handler(event, data)
