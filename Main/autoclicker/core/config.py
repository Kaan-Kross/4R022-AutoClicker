"""Settings model (JSON persisted, atomic writes, corruption-safe)."""
from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field, fields, asdict
from pathlib import Path
from typing import Any

from . import paths
from .logger import get_logger

BUTTONS = ("left", "right", "middle")
MODES = ("single", "double", "burst")
POSITION_MODES = ("current", "fixed", "multi")
SEQUENCE_ORDERS = ("sequential", "random", "pingpong")
LANGUAGES = ("tr", "en", "ru")
THEMES = ("dark", "light")

DEFAULT_HOTKEYS = {
    "start": "f6",
    "stop": "f7",
    "pause": "f8",
    "add_target": "f9",
    "kill": "ctrl+shift+f12",
}


def _clamp(v, lo, hi):
    try:
        v = type(lo)(v)
    except (TypeError, ValueError):
        return lo
    return max(lo, min(hi, v))


@dataclass
class ClickSettings:
    button: str = "left"
    mode: str = "single"
    burst_clicks: int = 5
    burst_gap_ms: int = 20
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    millis: int = 100
    random_enabled: bool = False
    random_min_ms: int = 80
    random_max_ms: int = 150
    count_limit: int = 0            # 0 = unlimited (total clicks)
    loops: int = 0                  # 0 = unlimited (passes over the target list / actions)
    start_delay_s: float = 0.0
    hold_ms: int = 0
    position_mode: str = "current"
    fixed_x: int = 0
    fixed_y: int = 0
    targets: list = field(default_factory=list)   # [{"x":int,"y":int,"label":str}]
    sequence_order: str = "sequential"
    jitter_px: int = 0
    max_runtime_s: int = 0          # 0 = unlimited
    failsafe_corner: bool = True

    def interval_s(self) -> float:
        return self.hours * 3600 + self.minutes * 60 + self.seconds + self.millis / 1000.0

    def interval_ms(self) -> float:
        return self.interval_s() * 1000.0

    def validate(self) -> "ClickSettings":
        self.button = self.button if self.button in BUTTONS else "left"
        self.mode = self.mode if self.mode in MODES else "single"
        self.position_mode = self.position_mode if self.position_mode in POSITION_MODES else "current"
        self.sequence_order = self.sequence_order if self.sequence_order in SEQUENCE_ORDERS else "sequential"
        self.burst_clicks = _clamp(self.burst_clicks, 1, 1000)
        self.burst_gap_ms = _clamp(self.burst_gap_ms, 0, 10_000)
        self.hours = _clamp(self.hours, 0, 99)
        self.minutes = _clamp(self.minutes, 0, 59)
        self.seconds = _clamp(self.seconds, 0, 59)
        self.millis = _clamp(self.millis, 0, 999)
        self.random_min_ms = _clamp(self.random_min_ms, 0, 3_600_000)
        self.random_max_ms = _clamp(self.random_max_ms, 0, 3_600_000)
        if self.random_max_ms < self.random_min_ms:
            self.random_min_ms, self.random_max_ms = self.random_max_ms, self.random_min_ms
        self.count_limit = _clamp(self.count_limit, 0, 10**9)
        self.loops = _clamp(self.loops, 0, 10**9)
        self.start_delay_s = _clamp(self.start_delay_s, 0.0, 3600.0)
        self.hold_ms = _clamp(self.hold_ms, 0, 60_000)
        self.jitter_px = _clamp(self.jitter_px, 0, 500)
        self.max_runtime_s = _clamp(self.max_runtime_s, 0, 10**7)
        self.fixed_x = _clamp(self.fixed_x, -100_000, 100_000)
        self.fixed_y = _clamp(self.fixed_y, -100_000, 100_000)
        clean = []
        for t in self.targets or []:
            try:
                clean.append({"x": int(t["x"]), "y": int(t["y"]), "label": str(t.get("label", ""))})
            except (KeyError, TypeError, ValueError):
                continue
        self.targets = clean
        return self

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict | None) -> "ClickSettings":
        d = d or {}
        known = {f.name for f in fields(cls)}
        obj = cls(**{k: v for k, v in d.items() if k in known})
        return obj.validate()


@dataclass
class AppSettings:
    language: str = "tr"
    theme: str = "dark"
    font_scale: int = 100
    backend: str = "auto"
    export_dir: str = ""
    run_in_background: bool = True       # close button -> tray instead of quit
    start_minimized: bool = False
    always_on_top: bool = False
    show_mini_panel: bool = False
    key_protection: bool = True          # double-press hotkeys while app is in background
    kill_exit_app: bool = False
    auto_shutdown_minutes: int = 0       # 0 = off
    confirm_exit: bool = False
    hotkeys: dict = field(default_factory=lambda: dict(DEFAULT_HOTKEYS))
    plugins_enabled: list = field(default_factory=list)
    click: ClickSettings = field(default_factory=ClickSettings)

    def validate(self) -> "AppSettings":
        self.language = self.language if self.language in LANGUAGES else "tr"
        self.theme = self.theme if self.theme in THEMES else "dark"
        self.font_scale = _clamp(self.font_scale, 80, 160)
        self.auto_shutdown_minutes = _clamp(self.auto_shutdown_minutes, 0, 100_000)
        hk = dict(DEFAULT_HOTKEYS)
        if isinstance(self.hotkeys, dict):
            for k in DEFAULT_HOTKEYS:
                if isinstance(self.hotkeys.get(k), str):
                    hk[k] = self.hotkeys[k]
        self.hotkeys = hk
        if not self.export_dir:
            self.export_dir = str(paths.default_export_dir())
        if not isinstance(self.plugins_enabled, list):
            self.plugins_enabled = []
        self.click.validate()
        return self

    def to_dict(self) -> dict:
        d = asdict(self)
        d["click"] = self.click.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict | None) -> "AppSettings":
        d = dict(d or {})
        click = ClickSettings.from_dict(d.pop("click", None))
        known = {f.name for f in fields(cls)}
        obj = cls(**{k: v for k, v in d.items() if k in known and k != "click"})
        obj.click = click
        return obj.validate()

    def copy(self) -> "AppSettings":
        return AppSettings.from_dict(copy.deepcopy(self.to_dict()))


def load_settings(path: Path | None = None) -> AppSettings:
    path = path or paths.config_file()
    if not path.exists():
        return AppSettings().validate()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("config root is not an object")
        return AppSettings.from_dict(data)
    except (OSError, ValueError) as exc:
        get_logger().error("config unreadable (%s) - using defaults, backup kept", exc)
        try:
            shutil.copy2(path, path.with_suffix(".json.bak"))
        except OSError:
            pass
        return AppSettings().validate()


def save_settings(settings: AppSettings, path: Path | None = None) -> bool:
    path = path or paths.config_file()
    tmp = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(settings.to_dict(), indent=2, ensure_ascii=False)   # serialize first: never half-write
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".cfg-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
        os.replace(tmp, path)
        return True
    except (OSError, TypeError, ValueError) as exc:
        get_logger().error("config save failed: %s", exc)
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        return False
