from __future__ import annotations

import json
from pathlib import Path

from src.platform import PyWin32WindowGateway, WindowFinder, WindowSearchCriteria, WindowSession


def resolve_window_session(
    account_config_path: Path,
    gateway: PyWin32WindowGateway | None = None,
) -> WindowSession:
    account_config = json.loads(account_config_path.read_text(encoding="utf-8-sig"))
    resolved_gateway = gateway or PyWin32WindowGateway()
    finder = WindowFinder(resolved_gateway)
    return finder.find(
        WindowSearchCriteria(
            title_contains=account_config.get("window_title"),
            class_name=account_config.get("window_class"),
            handle=account_config.get("window_handle"),
            require_visible=True,
        )
    )
