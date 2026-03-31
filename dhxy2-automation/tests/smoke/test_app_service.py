from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.app import BattleAutomationApp
from src.domain import ActionType, AutomationContext, BattleObservation, BattleState
from src.executor import ActionExecutor
from src.platform import Rect, WindowSession
from src.policy import FixedActionRule, FixedRulePolicy
from src.runtime import RuntimeSession
from src.state_machine import BattleStateMachine


class FakeObservationProvider:
    def observe(self, window_session: WindowSession) -> BattleObservation:
        return BattleObservation(
            battle_ui_visible=True,
            action_prompt_visible=True,
            skill_panel_visible=True,
            target_select_visible=False,
            settlement_visible=False,
            window_alive=True,
            window_focused=True,
            frame_timestamp=datetime.now(timezone.utc),
            frame_hash="frame-hash",
            confidence_summary=0.95,
        )


class FakeWindowGateway:
    def __init__(self) -> None:
        self.focused = False

    def is_window(self, handle: int) -> bool:
        return handle == 1001

    def is_window_visible(self, handle: int) -> bool:
        return True

    def get_foreground_window(self) -> int:
        return 1001 if self.focused else 0

    def focus_window(self, handle: int) -> None:
        self.focused = True

    def get_window_text(self, handle: int) -> str:
        return "dhxy2"

    def get_class_name(self, handle: int) -> str:
        return "DhxyWindow"

    def get_window_rect(self, handle: int) -> Rect:
        return Rect(0, 0, 1280, 720)

    def get_client_rect(self, handle: int) -> Rect:
        return Rect(8, 32, 1272, 712)

    def capture_rect(self, rect: Rect):
        raise NotImplementedError


class FakeInputGateway:
    def __init__(self) -> None:
        self.operations: list[tuple[str, object]] = []

    def click(self, x: int, y: int) -> None:
        self.operations.append(("click", (x, y)))

    def press_key(self, key: str) -> None:
        self.operations.append(("key", key))

    def wait(self, seconds: float) -> None:
        self.operations.append(("wait", seconds))


class BattleAutomationAppTestCase(unittest.TestCase):
    def test_run_once_drives_single_battle_round(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = AutomationContext(
                instance_id="instance-1",
                battle_session_id="battle-1",
                state=BattleState.ROUND_ACTIONABLE,
            )
            runtime_session = RuntimeSession.create(Path(temp_dir), context)
            app = BattleAutomationApp(
                context=context,
                window_session=WindowSession(handle=1001, gateway=FakeWindowGateway()),
                observation_provider=FakeObservationProvider(),
                state_machine=BattleStateMachine(),
                policy=FixedRulePolicy(
                    FixedActionRule(
                        action_type=ActionType.CAST_SKILL,
                        reason="fixed_priority_skill",
                        target="enemy_front",
                        parameters={
                            "skill_point": (100, 200),
                            "target_point": (300, 400),
                            "confirm_point": (500, 600),
                        },
                    )
                ),
                executor=ActionExecutor(),
                runtime_session=runtime_session,
                input_gateway=FakeInputGateway(),
            )

            result = app.run_once()

            self.assertEqual(BattleState.ROUND_WAITING, context.state)
            self.assertEqual(1, len(result.executed_actions))
            self.assertEqual(3, len(result.transitions))
            self.assertEqual("CAST_SKILL", result.executed_actions[0].action_type)
            self.assertTrue(list(runtime_session.artifacts.session_paths.actions.glob("action_*.json")))


if __name__ == "__main__":
    unittest.main()
