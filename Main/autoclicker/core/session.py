"""Persistent stores: sessions, app activity (login/logout tracking), CPS results."""
from __future__ import annotations

import json
import platform
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import paths
from .logger import get_logger


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds")


class JsonlStore:
    def __init__(self, path_fn):
        self._path_fn = path_fn
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path_fn()

    def append(self, row: dict) -> None:
        with self._lock:
            try:
                with open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            except OSError as exc:
                get_logger().error("store append failed: %s", exc)

    def load(self, limit: Optional[int] = None) -> list[dict]:
        rows: list[dict] = []
        with self._lock:
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rows.append(json.loads(line))
                        except ValueError:
                            continue          # skip corrupt line, keep the rest
            except FileNotFoundError:
                return []
            except OSError as exc:
                get_logger().error("store read failed: %s", exc)
                return []
        return rows[-limit:] if limit else rows

    def clear(self) -> None:
        with self._lock:
            try:
                self.path.write_text("", encoding="utf-8")
            except OSError as exc:
                get_logger().error("store clear failed: %s", exc)


class SessionStore(JsonlStore):
    def __init__(self):
        super().__init__(paths.sessions_file)


class ActivityLog(JsonlStore):
    """Application sign-in / sign-out tracking + click session start/stop events."""

    def __init__(self):
        super().__init__(paths.activity_file)
        self.app_started_at: Optional[float] = None

    def event(self, kind: str, **data) -> None:
        row = {"ts": iso(time.time()), "event": kind}
        row.update(data)
        self.append(row)

    def app_start(self, version: str) -> None:
        self.app_started_at = time.time()
        self.event("app_start", version=version, os=platform.platform(), python=platform.python_version())

    def app_exit(self) -> None:
        up = round(time.time() - self.app_started_at, 1) if self.app_started_at else None
        self.event("app_exit", uptime_s=up)


class CpsStore:
    """CPS test results + personal bests (JSON file)."""

    def __init__(self):
        self._lock = threading.Lock()

    def _read(self) -> dict:
        try:
            data = json.loads(paths.cps_file().read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("results", [])
                data.setdefault("bests", {})
                return data
        except (OSError, ValueError):
            pass
        return {"results": [], "bests": {}}

    def results(self) -> list[dict]:
        with self._lock:
            return list(self._read()["results"])

    def best(self, duration: int) -> Optional[dict]:
        with self._lock:
            return self._read()["bests"].get(str(duration))

    def add(self, result: dict) -> bool:
        """Store result; returns True when it is a new personal best for its duration."""
        with self._lock:
            data = self._read()
            data["results"].append(result)
            data["results"] = data["results"][-500:]
            key = str(result.get("duration"))
            prev = data["bests"].get(key)
            new_best = prev is None or result.get("total", 0) > prev.get("total", 0)
            if new_best:
                data["bests"][key] = result
            try:
                paths.cps_file().write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            except OSError as exc:
                get_logger().error("cps store failed: %s", exc)
            return new_best

    def clear(self) -> None:
        with self._lock:
            try:
                paths.cps_file().write_text(json.dumps({"results": [], "bests": {}}), encoding="utf-8")
            except OSError:
                pass
