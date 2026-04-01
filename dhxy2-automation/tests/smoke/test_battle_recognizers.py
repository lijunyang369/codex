from __future__ import annotations

import unittest
from datetime import datetime, timezone

from PIL import Image

from src.domain import MatchResult, OCRResult
from src.perception import BattleRecognitionSuite, ObservationBuilder, RecognitionSnapshot
from src.platform import FrameCapture, Rect, WindowInfo


class BattleRecognitionSuiteTestCase(unittest.TestCase):
    def test_battle_scene_is_independent_from_prompt_and_skill_bar(self) -> None:
        snapshot = RecognitionSnapshot(
            matches=(
                MatchResult(
                    template_id="battle_action_prompt",
                    confidence=0.97,
                    region_name="battle_prompt",
                ),
                MatchResult(
                    template_id="battle_skill_bar",
                    confidence=0.95,
                    region_name="skill_bar",
                ),
            ),
            ocr_texts=(),
            named_regions={
                "battle_main": (0, 0, 180, 120),
                "battle_auto_button": (1290, 700, 1368, 750),
                "battle_prompt": (1170, 245, 1320, 530),
                "skill_bar": (950, 680, 1378, 831),
            },
        )

        results = BattleRecognitionSuite().evaluate(snapshot)

        self.assertFalse(results["battle_scene"].detected)
        self.assertTrue(results["battle_action_prompt"].detected)
        self.assertTrue(results["battle_skill_bar"].detected)

    def test_battle_round_recognizer_extracts_digits_from_battle_main_ocr(self) -> None:
        snapshot = RecognitionSnapshot(
            matches=(),
            ocr_texts=(
                OCRResult(
                    text="第 4 回合",
                    confidence=0.93,
                    region_name="battle_main",
                ),
            ),
            named_regions={"battle_main": (0, 0, 180, 120)},
        )

        results = BattleRecognitionSuite().evaluate(snapshot)

        self.assertTrue(results["battle_round"].detected)
        self.assertEqual(4, results["battle_round"].details["round_number"])
        self.assertIn("第 4 回合", results["battle_round"].summary)

    def test_module_reports_missing_region_without_affecting_others(self) -> None:
        snapshot = RecognitionSnapshot(
            matches=(),
            ocr_texts=(),
            named_regions={"battle_main": (0, 0, 180, 120)},
        )

        results = BattleRecognitionSuite().evaluate(snapshot)

        self.assertFalse(results["battle_action_prompt"].detected)
        self.assertFalse(results["battle_action_prompt"].details["region_configured"])
        self.assertEqual("场景未配置该识别区域", results["battle_action_prompt"].summary)


class ObservationBuilderModuleWiringTestCase(unittest.TestCase):
    def test_builder_maps_independent_recognizers_back_to_observation_flags(self) -> None:
        builder = ObservationBuilder()
        frame = FrameCapture(image=Image.new("RGB", (200, 120), color="black"))
        window_info = WindowInfo(
            handle=1001,
            title="dhxy2",
            class_name="DhxyWindow",
            window_rect=Rect(0, 0, 1280, 720),
            client_rect=Rect(8, 32, 1272, 712),
            is_visible=True,
            is_foreground=True,
        )

        observation = builder.build(
            frame=frame,
            window_info=window_info,
            matches=(
                MatchResult(
                    template_id="battle_action_prompt",
                    confidence=0.96,
                    region_name="battle_prompt",
                ),
                MatchResult(
                    template_id="battle_skill_bar",
                    confidence=0.94,
                    region_name="skill_bar",
                ),
            ),
            ocr_texts=(
                OCRResult(
                    text="第 2 回合",
                    confidence=0.91,
                    region_name="battle_main",
                ),
            ),
            named_regions={
                "battle_main": Rect(0, 0, 180, 120),
                "battle_auto_button": Rect(1290, 700, 1368, 750),
                "battle_prompt": Rect(1170, 245, 1320, 530),
                "skill_bar": Rect(950, 680, 1378, 831),
            },
        )

        self.assertFalse(observation.battle_ui_visible)
        self.assertTrue(observation.action_prompt_visible)
        self.assertTrue(observation.skill_panel_visible)
        self.assertEqual(2, observation.round_number)


if __name__ == "__main__":
    unittest.main()
