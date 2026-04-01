from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.app.account_loader import AccountBindingLoader
from src.app.config_refs import configs_root, resolve_config_reference
from src.app.observation_provider import DefaultObservationProvider, DefaultObservationProviderConfig
from src.app.profile_loader import CharacterProfileLoader
from src.app.service import BattleAutomationApp
from src.app.window_binding import resolve_window_session
from src.domain import AccountBinding, ActionType, AutomationContext, BattleState, MatchResult, OCRResult
from src.executor import ActionExecutor, ActionTranslator, ButtonCalibration, InputGateway
from src.perception import (
    NullOCRReader,
    NullTemplateMatcher,
    OpenCvTemplateMatcher,
    RegionRequest,
    StaticOCRReader,
    StaticTemplateMatcher,
    TemplateCatalog,
)
from src.platform import PyWin32WindowGateway, WindowSession
from src.policy import FixedActionRule, FixedRulePolicy
from src.runtime import RuntimeSession
from src.state_machine import BattleStateMachine


@dataclass(frozen=True)
class BootstrapPaths:
    env_config: Path
    account_config: Path
    scenario_config: Path


class JsonConfigLoader:
    def load(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8-sig"))


class NoOpInputGateway(InputGateway):
    def __init__(self) -> None:
        self.operations: list[tuple[str, object]] = []

    def click(self, x: int, y: int) -> None:
        self.operations.append(("click", (x, y)))

    def press_key(self, key: str) -> None:
        self.operations.append(("key", key))

    def wait(self, seconds: float) -> None:
        self.operations.append(("wait", seconds))


def build_app(
    paths: BootstrapPaths,
    window_session: WindowSession,
    input_gateway: InputGateway | None = None,
) -> BattleAutomationApp:
    loader = JsonConfigLoader()
    env_config = loader.load(paths.env_config)
    account_binding = AccountBindingLoader().load(paths.account_config)
    scenario_config = loader.load(paths.scenario_config)

    initial_state = BattleState(scenario_config.get("initial_state", "OUT_OF_BATTLE"))
    context = AutomationContext(
        instance_id=account_binding.instance_id,
        battle_session_id=f"{scenario_config['scenario_id']}-session",
        state=initial_state,
        previous_stable_state=initial_state,
        previous_state=initial_state,
    )
    character_profile = _load_character_profile(paths.account_config, account_binding)
    if character_profile is not None:
        context.character_profile = character_profile
        context.metadata["character_profile"] = character_profile.to_dict()

    runtime_session = RuntimeSession.create(Path(env_config["runs_root"]), context)

    primary_rule = scenario_config["primary_rule"]
    policy = FixedRulePolicy(
        FixedActionRule(
            action_type=ActionType(primary_rule["action_type"]),
            reason=primary_rule["reason"],
            target=primary_rule.get("target"),
            parameters=dict(primary_rule.get("parameters", {})),
        )
    )

    regions = tuple(
        RegionRequest(
            name=entry["name"],
            rect=_to_rect(entry.get("rect")),
            use_template_match=bool(entry.get("use_template_match", True)),
            use_ocr=bool(entry.get("use_ocr", False)),
        )
        for entry in scenario_config.get("regions", [])
    )

    dry_run = bool(env_config.get("dry_run", False))
    template_matcher = _build_template_matcher(scenario_config, env_config, dry_run)
    ocr_reader = _build_ocr_reader(scenario_config, dry_run)
    observation_provider = DefaultObservationProvider(
        template_matcher=template_matcher,
        ocr_reader=ocr_reader,
        config=DefaultObservationProviderConfig(regions=regions),
    )
    executor = _build_executor(env_config)

    return BattleAutomationApp(
        context=context,
        window_session=window_session,
        observation_provider=observation_provider,
        state_machine=BattleStateMachine(),
        policy=policy,
        executor=executor,
        runtime_session=runtime_session,
        input_gateway=input_gateway or NoOpInputGateway(),
    )


def build_app_from_configs(
    paths: BootstrapPaths,
    input_gateway: InputGateway | None = None,
    gateway: PyWin32WindowGateway | None = None,
) -> BattleAutomationApp:
    window_session = resolve_window_session(paths.account_config, gateway=gateway)
    return build_app(paths=paths, window_session=window_session, input_gateway=input_gateway)


def _build_executor(env_config: dict[str, Any]) -> ActionExecutor:
    button_calibration_path = env_config.get("button_calibration")
    button_calibration = None
    if button_calibration_path:
        calibration_file = Path(button_calibration_path)
        if calibration_file.exists():
            button_calibration = ButtonCalibration.load(calibration_file)
    return ActionExecutor(translator=ActionTranslator(button_calibration=button_calibration))


def _load_character_profile(account_config_path: Path, account_binding: AccountBinding):
    character_config_ref = account_binding.character_config_ref
    if not character_config_ref:
        return None
    character_root = configs_root(account_config_path) / "characters"
    character_config_path = resolve_config_reference(
        account_config_path,
        str(character_config_ref),
        allowed_root=character_root,
    )
    return CharacterProfileLoader().load(character_config_path)


def _build_template_matcher(scenario_config: dict[str, Any], env_config: dict[str, Any], dry_run: bool):
    if dry_run:
        matches_by_region: dict[str, tuple[MatchResult, ...]] = {}
        for region_name, entries in scenario_config.get("mock_matches", {}).items():
            matches_by_region[region_name] = tuple(
                MatchResult(
                    template_id=entry["template_id"],
                    confidence=float(entry["confidence"]),
                    region_name=region_name,
                    bounds=tuple(entry["bounds"]) if entry.get("bounds") else None,
                    note=entry.get("note"),
                )
                for entry in entries
            )
        return StaticTemplateMatcher(matches_by_region)

    template_catalog_path = env_config.get("template_catalog")
    if template_catalog_path:
        catalog = TemplateCatalog.load(Path(template_catalog_path))
        if not catalog.is_empty():
            return OpenCvTemplateMatcher(catalog)
    return NullTemplateMatcher()


def _build_ocr_reader(scenario_config: dict[str, Any], dry_run: bool):
    if dry_run:
        lines_by_region: dict[str, tuple[OCRResult, ...]] = {}
        for region_name, entries in scenario_config.get("mock_ocr", {}).items():
            lines_by_region[region_name] = tuple(
                OCRResult(
                    text=entry["text"],
                    confidence=float(entry["confidence"]),
                    region_name=region_name,
                    bounds=tuple(entry["bounds"]) if entry.get("bounds") else None,
                )
                for entry in entries
            )
        return StaticOCRReader(lines_by_region)
    return NullOCRReader()


def _to_rect(raw: list[int] | tuple[int, int, int, int] | None):
    if raw is None:
        return None
    from src.platform import Rect

    left, top, right, bottom = raw
    return Rect(left=left, top=top, right=right, bottom=bottom)
