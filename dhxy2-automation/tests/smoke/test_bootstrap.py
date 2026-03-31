from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.app import BootstrapPaths, NoOpInputGateway, build_app
from src.platform import Rect, WindowSession


class FakeWindowGateway:
    def is_window(self, handle: int) -> bool:
        return handle == 1001

    def is_window_visible(self, handle: int) -> bool:
        return True

    def get_foreground_window(self) -> int:
        return 1001

    def focus_window(self, handle: int) -> None:
        return None

    def get_window_text(self, handle: int) -> str:
        return "dhxy2"

    def get_class_name(self, handle: int) -> str:
        return "DhxyWindow"

    def get_window_rect(self, handle: int) -> Rect:
        return Rect(0, 0, 1280, 720)

    def get_client_rect(self, handle: int) -> Rect:
        return Rect(8, 32, 1272, 712)

    def capture_rect(self, rect: Rect) -> Image.Image:
        return Image.new("RGB", (rect.width, rect.height), color="black")


class BootstrapTestCase(unittest.TestCase):
    def test_build_app_from_json_configs(self) -> None:
        root = Path('D:/Codex/dhxy2-automation')
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / 'local.json'
            env_path.write_text('{"runs_root": "' + temp_dir.replace('\\', '\\\\') + '", "dry_run": true}', encoding='utf-8')

            app = build_app(
                BootstrapPaths(
                    env_config=env_path,
                    account_config=root / 'configs' / 'accounts' / 'instance-1.json',
                    scenario_config=root / 'configs' / 'scenarios' / 'battle-smoke.json',
                ),
                window_session=WindowSession(handle=1001, gateway=FakeWindowGateway()),
                input_gateway=NoOpInputGateway(),
            )

            result = app.run_once()

            self.assertEqual('instance-1', app._context.instance_id)
            self.assertEqual(1, len(result.executed_actions))
            self.assertTrue(app._context.battle_session_id.startswith('battle-smoke'))


if __name__ == '__main__':
    unittest.main()
