from __future__ import annotations

import unittest
from pathlib import Path

from src.app import CharacterProfileLoader


class CharacterProfileLoaderTestCase(unittest.TestCase):
    def test_loads_profile_and_referenced_knowledge_configs(self) -> None:
        root = Path("D:/Codex/dhxy2-automation")
        loader = CharacterProfileLoader()

        profile = loader.load(root / "configs" / "characters" / "mage-default.json")

        self.assertEqual("mage-default", profile.character_id)
        self.assertEqual("mage", profile.role_type)
        self.assertIsNotNone(profile.character_system)
        self.assertIsNotNone(profile.pet_system)
        self.assertIn("根骨", profile.character_system.base_attributes)
        self.assertIn("growth_rate", profile.pet_system.core_fields)
        self.assertEqual("2014-07-29 06:12:50", profile.character_system.source[0].updated_at)


if __name__ == "__main__":
    unittest.main()
