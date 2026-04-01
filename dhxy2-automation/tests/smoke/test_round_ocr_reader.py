from __future__ import annotations

import unittest

import numpy as np
from PIL import Image

from src.perception.services import (
    _build_digit_templates,
    _classify_digit_roi,
    _load_real_digit_templates,
    _match_digit_band,
    build_round_digit_mask,
)
from tests.smoke._paths import RESOURCES_ROOT, RUNS_ROOT


class RoundOCRReaderTestCase(unittest.TestCase):
    def test_match_digit_band_recognizes_real_round_three_crop(self) -> None:
        templates = _build_digit_templates()
        mask = build_round_digit_mask(
            Image.open(
                RUNS_ROOT
                / "artifacts"
                / "probes"
                / "recognition-workbench"
                / "20260401T092306780541Z"
                / "region-battle_main.png"
            )
        )

        text, confidence = _match_digit_band(mask, templates)

        self.assertEqual("3", text)
        self.assertGreaterEqual(confidence, 0.45)

    def test_match_digit_band_recognizes_recent_round_two_crop(self) -> None:
        templates = _build_digit_templates()
        mask = build_round_digit_mask(
            Image.open(
                RUNS_ROOT
                / "artifacts"
                / "probes"
                / "recognition-workbench"
                / "20260401T104329612674Z"
                / "region-battle_main.png"
            )
        )

        text, confidence = _match_digit_band(mask, templates)

        self.assertEqual("2", text)
        self.assertGreaterEqual(confidence, 0.45)

    def test_match_digit_band_recognizes_recent_round_seven_crop(self) -> None:
        templates = _build_digit_templates()
        mask = build_round_digit_mask(
            Image.open(
                RUNS_ROOT
                / "artifacts"
                / "probes"
                / "recognition-workbench"
                / "20260401T104428736170Z"
                / "region-battle_main.png"
            )
        )

        text, confidence = _match_digit_band(mask, templates)

        self.assertEqual("7", text)
        self.assertGreaterEqual(confidence, 0.45)

    def test_real_digit_templates_cover_one_to_nine(self) -> None:
        templates = _load_real_digit_templates()

        self.assertEqual([str(index) for index in range(1, 10)], sorted(templates.keys()))

    def test_real_digit_templates_self_classify_as_expected(self) -> None:
        templates = _build_digit_templates()

        for digit in range(1, 10):
            image = np.array(
                Image.open(
                    RESOURCES_ROOT
                    / "templates"
                    / "battle"
                    / f"battle_round_digit_{digit}.png"
                ).convert("L")
            )
            recognized, confidence = _classify_digit_roi(image, templates)
            self.assertEqual(str(digit), recognized)
            self.assertGreaterEqual(confidence, 0.9)


if __name__ == "__main__":
    unittest.main()
