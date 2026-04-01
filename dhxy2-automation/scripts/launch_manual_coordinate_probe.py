from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _resolve_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_project_root_on_sys_path(project_root: Path) -> None:
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _show_startup_error(message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("DHXY Manual Coordinate Probe", message)
        root.destroy()
    except Exception:
        print(message, file=sys.stderr)


def main() -> int:
    project_root = _resolve_project_root()
    _ensure_project_root_on_sys_path(project_root)
    os.environ["DHXY_TOOL_LAUNCHER"] = str(Path(__file__).resolve())
    os.environ["DHXY_TOOL_PROJECT_ROOT"] = str(project_root)
    try:
        from src.app.manual_probe_tool import launch_manual_coordinate_probe

        launch_manual_coordinate_probe(project_root)
        return 0
    except Exception as exc:
        error_detail = "".join(traceback.format_exception(exc)).strip()
        _show_startup_error(f"Probe launcher failed.\n\nProject root: {project_root}\n\n{error_detail}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
