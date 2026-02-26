"""Async SQLAlchemy engine + session factory."""
from __future__ import annotations

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import config
from database.models.base import Base

engine = create_async_engine(
    config.db_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    for attempt in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as e:
            print(f"DB not ready (attempt {attempt + 1}/10): {e}")
            await asyncio.sleep(3)
    raise RuntimeError("Could not connect to database after 10 attempts.")


async def get_session() -> AsyncSession:  # type: ignore[return]
    async with AsyncSessionFactory() as session:
        yield session