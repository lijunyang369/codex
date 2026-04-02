from functools import lru_cache

from ocr_service.config.settings import Settings, load_settings
from ocr_service.providers.base import OCRProvider
from ocr_service.providers.null_provider import NullOCRProvider
from ocr_service.providers.paddle_provider import PaddleOCRProvider
from ocr_service.services.ocr_service import OCRService


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()


@lru_cache(maxsize=1)
def get_provider() -> OCRProvider:
    settings = get_settings()
    if settings.provider == "paddle":
        return PaddleOCRProvider(settings)
    return NullOCRProvider()


@lru_cache(maxsize=1)
def get_ocr_service() -> OCRService:
    return OCRService(
        settings=get_settings(),
        provider=get_provider(),
    )
