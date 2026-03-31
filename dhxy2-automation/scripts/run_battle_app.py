from __future__ import annotations

import json
from pathlib import Path

from src.app import BootstrapPaths, build_app_from_configs
from src.platform import Rect


class DemoWindowGateway:
    def __init__(self) -> None:
        self._handles = (1001,)

    def enumerate_windows(self) -> tuple[int, ...]:
        return self._handles

    def is_window(self, handle: int) -> bool:
        return handle in self._handles

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

    def capture_rect(self, rect: Rect):
        from PIL import Image

        return Image.new("RGB", (rect.width, rect.height), color="black")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    app = build_app_from_configs(
        BootstrapPaths(
            env_config=root / "configs" / "env" / "local.json",
            account_config=root / "configs" / "accounts" / "instance-1.json",
            scenario_config=root / "configs" / "scenarios" / "battle-smoke.json",
        ),
        gateway=DemoWindowGateway(),
    )
    result = app.run_once()
    payload = {
        "state": app._context.state.value,
        "window_handle": app._window_session.handle,
        "transition_count": len(result.transitions),
        "executed_action_count": len(result.executed_actions),
        "observation_confidence": result.observation.confidence_summary,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()