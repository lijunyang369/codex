from __future__ import annotations

from dataclasses import dataclass

from src.domain import ActionPlan, AutomationContext, BattleObservation, TransitionResult
from src.executor import ActionExecutor, ExecutionResult, InputGateway
from src.platform import WindowSession
from src.policy import FixedRulePolicy
from src.runtime import RuntimeSession
from src.state_machine import BattleStateMachine
from src.app.interfaces import ObservationProvider


@dataclass(frozen=True)
class AppTickResult:
    observation: BattleObservation
    transitions: tuple[TransitionResult, ...]
    executed_actions: tuple[ExecutionResult, ...]


class BattleAutomationApp:
    def __init__(
        self,
        context: AutomationContext,
        window_session: WindowSession,
        observation_provider: ObservationProvider,
        state_machine: BattleStateMachine,
        policy: FixedRulePolicy,
        executor: ActionExecutor,
        runtime_session: RuntimeSession,
        input_gateway: InputGateway,
    ) -> None:
        self._context = context
        self._window_session = window_session
        self._observation_provider = observation_provider
        self._state_machine = state_machine
        self._policy = policy
        self._executor = executor
        self._runtime_session = runtime_session
        self._input_gateway = input_gateway

    def run_once(self) -> AppTickResult:
        observation = self._observation_provider.observe(self._window_session)
        self._runtime_session.record_observation(observation)

        transitions: list[TransitionResult] = []
        executed_actions: list[ExecutionResult] = []

        state_transition = self._state_machine.tick(observation, self._context)
        self._runtime_session.record_transition(state_transition)
        transitions.append(state_transition)

        plan = self._policy.build_plan(observation, self._context)
        if plan.is_empty():
            return AppTickResult(
                observation=observation,
                transitions=tuple(transitions),
                executed_actions=tuple(executed_actions),
            )

        begin_transition = self._state_machine.begin_action(plan, self._context)
        self._runtime_session.record_transition(begin_transition)
        transitions.append(begin_transition)

        for action in plan.actions:
            self._runtime_session.record_action(action, reason=plan.reason)
            executed_actions.append(
                self._executor.execute(
                    action=action,
                    window_session=self._window_session,
                    input_gateway=self._input_gateway,
                )
            )

        finish_transition = self._state_machine.complete_action(self._context, accepted_by_ui=True)
        self._runtime_session.record_transition(finish_transition)
        transitions.append(finish_transition)

        return AppTickResult(
            observation=observation,
            transitions=tuple(transitions),
            executed_actions=tuple(executed_actions),
        )
