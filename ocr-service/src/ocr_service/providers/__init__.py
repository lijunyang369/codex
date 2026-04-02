from .base import OCRProvider, OCRProviderError, ProviderHealth, ProviderLineResult, ProviderLinesResult, ProviderTextResult
from .null_provider import NullOCRProvider
from .paddle_provider import PaddleOCRProvider

__all__ = [
    "OCRProvider",
    "OCRProviderError",
    "NullOCRProvider",
    "PaddleOCRProvider",
    "ProviderHealth",
    "ProviderLineResult",
    "ProviderLinesResult",
    "ProviderTextResult",
]
