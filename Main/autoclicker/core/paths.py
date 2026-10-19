"""Platform-aware paths (config, data, logs, exports, bundled resources)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from .. import APP_ID


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def resource_dir() -> Path:
    """Directory of the `autoclicker` package (works frozen or from source)."""
    if is_frozen():
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base / "autoclicker"
    return Path(__file__).resolve().parents[1]


def asset(name: str) -> Path:
    return resource_dir() / "assets" / name


def data_dir() -> Path:
    override = os.environ.get("AUTOCLICKER_4R022_HOME")
    if override:
        base = Path(override)
    elif sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / APP_ID
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / APP_ID
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / APP_ID
    base.mkdir(parents=True, exist_ok=True)
    return base


def _sub(name: str) -> Path:
    p = data_dir() / name
    p.mkdir(parents=True, exist_ok=True)
    return p


def logs_dir() -> Path:
    return _sub("logs")


def plugins_dir() -> Path:
    return _sub("plugins")


def default_export_dir() -> Path:
    docs = Path.home() / "Documents"
    base = docs if docs.exists() else Path.home()
    p = base / f"{APP_ID}-Exports"
    p.mkdir(parents=True, exist_ok=True)
    return p


def config_file() -> Path:
    return data_dir() / "config.json"


def sessions_file() -> Path:
    return data_dir() / "sessions.jsonl"


def activity_file() -> Path:
    return data_dir() / "activity.jsonl"


def cps_file() -> Path:
    return data_dir() / "cps_results.json"
