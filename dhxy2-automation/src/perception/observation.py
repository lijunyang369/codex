from __future__ import annotations

from dataclasses import dataclass

from src.domain import BattleObservation, MatchResult, OCRResult
from src.perception.battle_recognizers import BattleRecognitionSuite
from src.perception.recognizer_models import RecognitionModuleResult, RecognitionSnapshot
from src.platform import FrameCapture, WindowInfo
from src.platform.models import Rect


@dataclass(frozen=True)
class ObservationSignalConfig:
    enabled_module_ids: tuple[str, ...] = (
        "battle_scene",
        "battle_round",
        "battle_action_prompt",
        "battle_skill_bar",
        "battle_target_select",
        "battle_settlement",
    )


class ObservationBuilder:
    def __init__(self, config: ObservationSignalConfig | None = None) -> None:
        self._config = config or ObservationSignalConfig()
        self._suite = BattleRecognitionSuite()

    @property
    def module_specs(self):
        return tuple(spec for spec in self._suite.specs if spec.module_id in self._config.enabled_module_ids)

    def build_snapshot(
        self,
        matches: tuple[MatchResult, ...],
        ocr_texts: tuple[OCRResult, ...] = (),
        named_regions: dict[str, Rect] | None = None,
    ) -> RecognitionSnapshot:
        regions = named_regions or {}
        return RecognitionSnapshot(
            matches=matches,
            ocr_texts=ocr_texts,
            named_regions={name: rect.as_bbox() for name, rect in regions.items()},
        )

    def evaluate_snapshot(self, snapshot: RecognitionSnapshot) -> dict[str, RecognitionModuleResult]:
        results = self._suite.evaluate(snapshot)
        return {
            module_id: result
            for module_id, result in results.items()
            if module_id in self._config.enabled_module_ids
        }

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
        snapshot = self.build_snapshot(matches=matches, ocr_texts=ocr_texts, named_regions=named_regions)
        return self.build_from_snapshot(
            frame=frame,
            window_info=window_info,
            snapshot=snapshot,
            last_action_feedback=last_action_feedback,
            anomaly_reason=anomaly_reason,
        )

    def build_from_snapshot(
        self,
        frame: FrameCapture,
        window_info: WindowInfo,
        snapshot: RecognitionSnapshot,
        last_action_feedback: str | None = None,
        anomaly_reason: str | None = None,
    ) -> BattleObservation:
        module_results = self.evaluate_snapshot(snapshot)
        confidence_summary = self._calculate_confidence_summary(snapshot.matches, snapshot.ocr_texts)

        return BattleObservation(
            battle_ui_visible=module_results.get("battle_scene", _empty_result()).detected,
            action_prompt_visible=module_results.get("battle_action_prompt", _empty_result()).detected,
            skill_panel_visible=module_results.get("battle_skill_bar", _empty_result()).detected,
            target_select_visible=module_results.get("battle_target_select", _empty_result()).detected,
            settlement_visible=module_results.get("battle_settlement", _empty_result()).detected,
            window_alive=True,
            window_focused=window_info.is_foreground,
            frame_timestamp=frame.captured_at,
            frame_hash=frame.frame_hash,
            confidence_summary=confidence_summary,
            matches=snapshot.matches,
            ocr_texts=snapshot.ocr_texts,
            named_regions=dict(snapshot.named_regions),
            last_action_feedback=last_action_feedback,
            anomaly_reason=anomaly_reason,
        )

    def _calculate_confidence_summary(
        self,
        matches: tuple[MatchResult, ...],
        ocr_texts: tuple[OCRResult, ...],
    ) -> float:
        scores = [match.confidence for match in matches] + [line.confidence for line in ocr_texts]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 4)


def _empty_result() -> RecognitionModuleResult:
    return RecognitionModuleResult(
        module_id="",
        label="",
        region_name="",
        mode="",
        detected=False,
        confidence=0.0,
        summary="",
    )
