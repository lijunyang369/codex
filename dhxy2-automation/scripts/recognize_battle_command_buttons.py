from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from PIL import ImageDraw

from src.app.window_binding import resolve_window_session
from src.perception import detect_battle_command_buttons
from src.platform import PyWin32WindowGateway


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect battle command buttons from current battle frame.")
    parser.add_argument(
        "--names",
        default="spell,item,defend,protect,summon,recall,catch,escape",
        help="Comma-separated button names ordered from top to bottom.",
    )
    parser.add_argument("--label", default="battle-command-detect")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    project_root = Path(__file__).resolve().parents[1]
    output_root = project_root / "runs" / "artifacts" / "probes"
    output_root.mkdir(parents=True, exist_ok=True)

    names = [item.strip() for item in str(args.names).split(",") if item.strip()]

    session = resolve_window_session(
        project_root / "configs" / "accounts" / "instance-1.json",
        gateway=PyWin32WindowGateway(),
    )
    session.focus()
    frame = session.capture_client()
    image = frame.image.convert("RGB")

    detections = detect_battle_command_buttons(image, names)

    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    for entry in detections:
        x1, y1, x2, y2 = entry.bounds
        draw.rectangle((x1, y1, x2, y2), outline=(0, 255, 255), width=2)
        draw.text((x1 - 70, y1), f"{entry.index}:{entry.name}", fill=(255, 255, 0))
        cx, cy = entry.center
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(0, 255, 0))

    raw_path = output_root / f"{args.label}-raw.png"
    ann_path = output_root / f"{args.label}-annotated.png"
    json_path = output_root / f"{args.label}.json"
    image.save(raw_path)
    annotated.save(ann_path)

    payload = {
        "handle": session.handle,
        "frame_hash": frame.frame_hash,
        "raw_path": str(raw_path),
        "annotated_path": str(ann_path),
        "detection_count": len(detections),
        "detections": [asdict(entry) for entry in detections],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
