from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from PIL import Image

from ocr_service.config.settings import Settings
from ocr_service.providers.base import (
    OCRProvider,
    OCRProviderError,
    ProviderHealth,
    ProviderLineResult,
    ProviderLinesResult,
    ProviderTextResult,
)


@dataclass(frozen=True)
class PaddleOCRProvider(OCRProvider):
    settings: Settings

    @property
    def name(self) -> str:
        return "paddle"

    def health(self) -> ProviderHealth:
        try:
            self._get_engine(
                self.settings.paddle_language,
                self.settings.paddle_use_angle_cls,
            )
        except Exception as exc:
            return ProviderHealth(
                status="degraded",
                provider=self.name,
                detail=f"paddle provider unavailable: {exc}",
            )
        return ProviderHealth(
            status="ok",
            provider=self.name,
            detail="paddle provider ready",
        )

    def read_text(self, image: Image.Image, *, profile: str, allowlist: str | None) -> ProviderTextResult:
        lines_result = self.read_lines(image, profile=profile, allowlist=allowlist)
        if not lines_result.lines:
            return ProviderTextResult(text="", confidence=0.0, provider=self.name)
        merged_text = "\n".join(line.text for line in lines_result.lines if line.text)
        average_confidence = sum(line.confidence for line in lines_result.lines) / len(lines_result.lines)
        return ProviderTextResult(
            text=merged_text,
            confidence=average_confidence,
            provider=self.name,
        )

    def read_lines(self, image: Image.Image, *, profile: str, allowlist: str | None) -> ProviderLinesResult:
        del profile
        try:
            engine = self._get_engine(
                self.settings.paddle_language,
                self.settings.paddle_use_angle_cls,
            )
            result = engine.ocr(image, cls=self.settings.paddle_use_angle_cls)
        except Exception as exc:
            raise OCRProviderError(f"paddle OCR inference failed: {exc}") from exc
        lines: list[ProviderLineResult] = []
        for block in result or []:
            for item in block or []:
                if len(item) != 2:
                    continue
                points, payload = item
                if not isinstance(payload, (list, tuple)) or len(payload) != 2:
                    continue
                text = str(payload[0])
                if allowlist:
                    text = "".join(char for char in text if char in allowlist)
                    if not text:
                        continue
                confidence = float(payload[1])
                bounds = _points_to_bounds(points)
                lines.append(
                    ProviderLineResult(
                        text=text,
                        confidence=confidence,
                        bounds=bounds,
                    )
                )
        lines.sort(key=_line_sort_key)
        return ProviderLinesResult(lines=tuple(lines), provider=self.name)

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_engine(language: str, use_angle_cls: bool):
        from paddleocr import PaddleOCR

        return PaddleOCR(use_angle_cls=use_angle_cls, lang=language)


def _points_to_bounds(points) -> tuple[int, int, int, int] | None:
    if not points:
        return None
    xs = [int(point[0]) for point in points]
    ys = [int(point[1]) for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def _line_sort_key(line: ProviderLineResult) -> tuple[int, int]:
    if line.bounds is None:
        return (10**9, 10**9)
    left, top, _, _ = line.bounds
    return (top, left)
