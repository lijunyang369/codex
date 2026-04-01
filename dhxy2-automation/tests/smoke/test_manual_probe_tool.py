from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.app.manual_probe_tool import (
    ButtonCalibrationStore,
    ManualCoordinateProbeService,
    ManualProbeArtifacts,
)


class ManualCoordinateProbeServiceTestCase(unittest.TestCase):
    def test_save_feedback_updates_existing_probe_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "runs" / "artifacts" / "probes" / "manual-coordinate-ui"
            record_dir.mkdir(parents=True, exist_ok=True)
            service = ManualCoordinateProbeService(root)
            record = ManualProbeArtifacts(
                run_id="test-run",
                handle=1,
                client_x=100,
                client_y=200,
                screen_x=300,
                screen_y=400,
                before_path="before.png",
                after_path="after.png",
                before_hash="before",
                after_hash="after",
                frame_changed=True,
                delay_seconds=0.8,
                label="manual-probe",
                button_ref="nonbattle_toolbar.bag_panel",
            )
            record_path = record_dir / "test-run.json"
            record_path.write_text(json.dumps(record.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")

            saved_path = service.save_feedback("test-run", "confirmed", "opened panel")
            payload = json.loads(saved_path.read_text(encoding="utf-8-sig"))

            self.assertEqual(record_path, saved_path)
            self.assertEqual("confirmed", payload["status"])
            self.assertEqual("opened panel", payload["notes"])
            self.assertIn("reviewed_at", payload)


class ButtonCalibrationStoreTestCase(unittest.TestCase):
    def test_load_entries_splits_character_pet_and_nonbattle_buttons(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "configs" / "ui"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "button-calibration.json"
            config_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "nonbattle_toolbar": {
                            "buttons": {
                                "bag_panel": {
                                    "label": "道具",
                                    "status": "confirmed",
                                    "point": [950, 792],
                                }
                            }
                        },
                        "battle_command_bar": {
                            "buttons": {
                                "defend": {
                                    "label": "防御",
                                    "status": "candidate",
                                    "point": [1252, 348],
                                }
                            }
                        },
                        "pet_battle_command_bar": {
                            "buttons": {
                                "spell": {
                                    "label": "法术",
                                    "status": "candidate",
                                    "point": [1247, 267],
                                }
                            }
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            store = ButtonCalibrationStore(root)
            entries = store.load_entries()

            self.assertEqual(3, len(entries))
            self.assertEqual("nonbattle", store.load_entry("nonbattle_toolbar.bag_panel").category)
            self.assertEqual("character_battle", store.load_entry("battle_command_bar.defend").category)
            self.assertEqual("pet_battle", store.load_entry("pet_battle_command_bar.spell").category)

    def test_update_entry_writes_new_point_and_status_back_to_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "configs" / "ui"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "button-calibration.json"
            config_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "nonbattle_toolbar": {
                            "buttons": {
                                "friend_panel": {
                                    "label": "好友",
                                    "status": "candidate",
                                    "point": [1270, 792],
                                }
                            }
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            store = ButtonCalibrationStore(root)
            updated = store.update_entry(
                "nonbattle_toolbar.friend_panel",
                x=1282,
                y=805,
                status="confirmed",
                label="好友",
            )
            payload = json.loads(config_path.read_text(encoding="utf-8-sig"))

            self.assertEqual(1282, updated.x)
            self.assertEqual(805, updated.y)
            self.assertEqual("confirmed", updated.status)
            self.assertEqual([1282, 805], payload["nonbattle_toolbar"]["buttons"]["friend_panel"]["point"])
            self.assertEqual("confirmed", payload["nonbattle_toolbar"]["buttons"]["friend_panel"]["status"])


if __name__ == "__main__":
    unittest.main()
