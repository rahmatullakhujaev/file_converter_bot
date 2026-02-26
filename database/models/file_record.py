"""File conversion record – stores metadata + binary content."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    BigInteger, DateTime, Enum, ForeignKey,
    Integer, LargeBinary, String, func, Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from database.models.base import Base


class ConversionType(str, enum.Enum):
    DOCX_TO_PDF  = "docx_to_pdf"
    PPTX_TO_PDF  = "pptx_to_pdf"
    IMAGE_TO_PDF = "image_to_pdf"   # jpg/png → pdf (merged if multiple)
    HEIC_TO_PDF  = "heic_to_pdf"
    HEIC_TO_JPG  = "heic_to_jpg"


class ConversionStatus(str, enum.Enum):
    PENDING   = "pending"
    SUCCESS   = "success"
    FAILED    = "failed"


class FileRecord(Base):
    __tablename__ = "file_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Owner
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Input metadata
    original_filename: Mapped[str] = mapped_column(String(512))
    original_extension: Mapped[str] = mapped_column(String(20))
    original_mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    original_size_bytes: Mapped[int] = mapped_column(BigInteger)
    telegram_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Conversion
    conversion_type: Mapped[ConversionType] = mapped_column(
        Enum(ConversionType), index=True
    )
    status: Mapped[ConversionStatus] = mapped_column(
        Enum(ConversionStatus), default=ConversionStatus.PENDING, index=True
    )
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Output
    output_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    output_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    output_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="files")  # noqa: F821

    def __repr__(self) -> str:
        return f"<FileRecord id={self.id} type={self.conversion_type} status={self.status}>"
