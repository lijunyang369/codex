from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.domain import MatchResult, OCRResult
from src.perception.interfaces import OCRReader, TemplateMatcher
from src.perception.template_catalog import TemplateCatalog
from src.platform import FrameCapture
from src.platform.models import Rect


@dataclass(frozen=True)
class RegionRequest:
    name: str
    rect: Rect | None = None
    use_template_match: bool = True
    use_ocr: bool = False


class NullTemplateMatcher:
    def match(self, frame: FrameCapture, region_name: str, rect: Rect | None = None) -> tuple[MatchResult, ...]:
        return ()


class NullOCRReader:
    def read_lines(self, frame: FrameCapture, region_name: str, rect: Rect | None = None) -> tuple[OCRResult, ...]:
        return ()


class StaticTemplateMatcher:
    def __init__(self, matches_by_region: dict[str, tuple[MatchResult, ...]]) -> None:
        self._matches_by_region = matches_by_region

    def match(self, frame: FrameCapture, region_name: str, rect: Rect | None = None) -> tuple[MatchResult, ...]:
        return self._matches_by_region.get(region_name, ())


class StaticOCRReader:
    def __init__(self, lines_by_region: dict[str, tuple[OCRResult, ...]]) -> None:
        self._lines_by_region = lines_by_region

    def read_lines(self, frame: FrameCapture, region_name: str, rect: Rect | None = None) -> tuple[OCRResult, ...]:
        return self._lines_by_region.get(region_name, ())


class BattleRoundOCRReader:
    def __init__(self) -> None:
        self._digit_templates = _build_digit_templates()

    def read_lines(self, frame: FrameCapture, region_name: str, rect: Rect | None = None) -> tuple[OCRResult, ...]:
        if region_name != "battle_main" or rect is None:
            return ()
        digit_text, confidence = self._extract_round_digits(frame.image, rect)
        if not digit_text:
            return ()
        return (
            OCRResult(
                text=f"第{digit_text}回合",
                confidence=confidence,
                region_name=region_name,
                bounds=rect.as_bbox(),
            ),
        )

    def _extract_round_digits(self, image: Image.Image, rect: Rect) -> tuple[str, float]:
        crop = image.crop(rect.as_bbox())
        mask = build_round_digit_mask(crop)
        return _match_digit_band(mask, self._digit_templates)


def build_round_digit_mask(image: Image.Image) -> np.ndarray:
    rgb = np.array(image.convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)

    lower = np.array([10, 80, 120], dtype=np.uint8)
    upper = np.array([40, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.medianBlur(mask, 3)
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def build_round_digit_template(image: Image.Image) -> np.ndarray | None:
    mask = build_round_digit_mask(image)
    digit_mask = _extract_digit_mask(mask)
    if digit_mask is None:
        return None
    return cv2.resize(digit_mask, (22, 30), interpolation=cv2.INTER_NEAREST)


def refresh_round_digit_template_cache() -> None:
    _build_digit_templates.cache_clear()


class OpenCvTemplateMatcher:
    def __init__(self, catalog: TemplateCatalog) -> None:
        self._catalog = catalog

    def match(self, frame: FrameCapture, region_name: str, rect: Rect | None = None) -> tuple[MatchResult, ...]:
        frame_array = self._to_gray_array(frame.image, rect)
        offset_x = rect.left if rect is not None else 0
        offset_y = rect.top if rect is not None else 0
        matches: list[MatchResult] = []

        for definition in self._catalog.for_region(region_name):
            template = self._load_template(definition.file)
            if template.shape[0] > frame_array.shape[0] or template.shape[1] > frame_array.shape[1]:
                continue
            result = cv2.matchTemplate(frame_array, template, cv2.TM_CCOEFF_NORMED)
            _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
            if float(max_val) < definition.threshold:
                continue
            left, top = max_loc
            right = left + template.shape[1]
            bottom = top + template.shape[0]
            matches.append(
                MatchResult(
                    template_id=definition.id,
                    confidence=round(float(max_val), 4),
                    region_name=region_name,
                    bounds=(left + offset_x, top + offset_y, right + offset_x, bottom + offset_y),
                    note=definition.note,
                )
            )

        return tuple(matches)

    @staticmethod
    def _to_gray_array(image: Image.Image, rect: Rect | None) -> np.ndarray:
        if rect is not None:
            image = image.crop(rect.as_bbox())
        return cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)

    @staticmethod
    @lru_cache(maxsize=128)
    def _load_template(path: Path) -> np.ndarray:
        image = Image.open(path).convert("RGB")
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)


def _classify_digit_roi(
    roi: np.ndarray,
    templates: dict[str, tuple[np.ndarray, ...]],
) -> tuple[str | None, float]:
    normalized = cv2.resize(roi, (22, 30), interpolation=cv2.INTER_NEAREST)
    best_digit: str | None = None
    best_score = -1.0
    for digit, variants in templates.items():
        for variant in variants:
            result = cv2.matchTemplate(normalized, variant, cv2.TM_CCOEFF_NORMED)
            score = float(result[0][0])
            if score > best_score:
                best_score = score
                best_digit = digit
    if best_score < 0.35:
        return None, best_score
    return best_digit, round(best_score, 4)


def _match_digit_band(
    mask: np.ndarray,
    templates: dict[str, tuple[np.ndarray, ...]],
) -> tuple[str, float]:
    band = _extract_digit_band(mask)
    if band is None:
        return "", 0.0

    enlarged_band = cv2.resize(
        band,
        (max(1, band.shape[1] * 2), max(1, band.shape[0] * 2)),
        interpolation=cv2.INTER_NEAREST,
    )

    best_digit = ""
    best_score = -1.0
    for digit, variants in templates.items():
        for variant in variants:
            if variant.shape[0] > enlarged_band.shape[0] or variant.shape[1] > enlarged_band.shape[1]:
                continue
            result = cv2.matchTemplate(enlarged_band, variant, cv2.TM_CCOEFF_NORMED)
            score = float(result.max())
            if score > best_score:
                best_score = score
                best_digit = digit

    if best_score < 0.45:
        return "", 0.0
    return best_digit, round(best_score, 4)


def _extract_digit_mask(mask: np.ndarray) -> np.ndarray | None:
    height, width = mask.shape[:2]
    component_mask = _extract_digit_components(mask)
    if component_mask is not None:
        return component_mask

    # Fallback for unexpected layouts: keep the previous band logic.
    left = max(0, int(width * 0.2))
    right = min(width, int(width * 0.42))
    if right <= left:
        return None

    band = mask[:, left:right]
    if not np.any(band):
        return None

    points = cv2.findNonZero(band)
    if points is None:
        return None
    x, y, w, h = cv2.boundingRect(points)
    if w <= 0 or h <= 0:
        return None
    return band[y : y + h, x : x + w]


def _extract_digit_components(mask: np.ndarray) -> np.ndarray | None:
    height, width = mask.shape[:2]
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    selected_boxes: list[tuple[int, int, int, int]] = []

    digit_left = width * 0.26
    digit_right = width * 0.36
    min_area = max(6, int(height * 0.06))

    for label in range(1, num_labels):
        x, y, w, h, area = stats[label]
        cx, cy = centroids[label]
        if area < min_area:
            continue
        if not (digit_left <= cx <= digit_right):
            continue
        if h < max(4, int(height * 0.12)):
            continue
        selected_boxes.append((x, y, w, h))

    if not selected_boxes:
        return None

    left = min(x for x, _y, _w, _h in selected_boxes)
    top = min(y for _x, y, _w, _h in selected_boxes)
    right = max(x + w for x, _y, w, _h in selected_boxes)
    bottom = max(y + h for _x, y, _w, h in selected_boxes)
    return mask[top:bottom, left:right]


def _extract_digit_band(mask: np.ndarray) -> np.ndarray | None:
    _height, width = mask.shape[:2]
    left = max(0, int(width * 0.2))
    right = min(width, int(width * 0.42))
    if right <= left:
        return None

    band = mask[:, left:right]
    if not np.any(band):
        return None

    points = cv2.findNonZero(band)
    if points is None:
        return None
    x, y, w, h = cv2.boundingRect(points)
    if w <= 0 or h <= 0:
        return None
    return band[y : y + h, x : x + w]


@lru_cache(maxsize=1)
def _build_digit_templates() -> dict[str, tuple[np.ndarray, ...]]:
    fonts = _resolve_digit_fonts()
    templates: dict[str, list[np.ndarray]] = {str(index): [] for index in range(10)}
    real_templates = _load_real_digit_templates()
    for digit, template in real_templates.items():
        templates[digit].append(template)
    for digit in templates:
        # Once the user has saved a real in-game template for a digit, do not
        # mix in generated font fallbacks for that same digit.
        if digit in real_templates:
            continue
        for font in fonts:
            canvas = Image.new("RGB", (28, 36), "black")
            draw = ImageDraw.Draw(canvas)
            draw.text(
                (4, 0),
                digit,
                font=font,
                fill=(255, 210, 80),
                stroke_width=2,
                stroke_fill=(45, 25, 0),
            )
            gray = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
            templates[digit].append(cv2.resize(binary, (22, 30), interpolation=cv2.INTER_NEAREST))
    return {digit: tuple(items) for digit, items in templates.items()}


def _load_real_digit_templates() -> dict[str, np.ndarray]:
    base_dir = Path(__file__).resolve().parents[2] / "resources" / "templates" / "battle"
    templates: dict[str, np.ndarray] = {}
    for digit in range(10):
        path = base_dir / f"battle_round_digit_{digit}.png"
        if not path.is_file():
            continue
        image = Image.open(path).convert("L")
        array = np.array(image)
        _, binary = cv2.threshold(array, 60, 255, cv2.THRESH_BINARY)
        templates[str(digit)] = cv2.resize(binary, (22, 30), interpolation=cv2.INTER_NEAREST)
    return templates


def _resolve_digit_fonts() -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, ...]:
    candidates = [
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts" / "msyhbd.ttc",
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts" / "msyh.ttc",
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts" / "simhei.ttf",
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts" / "arialbd.ttf",
    ]
    fonts: list[ImageFont.FreeTypeFont | ImageFont.ImageFont] = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            fonts.append(ImageFont.truetype(str(path), 26))
        except OSError:
            continue
    if not fonts:
        fonts.append(ImageFont.load_default())
    return tuple(fonts)
