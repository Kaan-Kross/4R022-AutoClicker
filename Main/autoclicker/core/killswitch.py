"""KillSwitch: emergency stop + watchdog + auto shutdown."""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from .engine import ClickEngine
from .logger import TaskLog, get_logger


class KillSwitch:
    """Triggers: hotkey / UI button / corner failsafe (worker) / auto shutdown / watchdog.

    The watchdog also detects a click thread stuck inside a backend call (stale heartbeat)
    and force-releases every mouse button so the user never ends up with a stuck button.
    """

    STALE_AFTER = 15.0

    def __init__(self, engine: ClickEngine, tasklog: TaskLog,
                 exit_callback: Optional[Callable[[], None]] = None):
        self.engine = engine
        self.tasklog = tasklog
        self.exit_callback = exit_callback
        self.exit_app_on_kill = False
        self.auto_shutdown_s = 0
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._run_started: Optional[float] = None
        self._stale_reported = False

    def configure(self, exit_app_on_kill: bool, auto_shutdown_minutes: int) -> None:
        self.exit_app_on_kill = bool(exit_app_on_kill)
        self.auto_shutdown_s = int(auto_shutdown_minutes) * 60

    def trigger(self, reason: str = "killswitch") -> None:
        self.tasklog.warn("killswitch.triggered", reason=reason)
        self.engine.stop("killswitch" if reason == "killswitch" else reason)
        try:
            self.engine.backend.release_all()
        except Exception:
            get_logger().exception("release_all failed")
        if self.exit_app_on_kill and self.exit_callback:
            self.exit_callback()

    def arm(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._watch, name="4R022-Watchdog", daemon=True)
        self._thread.start()

    def disarm(self) -> None:
        self._stop.set()

    def _watch(self) -> None:
        while not self._stop.wait(0.5):
            w = self.engine.worker
            if not w or not w.is_alive() or w.t_start is None:
                self._run_started = None
                self._stale_reported = False
                continue
            if self._run_started is None:
                self._run_started = time.monotonic()
            if self.auto_shutdown_s and time.monotonic() - self._run_started >= self.auto_shutdown_s:
                self.trigger("auto_shutdown")
                self._run_started = None
                continue
            if time.monotonic() - w.heartbeat > self.STALE_AFTER and not self._stale_reported:
                self._stale_reported = True
                self.tasklog.error("killswitch.stale")
                try:
                    self.engine.backend.release_all()
                except Exception:
                    pass
                w.request_stop("error")
