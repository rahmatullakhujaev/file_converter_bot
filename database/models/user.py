"""Telegram user model – stores every field Telegram exposes."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class User(Base):
    __tablename__ = "users"

    # Primary key = Telegram user_id (guaranteed unique)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    # Identity
    first_name: Mapped[str] = mapped_column(String(256))
    last_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    username: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    language_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stats
    total_conversions: Mapped[int] = mapped_column(Integer, default=0)
    total_bytes_processed: Mapped[int] = mapped_column(BigInteger, default=0)

    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    files: Mapped[list["FileRecord"]] = relationship(  # noqa: F821
        "FileRecord", back_populates="user", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"
