from __future__ import annotations

from dataclasses import dataclass

from src.domain import BattleObservation, MatchResult, OCRResult
from src.platform import FrameCapture, WindowInfo
from src.platform.models import Rect


@dataclass(frozen=True)
class ObservationSignalConfig:
    battle_ui_templates: tuple[str, ...] = (
        "battle_ui",
        "battle_action_prompt",
        "battle_skill_bar",
    )
    action_prompt_templates: tuple[str, ...] = ("battle_action_prompt",)
    skill_panel_templates: tuple[str, ...] = ("battle_skill_bar",)
    target_select_templates: tuple[str, ...] = ("battle_target_panel",)
    settlement_templates: tuple[str, ...] = ("battle_settlement",)


class ObservationBuilder:
    def __init__(self, config: ObservationSignalConfig | None = None) -> None:
        self._config = config or ObservationSignalConfig()

    def build(
        self,
        frame: FrameCapture,
        window_info: WindowInfo,
        matches: tuple[MatchResult, ...],
        ocr_texts: tuple[OCRResult, ...] = (),
        named_regions: dict[str, Rect] | None = None,
        last_action_feedback: str | None = None,
        anomaly_reason: str | None = None,
    ) -> BattleObservation:
        regions = named_regions or {}
        confidence_summary = self._calculate_confidence_summary(matches, ocr_texts)

        return BattleObservation(
            battle_ui_visible=self._has_any_match(matches, self._config.battle_ui_templates),
            action_prompt_visible=self._has_any_match(matches, self._config.action_prompt_templates),
            skill_panel_visible=self._has_any_match(matches, self._config.skill_panel_templates),
            target_select_visible=self._has_any_match(matches, self._config.target_select_templates),
            settlement_visible=self._has_any_match(matches, self._config.settlement_templates),
            window_alive=True,
            window_focused=window_info.is_foreground,
            frame_timestamp=frame.captured_at,
            frame_hash=frame.frame_hash,
            confidence_summary=confidence_summary,
            matches=matches,
            ocr_texts=ocr_texts,
            named_regions={name: rect.as_bbox() for name, rect in regions.items()},
            last_action_feedback=last_action_feedback,
            anomaly_reason=anomaly_reason,
        )

    def _has_any_match(self, matches: tuple[MatchResult, ...], template_ids: tuple[str, ...]) -> bool:
        template_id_set = set(template_ids)
        return any(match.template_id in template_id_set for match in matches)

    def _calculate_confidence_summary(
        self,
        matches: tuple[MatchResult, ...],
        ocr_texts: tuple[OCRResult, ...],
    ) -> float:
        scores = [match.confidence for match in matches] + [line.confidence for line in ocr_texts]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 4)
