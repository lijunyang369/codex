from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain import MatchResult, OCRResult


@dataclass(frozen=True)
class RecognitionSnapshot:
    matches: tuple[MatchResult, ...]
    ocr_texts: tuple[OCRResult, ...]
    named_regions: dict[str, tuple[int, int, int, int]] = field(default_factory=dict)

    def has_region(self, region_name: str) -> bool:
        return region_name in self.named_regions

    def matching_templates(self, template_ids: tuple[str, ...]) -> tuple[MatchResult, ...]:
        template_id_set = set(template_ids)
        return tuple(match for match in self.matches if match.template_id in template_id_set)

    def ocr_lines_for_region(self, region_name: str) -> tuple[OCRResult, ...]:
        return tuple(line for line in self.ocr_texts if line.region_name == region_name)


@dataclass(frozen=True)
class RecognitionModuleSpec:
    module_id: str
    label: str
    region_name: str
    mode: str


@dataclass(frozen=True)
class RecognitionModuleResult:
    module_id: str
    label: str
    region_name: str
    mode: str
    detected: bool
    confidence: float
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
