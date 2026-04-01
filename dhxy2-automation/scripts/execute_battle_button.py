from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from src.app.window_binding import resolve_window_session
from src.executor import ButtonCalibration, Win32SendInputGateway
from src.platform import PyWin32WindowGateway


@dataclass(frozen=True)
class ExecuteResult:
    button_ref: str
    handle: int
    client_x: int
    client_y: int
    before_hash: str
    after_hash: str
    frame_changed: bool
    before_path: str
    after_path: str
    elapsed_ms: int


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute one battle button click by button_ref.")
    parser.add_argument("--button-ref", required=True)
    parser.add_argument("--label", default="battle-action")
    parser.add_argument("--delay", type=float, default=0.25, help="Seconds to wait after click before capture.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    project_root = Path(__file__).resolve().parents[1]
    calibration = ButtonCalibration.load(project_root / "configs" / "ui" / "button-calibration.json")
    client_x, client_y = calibration.resolve(args.button_ref)

    output_root = project_root / "runs" / "artifacts" / "probes"
    output_root.mkdir(parents=True, exist_ok=True)

    session = resolve_window_session(
        project_root / "configs" / "accounts" / "instance-1.json",
        gateway=PyWin32WindowGateway(),
    )
    session.focus()
    gateway = Win32SendInputGateway()

    started_at = time.time()
    before = session.capture_client()
    gateway.click(client_x, client_y)
    time.sleep(max(0.0, float(args.delay)))
    after = session.capture_client()
    elapsed_ms = int((time.time() - started_at) * 1000)

    before_path = output_root / f"{args.label}-{args.button_ref.replace('.', '-')}-before.png"
    after_path = output_root / f"{args.label}-{args.button_ref.replace('.', '-')}-after.png"
    before.image.save(before_path)
    after.image.save(after_path)

    result = ExecuteResult(
        button_ref=args.button_ref,
        handle=session.handle,
        client_x=client_x,
        client_y=client_y,
        before_hash=before.frame_hash,
        after_hash=after.frame_hash,
        frame_changed=before.frame_hash != after.frame_hash,
        before_path=str(before_path),
        after_path=str(after_path),
        elapsed_ms=elapsed_ms,
    )

    json_path = output_root / f"{args.label}-{args.button_ref.replace('.', '-')}.json"
    json_path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
