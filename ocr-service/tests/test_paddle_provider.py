from unittest import TestCase
from unittest.mock import patch

from ocr_service.config.settings import Settings
from ocr_service.providers.base import OCRProviderError
from ocr_service.providers.paddle_provider import PaddleOCRProvider


class _FakeEngine:
    def __init__(self, result) -> None:
        self._result = result

    def ocr(self, image, cls=True):
        del image, cls
        return self._result


class _BrokenEngine:
    def ocr(self, image, cls=True):
        del image, cls
        raise RuntimeError("boom")


class PaddleProviderTests(TestCase):
    def setUp(self) -> None:
        self.provider = PaddleOCRProvider(Settings(provider="paddle"))

    def test_read_lines_sorts_and_filters_allowlist(self) -> None:
        fake_result = [
            [
                (
                    [[30, 40], [60, 40], [60, 60], [30, 60]],
                    ("B-2", 0.8),
                ),
                (
                    [[10, 10], [40, 10], [40, 20], [10, 20]],
                    ("A1", 0.9),
                ),
            ]
        ]
        with patch.object(
            PaddleOCRProvider,
            "_get_engine",
            return_value=_FakeEngine(fake_result),
        ):
            result = self.provider.read_lines(image=None, profile="default", allowlist="AB12")  # type: ignore[arg-type]

        self.assertEqual([line.text for line in result.lines], ["A1", "B2"])

    def test_read_text_merges_lines(self) -> None:
        fake_result = [
            [
                (
                    [[0, 0], [10, 0], [10, 10], [0, 10]],
                    ("first", 0.9),
                ),
                (
                    [[0, 20], [10, 20], [10, 30], [0, 30]],
                    ("second", 0.7),
                ),
            ]
        ]
        with patch.object(
            PaddleOCRProvider,
            "_get_engine",
            return_value=_FakeEngine(fake_result),
        ):
            result = self.provider.read_text(image=None, profile="default", allowlist=None)  # type: ignore[arg-type]

        self.assertEqual(result.text, "first\nsecond")
        self.assertAlmostEqual(result.confidence, 0.8)

    def test_read_lines_raises_provider_error_on_engine_failure(self) -> None:
        with patch.object(
            PaddleOCRProvider,
            "_get_engine",
            return_value=_BrokenEngine(),
        ):
            with self.assertRaises(OCRProviderError):
                self.provider.read_lines(image=None, profile="default", allowlist=None)  # type: ignore[arg-type]
