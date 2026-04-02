from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
from threading import Thread

from ocr_service.config.settings import Settings
from ocr_service.models.request_models import OCRReadRequest
from ocr_service.providers.base import OCRProvider, OCRProviderError, ProviderHealth, ProviderLinesResult, ProviderTextResult
from ocr_service.services.image_loader import ImageLoader, InvalidImageInputError
from ocr_service.services.preprocess import normalize_image


@dataclass(frozen=True)
class OCRService:
    settings: Settings
    provider: OCRProvider

    def __post_init__(self) -> None:
        object.__setattr__(self, "_image_loader", ImageLoader(self.settings))

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            status="ok",
            provider=self.provider.name,
            detail="service is running",
        )

    def readiness(self) -> ProviderHealth:
        return self.provider.health()

    def read_text(self, request: OCRReadRequest) -> ProviderTextResult:
        self._validate_request(request)
        image = normalize_image(self._image_loader.load(request))
        return self._run_with_timeout(
            self.provider.read_text,
            image,
            profile=request.profile,
            allowlist=request.allowlist,
        )

    def read_lines(self, request: OCRReadRequest) -> ProviderLinesResult:
        self._validate_request(request)
        image = normalize_image(self._image_loader.load(request))
        return self._run_with_timeout(
            self.provider.read_lines,
            image,
            profile=request.profile,
            allowlist=request.allowlist,
        )

    def _validate_request(self, request: OCRReadRequest) -> None:
        if request.profile != "default":
            raise InvalidImageInputError(f"unsupported profile: {request.profile}")

    def _run_with_timeout(self, func, image, *, profile: str, allowlist: str | None):
        result_queue: Queue[tuple[str, object]] = Queue(maxsize=1)

        def run_provider() -> None:
            try:
                result = func(image, profile=profile, allowlist=allowlist)
            except Exception as exc:
                result_queue.put(("error", exc))
                return
            result_queue.put(("result", result))

        worker = Thread(target=run_provider, name="ocr-provider-call", daemon=True)
        worker.start()

        try:
            kind, payload = result_queue.get(timeout=self.settings.request_timeout_ms / 1000)
        except Empty as exc:
            raise OCRProviderError(
                f"provider timed out after {self.settings.request_timeout_ms}ms"
            ) from exc

        if kind == "error":
            raise payload  # type: ignore[misc]
        return payload
