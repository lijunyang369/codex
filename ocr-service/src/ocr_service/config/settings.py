from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    service_name: str = "ocr-service"
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 18080
    provider: str = "null"
    request_timeout_ms: int = 1500
    allowed_roots: tuple[Path, ...] = (Path(r"D:\Codex"),)
    paddle_language: str = "ch"
    paddle_use_angle_cls: bool = True
    max_image_bytes: int = 5 * 1024 * 1024
    max_image_width: int = 4096
    max_image_height: int = 4096
    max_image_pixels: int = 8_000_000


def _parse_bool(raw: str | None, *, default: bool) -> bool:
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def load_settings() -> Settings:
    host = os.environ.get("OCR_SERVICE_HOST", os.environ.get("OCR_SIDECAR_HOST", "127.0.0.1"))
    port = int(os.environ.get("OCR_SERVICE_PORT", os.environ.get("OCR_SIDECAR_PORT", "18080")))
    provider = (
        os.environ.get("OCR_SERVICE_PROVIDER", os.environ.get("OCR_SIDECAR_PROVIDER", "null"))
        .strip()
        .lower()
        or "null"
    )
    request_timeout_ms = int(
        os.environ.get(
            "OCR_SERVICE_REQUEST_TIMEOUT_MS",
            os.environ.get("OCR_SIDECAR_REQUEST_TIMEOUT_MS", "1500"),
        )
    )
    allowed_roots_raw = os.environ.get(
        "OCR_SERVICE_ALLOWED_ROOTS",
        os.environ.get("OCR_SIDECAR_ALLOWED_ROOTS", r"D:\Codex"),
    )
    paddle_language = (
        os.environ.get(
            "OCR_SERVICE_PADDLE_LANGUAGE",
            os.environ.get("OCR_SIDECAR_PADDLE_LANGUAGE", "ch"),
        )
        .strip()
        .lower()
        or "ch"
    )
    paddle_use_angle_cls = _parse_bool(
        os.environ.get(
            "OCR_SERVICE_PADDLE_USE_ANGLE_CLS",
            os.environ.get("OCR_SIDECAR_PADDLE_USE_ANGLE_CLS"),
        ),
        default=True,
    )
    max_image_bytes = int(
        os.environ.get(
            "OCR_SERVICE_MAX_IMAGE_BYTES",
            os.environ.get("OCR_SIDECAR_MAX_IMAGE_BYTES", str(5 * 1024 * 1024)),
        )
    )
    max_image_width = int(
        os.environ.get(
            "OCR_SERVICE_MAX_IMAGE_WIDTH",
            os.environ.get("OCR_SIDECAR_MAX_IMAGE_WIDTH", "4096"),
        )
    )
    max_image_height = int(
        os.environ.get(
            "OCR_SERVICE_MAX_IMAGE_HEIGHT",
            os.environ.get("OCR_SIDECAR_MAX_IMAGE_HEIGHT", "4096"),
        )
    )
    max_image_pixels = int(
        os.environ.get(
            "OCR_SERVICE_MAX_IMAGE_PIXELS",
            os.environ.get("OCR_SIDECAR_MAX_IMAGE_PIXELS", "8000000"),
        )
    )
    allowed_roots = tuple(
        Path(item).resolve()
        for item in allowed_roots_raw.split(";")
        if item.strip()
    )
    return Settings(
        host=host,
        port=port,
        provider=provider,
        request_timeout_ms=request_timeout_ms,
        allowed_roots=allowed_roots or (Path(r"D:\Codex").resolve(),),
        paddle_language=paddle_language,
        paddle_use_angle_cls=paddle_use_angle_cls,
        max_image_bytes=max_image_bytes,
        max_image_width=max_image_width,
        max_image_height=max_image_height,
        max_image_pixels=max_image_pixels,
    )
