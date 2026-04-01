from __future__ import annotations

import json
import unittest

from tests.smoke._paths import CONFIGS_ROOT


class BattleCommandDetectionCandidatesTestCase(unittest.TestCase):
    def test_candidate_config_splits_character_and_pet_battle_profiles(self) -> None:
        payload = json.loads(
            (CONFIGS_ROOT / "ui" / "battle-command-detection-candidates.json").read_text(encoding="utf-8-sig")
        )

        self.assertEqual("template_detection", payload["source"]["type"])
        self.assertEqual(2, payload["version"])
        self.assertEqual(1247, payload["profiles"]["character_battle_command_bar"]["layout"]["x"])
        self.assertEqual([1247, 301], payload["profiles"]["character_battle_command_bar"]["buttons"]["item"]["point"])
        self.assertEqual([1247, 336], payload["profiles"]["character_battle_command_bar"]["buttons"]["defend"]["point"])
        self.assertEqual(
            [1146, 783],
            payload["profiles"]["character_battle_command_bar"]["seeded_buttons"]["battle_command_bar.pet"]["point"],
        )
        self.assertEqual(
            [1247, 370],
            payload["profiles"]["pet_battle_command_bar"]["buttons"]["protect"]["point"],
        )
        self.assertEqual(
            ["spell", "item", "defend", "protect"],
            list(payload["profiles"]["pet_battle_command_bar"]["buttons"].keys()),
        )


if __name__ == "__main__":
    unittest.main()
