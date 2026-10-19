"""Logging: rotating error log + in-memory task log (professional task tracking)."""
from __future__ import annotations

import collections
import logging
import logging.handlers
import threading
import time
from typing import Callable

from . import paths

_LOGGER_NAME = "4r022"
_configured = False


def get_logger() -> logging.Logger:
    global _configured
    log = logging.getLogger(_LOGGER_NAME)
    if not _configured:
        _configured = True
        log.setLevel(logging.DEBUG)
        try:
            fh = logging.handlers.RotatingFileHandler(
                paths.logs_dir() / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
            fh.setLevel(logging.INFO)
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
            log.addHandler(fh)
            eh = logging.handlers.RotatingFileHandler(
                paths.logs_dir() / "error.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
            eh.setLevel(logging.ERROR)
            eh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
            log.addHandler(eh)
        except OSError:
            log.addHandler(logging.NullHandler())
    return log


def read_error_log(max_chars: int = 60_000) -> str:
    f = paths.logs_dir() / "error.log"
    try:
        text = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[-max_chars:]


class TaskLog:
    """Ring buffer of structured task events. Messages are stored as (code, params)
    so the UI can render them in the *current* language, even after a live switch."""

    LEVELS = ("info", "warn", "error")

    def __init__(self, maxlen: int = 3000):
        self._items: collections.deque[dict] = collections.deque(maxlen=maxlen)
        self._lock = threading.Lock()
        self._listeners: list[Callable[[dict], None]] = []

    def add(self, level: str, code: str, **params) -> dict:
        item = {"ts": time.time(), "level": level if level in self.LEVELS else "info",
                "code": code, "params": params}
        with self._lock:
            self._items.append(item)
        lg = get_logger()
        text = f"{code} {params}" if params else code
        if item["level"] == "error":
            lg.error(text)
        elif item["level"] == "warn":
            lg.warning(text)
        else:
            lg.info(text)
        for cb in list(self._listeners):
            try:
                cb(item)
            except Exception:  # listener errors must never break the engine
                lg.exception("tasklog listener failed")
        return item

    def info(self, code: str, **p):
        return self.add("info", code, **p)

    def warn(self, code: str, **p):
        return self.add("warn", code, **p)

    def error(self, code: str, **p):
        return self.add("error", code, **p)

    def items(self) -> list[dict]:
        with self._lock:
            return list(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def subscribe(self, cb: Callable[[dict], None]) -> None:
        self._listeners.append(cb)
