from base64 import b64encode
from io import BytesIO
from unittest import TestCase

from PIL import Image

from ocr_service.config.settings import Settings
from ocr_service.models.request_models import OCRReadRequest
from ocr_service.services.image_loader import ImageLoader, InvalidImageInputError


class ImageLoaderTests(TestCase):
    def setUp(self) -> None:
        self.loader = ImageLoader(Settings())

    def test_loads_data_url_base64_image(self) -> None:
        image = Image.new("RGB", (4, 4), color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        payload = "data:image/png;base64," + b64encode(buffer.getvalue()).decode("ascii")

        loaded = self.loader.load(OCRReadRequest(image_base64=payload))

        self.assertEqual(loaded.size, (4, 4))

    def test_rejects_invalid_base64_payload(self) -> None:
        with self.assertRaises(InvalidImageInputError):
            self.loader.load(OCRReadRequest(image_base64="%%%"))

    def test_rejects_base64_payload_that_exceeds_size_limit(self) -> None:
        oversized_loader = ImageLoader(Settings(max_image_bytes=3))

        with self.assertRaises(InvalidImageInputError):
            oversized_loader.load(OCRReadRequest(image_base64=b64encode(b"1234").decode("ascii")))

    def test_rejects_image_dimensions_that_exceed_limit(self) -> None:
        image = Image.new("RGB", (8, 8), color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        limited_loader = ImageLoader(Settings(max_image_width=4, max_image_height=4))

        with self.assertRaises(InvalidImageInputError):
            limited_loader.load(
                OCRReadRequest(image_base64=b64encode(buffer.getvalue()).decode("ascii"))
            )
