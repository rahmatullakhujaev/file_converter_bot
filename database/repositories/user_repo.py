"""CRUD for User model."""
from __future__ import annotations

from datetime import datetime, timezone
from aiogram.types import User as TgUser
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from database.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, tg_user: TgUser) -> User:
        """Insert or update a user from a Telegram User object."""
        stmt = (
            insert(User)
            .values(
                id=tg_user.id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username,
                language_code=tg_user.language_code,
                is_bot=tg_user.is_bot,
                is_premium=bool(getattr(tg_user, "is_premium", False)),
                last_active_at=datetime.now(timezone.utc),
            )
            .on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "first_name": tg_user.first_name,
                    "last_name": tg_user.last_name,
                    "username": tg_user.username,
                    "language_code": tg_user.language_code,
                    "is_premium": bool(getattr(tg_user, "is_premium", False)),
                    "last_active_at": datetime.now(timezone.utc),
                },
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def increment_stats(self, user_id: int, bytes_processed: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                total_conversions=User.total_conversions + 1,
                total_bytes_processed=User.total_bytes_processed + bytes_processed,
                last_active_at=datetime.now(timezone.utc),
            )
        )
        await self.session.commit()

    async def is_banned(self, user_id: int) -> bool:
        result = await self.session.execute(
            select(User.is_banned).where(User.id == user_id)
        )
        row = result.scalar_one_or_none()
        return bool(row) if row is not None else False
