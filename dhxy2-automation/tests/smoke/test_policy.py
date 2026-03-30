from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.domain import ActionType, AutomationContext, BattleObservation, BattleState
from src.policy import FixedActionRule, FixedRulePolicy


def build_observation(**overrides: object) -> BattleObservation:
    payload = {
        "battle_ui_visible": True,
        "action_prompt_visible": True,
        "skill_panel_visible": True,
        "target_select_visible": False,
        "settlement_visible": False,
        "window_alive": True,
        "window_focused": True,
        "frame_timestamp": datetime.now(timezone.utc),
        "frame_hash": "frame-hash",
        "confidence_summary": 0.95,
    }
    payload.update(overrides)
    return BattleObservation(**payload)


class FixedRulePolicyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = FixedRulePolicy(
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
        )
        self.context = AutomationContext(
            instance_id="instance-1",
            battle_session_id="battle-1",
            state=BattleState.ROUND_ACTIONABLE,
        )

    def test_build_plan_returns_single_action_when_actionable(self) -> None:
        observation = build_observation()

        plan = self.policy.build_plan(observation, self.context)

        self.assertFalse(plan.is_empty())
        self.assertEqual(ActionType.CAST_SKILL, plan.actions[0].action_type)
        self.assertEqual("enemy_front", plan.actions[0].target)
        self.assertEqual("fixed_priority_skill", plan.reason)

    def test_build_plan_returns_empty_when_state_not_actionable(self) -> None:
        self.context.state = BattleState.ROUND_WAITING
        observation = build_observation()

        plan = self.policy.build_plan(observation, self.context)

        self.assertTrue(plan.is_empty())
        self.assertIn("not actionable", plan.reason)

    def test_build_plan_returns_empty_when_window_not_focused(self) -> None:
        observation = build_observation(window_focused=False)

        plan = self.policy.build_plan(observation, self.context)

        self.assertTrue(plan.is_empty())
        self.assertEqual("window is not focused", plan.reason)


if __name__ == "__main__":
    unittest.main()
