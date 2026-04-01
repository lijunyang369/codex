from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image


@dataclass(frozen=True)
class ButtonDetection:
    index: int
    name: str
    center: tuple[int, int]
    bounds: tuple[int, int, int, int]
    area: int


def detect_battle_command_buttons(
    client_rgb: Image.Image,
    names: list[str] | tuple[str, ...],
) -> tuple[ButtonDetection, ...]:
    boxes = _detect_button_boxes(client_rgb)
    detections: list[ButtonDetection] = []
    for idx, (x1, y1, x2, y2, area) in enumerate(boxes):
        center = ((x1 + x2) // 2, (y1 + y2) // 2)
        name = names[idx] if idx < len(names) else f"button_{idx + 1}"
        detections.append(
            ButtonDetection(
                index=idx,
                name=name,
                center=center,
                bounds=(x1, y1, x2, y2),
                area=area,
            )
        )
    return tuple(detections)


def _detect_button_boxes(client_rgb: Image.Image) -> list[tuple[int, int, int, int, int]]:
    frame = np.array(client_rgb.convert("RGB"))
    height, width, _channels = frame.shape
    roi_x1, roi_x2 = max(0, width - 140), width
    roi_y1, roi_y2 = max(0, int(height * 0.18)), min(height, int(height * 0.68))
    roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]

    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    lower1 = np.array([0, 30, 20], dtype=np.uint8)
    upper1 = np.array([10, 255, 255], dtype=np.uint8)
    lower2 = np.array([170, 30, 20], dtype=np.uint8)
    upper2 = np.array([180, 255, 255], dtype=np.uint8)
    hsv_mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)

    red = roi[:, :, 0].astype(np.int16)
    green = roi[:, :, 1].astype(np.int16)
    blue = roi[:, :, 2].astype(np.int16)
    rgb_mask = np.where((red > 60) & (red > green + 12) & (red > blue + 12), 255, 0).astype(np.uint8)
    mask = cv2.bitwise_or(hsv_mask, rgb_mask)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections: list[tuple[int, int, int, int, int]] = []
    for contour in contours:
        x, y, box_width, box_height = cv2.boundingRect(contour)
        area = int(box_width * box_height)
        if area < 350 or area > 4000:
            continue
        if box_width < 24 or box_height < 20:
            continue
        x1 = roi_x1 + x
        y1 = roi_y1 + y
        x2 = x1 + box_width
        y2 = y1 + box_height
        detections.append((x1, y1, x2, y2, area))

    detections.sort(key=lambda item: item[1])
    filtered: list[tuple[int, int, int, int, int]] = []
    for item in detections:
        if not filtered:
            filtered.append(item)
            continue

        prev = filtered[-1]
        if item[1] <= prev[3] - 8:
            x1 = min(prev[0], item[0])
            y1 = min(prev[1], item[1])
            x2 = max(prev[2], item[2])
            y2 = max(prev[3], item[3])
            area = max(prev[4], item[4])
            filtered[-1] = (x1, y1, x2, y2, area)
            continue

        filtered.append(item)

    return filtered
