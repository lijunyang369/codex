from base64 import b64encode
from io import BytesIO
from time import perf_counter, sleep
from unittest import TestCase

from PIL import Image

from ocr_service.config.settings import Settings
from ocr_service.models.request_models import OCRReadRequest
from ocr_service.providers.base import OCRProvider, OCRProviderError, ProviderHealth, ProviderLinesResult, ProviderTextResult
from ocr_service.services.ocr_service import OCRService


class _SlowProvider(OCRProvider):
    @property
    def name(self) -> str:
        return "slow"

    def health(self) -> ProviderHealth:
        return ProviderHealth(status="ok", provider=self.name, detail="ready")

    def read_text(self, image, *, profile: str, allowlist: str | None) -> ProviderTextResult:
        del image, profile, allowlist
        sleep(0.2)
        return ProviderTextResult(text="late", confidence=1.0, provider=self.name)

    def read_lines(self, image, *, profile: str, allowlist: str | None) -> ProviderLinesResult:
        del image, profile, allowlist
        sleep(0.2)
        return ProviderLinesResult(provider=self.name)


class OCRServiceTests(TestCase):
    def test_timeout_returns_quickly_without_waiting_for_provider_completion(self) -> None:
        image = Image.new("RGB", (4, 4), color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        request = OCRReadRequest(image_base64=b64encode(buffer.getvalue()).decode("ascii"))
        service = OCRService(
            settings=Settings(request_timeout_ms=20),
            provider=_SlowProvider(),
        )

        started_at = perf_counter()
        with self.assertRaises(OCRProviderError):
            service.read_text(request)
        elapsed = perf_counter() - started_at

        self.assertLess(elapsed, 0.15)
