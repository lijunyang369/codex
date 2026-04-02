from __future__ import annotations

from PIL import Image

from ocr_service.providers.base import OCRProvider, ProviderHealth, ProviderLinesResult, ProviderTextResult


class NullOCRProvider(OCRProvider):
    @property
    def name(self) -> str:
        return "null"

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            status="degraded",
            provider=self.name,
            detail="provider is not configured; returning empty OCR results",
        )

    def read_text(self, image: Image.Image, *, profile: str, allowlist: str | None) -> ProviderTextResult:
        del image, profile, allowlist
        return ProviderTextResult(text="", confidence=0.0, provider=self.name)

    def read_lines(self, image: Image.Image, *, profile: str, allowlist: str | None) -> ProviderLinesResult:
        del image, profile, allowlist
        return ProviderLinesResult(lines=(), provider=self.name)
