from __future__ import annotations

from dataclasses import dataclass

from src.app.interfaces import ObservationProvider
from src.domain import BattleObservation, MatchResult, OCRResult
from src.perception import ObservationBuilder
from src.perception.interfaces import OCRReader, TemplateMatcher
from src.perception.services import RegionRequest
from src.platform import WindowSession
from src.platform.models import Rect


@dataclass(frozen=True)
class DefaultObservationProviderConfig:
    regions: tuple[RegionRequest, ...]


class DefaultObservationProvider(ObservationProvider):
    def __init__(
        self,
        template_matcher: TemplateMatcher,
        ocr_reader: OCRReader,
        builder: ObservationBuilder | None = None,
        config: DefaultObservationProviderConfig | None = None,
    ) -> None:
        self._template_matcher = template_matcher
        self._ocr_reader = ocr_reader
        self._builder = builder or ObservationBuilder()
        self._config = config or DefaultObservationProviderConfig(regions=())

    def observe(self, window_session: WindowSession) -> BattleObservation:
        window_info = window_session.snapshot()
        frame = window_session.capture_client()

        matches: list[MatchResult] = []
        ocr_texts: list[OCRResult] = []
        named_regions: dict[str, Rect] = {}

        for region in self._config.regions:
            if region.rect is not None:
                named_regions[region.name] = region.rect
            if region.use_template_match:
                matches.extend(self._template_matcher.match(frame, region.name, region.rect))
            if region.use_ocr:
                ocr_texts.extend(self._ocr_reader.read_lines(frame, region.name, region.rect))

        return self._builder.build(
            frame=frame,
            window_info=window_info,
            matches=tuple(matches),
            ocr_texts=tuple(ocr_texts),
            named_regions=named_regions,
        )
