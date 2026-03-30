from __future__ import annotations

from src.domain import ActionType, AutomationAction
from src.executor.exceptions import ActionTranslationError
from src.executor.models import ExecutionStep, StepType


class ActionTranslator:
    def translate(self, action: AutomationAction) -> tuple[ExecutionStep, ...]:
        if action.action_type == ActionType.NO_OP:
            return (ExecutionStep(step_type=StepType.FOCUS_WINDOW),)

        if action.action_type == ActionType.CAST_SKILL:
            skill_point = self._require_point(action, "skill_point")
            steps = [
                ExecutionStep(step_type=StepType.FOCUS_WINDOW),
                ExecutionStep(step_type=StepType.CLICK, payload={"point": skill_point}),
            ]
            target_point = action.parameters.get("target_point")
            if target_point is not None:
                steps.append(ExecutionStep(step_type=StepType.CLICK, payload={"point": target_point}))
            confirm_point = action.parameters.get("confirm_point")
            if confirm_point is not None:
                steps.append(ExecutionStep(step_type=StepType.CLICK, payload={"point": confirm_point}))
            return tuple(steps)

        if action.action_type == ActionType.USE_ITEM:
            item_point = self._require_point(action, "item_point")
            steps = [
                ExecutionStep(step_type=StepType.FOCUS_WINDOW),
                ExecutionStep(step_type=StepType.CLICK, payload={"point": item_point}),
            ]
            target_point = action.parameters.get("target_point")
            if target_point is not None:
                steps.append(ExecutionStep(step_type=StepType.CLICK, payload={"point": target_point}))
            return tuple(steps)

        if action.action_type == ActionType.SELECT_TARGET:
            target_point = self._require_point(action, "target_point")
            return (
                ExecutionStep(step_type=StepType.FOCUS_WINDOW),
                ExecutionStep(step_type=StepType.CLICK, payload={"point": target_point}),
            )

        if action.action_type == ActionType.CONFIRM_ACTION:
            confirm_point = self._require_point(action, "confirm_point")
            return (
                ExecutionStep(step_type=StepType.FOCUS_WINDOW),
                ExecutionStep(step_type=StepType.CLICK, payload={"point": confirm_point}),
            )

        if action.action_type == ActionType.RECOVER:
            wait_seconds = float(action.parameters.get("wait_seconds", 0.2))
            return (
                ExecutionStep(step_type=StepType.FOCUS_WINDOW),
                ExecutionStep(step_type=StepType.WAIT, payload={"seconds": wait_seconds}),
            )

        raise ActionTranslationError(f"unsupported action type={action.action_type}")

    def _require_point(self, action: AutomationAction, key: str) -> tuple[int, int]:
        point = action.parameters.get(key)
        if point is None:
            raise ActionTranslationError(
                f"action type={action.action_type.value} requires parameter={key}"
            )
        return tuple(point)
