"""Abstract base converter interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseConverter(ABC):
    """All converters implement this interface."""

    @abstractmethod
    async def convert(self, input_path: Path, **kwargs) -> Path:
        """Convert a file and return the output path."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for logging."""
        ...
