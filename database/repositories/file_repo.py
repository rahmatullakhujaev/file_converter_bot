"""CRUD for FileRecord model."""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.file_record import FileRecord, ConversionType, ConversionStatus


class FileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: int,
        original_filename: str,
        original_extension: str,
        original_mime_type: str | None,
        original_size_bytes: int,
        telegram_file_id: str | None,
        conversion_type: ConversionType,
    ) -> FileRecord:
        record = FileRecord(
            user_id=user_id,
            original_filename=original_filename,
            original_extension=original_extension,
            original_mime_type=original_mime_type,
            original_size_bytes=original_size_bytes,
            telegram_file_id=telegram_file_id,
            conversion_type=conversion_type,
            status=ConversionStatus.PENDING,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def mark_success(
        self,
        record: FileRecord,
        *,
        output_filename: str,
        output_data: bytes,
        duration_seconds: float,
    ) -> FileRecord:
        record.status = ConversionStatus.SUCCESS
        record.output_filename = output_filename
        record.output_data = output_data
        record.output_size_bytes = len(output_data)
        record.duration_seconds = duration_seconds
        record.completed_at = datetime.now(timezone.utc)
        await self.session.commit()
        return record

    async def mark_failed(
        self, record: FileRecord, *, error_message: str, duration_seconds: float
    ) -> FileRecord:
        record.status = ConversionStatus.FAILED
        record.error_message = error_message[:1024]
        record.duration_seconds = duration_seconds
        record.completed_at = datetime.now(timezone.utc)
        await self.session.commit()
        return record

    async def get_user_history(
        self, user_id: int, *, limit: int = 10, offset: int = 0
    ) -> list[FileRecord]:
        result = await self.session.execute(
            select(FileRecord)
            .where(FileRecord.user_id == user_id)
            .order_by(FileRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_user(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).where(FileRecord.user_id == user_id)
        )
        return result.scalar_one()

    async def global_stats(self) -> dict:
        result = await self.session.execute(
            select(
                func.count().label("total"),
                func.sum(FileRecord.original_size_bytes).label("bytes_in"),
                func.sum(FileRecord.output_size_bytes).label("bytes_out"),
            ).where(FileRecord.status == ConversionStatus.SUCCESS)
        )
        row = result.one()
        return {
            "total_conversions": row.total or 0,
            "total_bytes_in": row.bytes_in or 0,
            "total_bytes_out": row.bytes_out or 0,
        }
