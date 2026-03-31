from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.app import BootstrapPaths, NoOpInputGateway, build_app_from_configs
from src.platform import Rect, WindowFinder, WindowNotFoundError, WindowSearchCriteria


class FakeWindowGateway:
    def __init__(self) -> None:
        self.windows = {
            1001: {"title": "大话西游2免费版 测试窗口", "class_name": "DHXYFreeJYMainFrame", "visible": True},
            1002: {"title": "other", "class_name": "OtherWindow", "visible": True},
        }

    def enumerate_windows(self) -> tuple[int, ...]:
        return tuple(self.windows.keys())

    def is_window(self, handle: int) -> bool:
        return handle in self.windows

    def is_window_visible(self, handle: int) -> bool:
        return self.windows[handle]["visible"]

    def get_foreground_window(self) -> int:
        return 1001

    def focus_window(self, handle: int) -> None:
        return None

    def get_window_text(self, handle: int) -> str:
        return str(self.windows[handle]["title"])

    def get_class_name(self, handle: int) -> str:
        return str(self.windows[handle]["class_name"])

    def get_window_rect(self, handle: int) -> Rect:
        return Rect(0, 0, 1280, 720)

    def get_client_rect(self, handle: int) -> Rect:
        return Rect(8, 32, 1272, 712)

    def capture_rect(self, rect: Rect) -> Image.Image:
        return Image.new("RGB", (rect.width, rect.height), color="black")


class WindowFinderTestCase(unittest.TestCase):
    def test_find_matches_by_title_and_class(self) -> None:
        gateway = FakeWindowGateway()
        finder = WindowFinder(gateway)

        session = finder.find(WindowSearchCriteria(title_contains="大话西游2免费版", class_name="DHXYFreeJYMainFrame"))

        self.assertEqual(1001, session.handle)

    def test_find_raises_when_no_window_matches(self) -> None:
        gateway = FakeWindowGateway()
        finder = WindowFinder(gateway)

        with self.assertRaises(WindowNotFoundError):
            finder.find(WindowSearchCriteria(title_contains="missing"))


class BootstrapWindowBindingTestCase(unittest.TestCase):
    def test_build_app_from_configs_binds_window_from_account_config(self) -> None:
        root = Path('D:/Codex/dhxy2-automation')
        gateway = FakeWindowGateway()
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / 'local.json'
            env_path.write_text('{"runs_root": "' + temp_dir.replace('\\', '\\\\') + '", "dry_run": true}', encoding='utf-8')

            app = build_app_from_configs(
                BootstrapPaths(
                    env_config=env_path,
                    account_config=root / 'configs' / 'accounts' / 'instance-1.json',
                    scenario_config=root / 'configs' / 'scenarios' / 'battle-smoke.json',
                ),
                input_gateway=NoOpInputGateway(),
                gateway=gateway,
            )

            result = app.run_once()

            self.assertEqual(1001, app._window_session.handle)
            self.assertEqual(1, len(result.executed_actions))


if __name__ == '__main__':
    unittest.main()
