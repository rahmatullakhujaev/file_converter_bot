"""Converter registry – maps conversion_type string to converter class."""
from converters.base import BaseConverter
from converters.docx_to_pdf import DocxToPdfConverter
from converters.pptx_to_pdf import PptxToPdfConverter
from converters.image_to_pdf import ImageToPdfConverter
from converters.heic_to_jpg import HeicToJpgConverter
from converters.heic_to_pdf import HeicToPdfConverter

REGISTRY: dict[str, type[BaseConverter]] = {
    "docx_to_pdf":  DocxToPdfConverter,
    "pptx_to_pdf":  PptxToPdfConverter,
    "image_to_pdf": ImageToPdfConverter,
    "heic_to_pdf":  HeicToPdfConverter,
    "heic_to_jpg":  HeicToJpgConverter,
}


def get_converter(conversion_type: str) -> BaseConverter:
    cls = REGISTRY.get(conversion_type)
    if cls is None:
        raise KeyError(f"No converter registered for '{conversion_type}'")
    return cls()


__all__ = ["get_converter", "REGISTRY", "BaseConverter"]
