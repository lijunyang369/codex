from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from PIL import Image


class OCRProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderHealth:
    status: str
    provider: str
    detail: str = ""


@dataclass(frozen=True)
class ProviderTextResult:
    text: str
    confidence: float
    provider: str


@dataclass(frozen=True)
class ProviderLineResult:
    text: str
    confidence: float
    bounds: tuple[int, int, int, int] | None = None


@dataclass(frozen=True)
class ProviderLinesResult:
    lines: tuple[ProviderLineResult, ...] = field(default_factory=tuple)
    provider: str = "unknown"


class OCRProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> ProviderHealth:
        raise NotImplementedError

    @abstractmethod
    def read_text(self, image: Image.Image, *, profile: str, allowlist: str | None) -> ProviderTextResult:
        raise NotImplementedError

    @abstractmethod
    def read_lines(self, image: Image.Image, *, profile: str, allowlist: str | None) -> ProviderLinesResult:
        raise NotImplementedError
