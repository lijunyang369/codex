from __future__ import annotations

from base64 import b64decode
from io import BytesIO
from pathlib import Path
from PIL import Image, UnidentifiedImageError

from ocr_service.config.settings import Settings
from ocr_service.models.request_models import OCRReadRequest


class InvalidImageInputError(ValueError):
    pass


class ImageLoader:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def load(self, request: OCRReadRequest) -> Image.Image:
        if request.image_path:
            return self._load_from_path(Path(request.image_path))
        if request.image_base64:
            return self._load_from_base64(request.image_base64)
        raise InvalidImageInputError("missing image input")

    def _load_from_path(self, path: Path) -> Image.Image:
        resolved = path.resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"image not found: {resolved}")
        if not self._is_allowed_path(resolved):
            raise InvalidImageInputError(f"path is outside allowed roots: {resolved}")
        try:
            with Image.open(resolved) as image:
                self._validate_image(image)
                return image.convert("RGB")
        except UnidentifiedImageError as exc:
            raise InvalidImageInputError(f"unsupported image file: {resolved}") from exc

    def _load_from_base64(self, payload: str) -> Image.Image:
        normalized_payload = payload.strip()
        if normalized_payload.startswith("data:"):
            _, _, normalized_payload = normalized_payload.partition(",")
        try:
            content = b64decode(normalized_payload, validate=True)
        except Exception as exc:
            raise InvalidImageInputError("invalid base64 image payload") from exc
        if len(content) > self._settings.max_image_bytes:
            raise InvalidImageInputError("base64 image payload exceeds size limit")
        try:
            with Image.open(BytesIO(content)) as image:
                self._validate_image(image)
                return image.convert("RGB")
        except UnidentifiedImageError as exc:
            raise InvalidImageInputError("base64 payload is not a supported image") from exc

    def _is_allowed_path(self, resolved: Path) -> bool:
        for root in self._settings.allowed_roots:
            try:
                resolved.relative_to(root)
                return True
            except ValueError:
                continue
        return False

    def _validate_image(self, image: Image.Image) -> None:
        width, height = image.size
        if width > self._settings.max_image_width or height > self._settings.max_image_height:
            raise InvalidImageInputError("image dimensions exceed limit")
        if width * height > self._settings.max_image_pixels:
            raise InvalidImageInputError("image pixel count exceeds limit")
