"""ClickEngine: owns the worker lifecycle, builds session records, notifies listeners."""
from __future__ import annotations

import copy
import platform
import threading
import time
from typing import Callable, Optional

from .. import __version__
from .backend import ClickBackend
from .config import ClickSettings
from .logger import TaskLog, get_logger
from .session import SessionStore, ActivityLog, iso
from .workers import ClickWorker, S_IDLE, S_DELAY, S_RUNNING, S_PAUSED

Listener = Callable[[str, dict], None]


class ClickEngine:
    """Events sent to listeners:  ("state", {"state", "reason"})  and  ("session", record)."""

    def __init__(self, backend: ClickBackend, tasklog: TaskLog,
                 sessions: Optional[SessionStore] = None, activity: Optional[ActivityLog] = None):
        self.backend = backend
        self.tasklog = tasklog
        self.sessions = sessions
        self.activity = activity
        self._worker: Optional[ClickWorker] = None
        self._lock = threading.RLock()
        self._listeners: list[Listener] = []
        self.last_snapshot: dict = self._empty_snapshot()
        self.last_session: Optional[dict] = None
        self._done = threading.Event()
        self._done.set()

    # ---- listeners -------------------------------------------------------------
    def subscribe(self, cb: Listener) -> None:
        self._listeners.append(cb)

    def _emit(self, event: str, payload: dict) -> None:
        for cb in list(self._listeners):
            try:
                cb(event, payload)
            except Exception:
                get_logger().exception("engine listener failed")

    # ---- state -----------------------------------------------------------------
    @property
    def worker(self) -> Optional[ClickWorker]:
        return self._worker

    @property
    def state(self) -> str:
        w = self._worker
        return w.state if w and w.is_alive() else S_IDLE

    def is_active(self) -> bool:
        return self.state != S_IDLE

    @staticmethod
    def _empty_snapshot() -> dict:
        return {"state": S_IDLE, "total": 0, "elapsed": 0.0, "avg_cps": 0.0, "instant_cps": 0.0,
                "peak_cps": 0.0, "errors": 0, "loops_done": 0, "target_index": -1}

    def snapshot(self) -> dict:
        w = self._worker
        if not w:
            return dict(self.last_snapshot)
        elapsed = w.elapsed()
        total = w.stats.total
        snap = {
            "state": self.state,
            "total": total,
            "elapsed": elapsed,
            "avg_cps": (total / elapsed) if elapsed > 0 else 0.0,
            "instant_cps": w.stats.instant_cps if w.state == S_RUNNING else 0.0,
            "peak_cps": w.stats.peak_cps,
            "errors": w.stats.errors,
            "loops_done": w.stats.loops_done,
            "target_index": w.stats.target_index,
        }
        if not w.is_alive():
            self.last_snapshot = dict(snap, instant_cps=0.0)
        return snap

    # ---- control ----------------------------------------------------------------
    def start(self, cfg: ClickSettings) -> bool:
        with self._lock:
            if self.is_active():
                return False
            cfg = ClickSettings.from_dict(copy.deepcopy(cfg.to_dict()))
            worker = ClickWorker(cfg, self.backend, self.tasklog, self._on_worker_state, self._on_worker_done)
            self._worker = worker
            self._done.clear()
            self.tasklog.info("engine.start", button=cfg.button, mode=cfg.mode,
                              interval=round(cfg.interval_ms(), 1), position=cfg.position_mode)
            if self.activity:
                self.activity.event("session_start", button=cfg.button, mode=cfg.mode,
                                    interval_ms=round(cfg.interval_ms(), 1))
            worker.start()
            return True

    def stop(self, reason: str = "user") -> bool:
        w = self._worker
        if not w or not w.is_alive():
            return False
        w.request_stop(reason)
        return True

    def pause(self) -> bool:
        w = self._worker
        ok = bool(w and w.pause())
        if ok:
            self.tasklog.info("engine.pause")
        return ok

    def resume(self) -> bool:
        w = self._worker
        ok = bool(w and w.resume())
        if ok:
            self.tasklog.info("engine.resume")
        return ok

    def toggle_pause(self) -> bool:
        return self.resume() if self.state == S_PAUSED else self.pause()

    def toggle(self, cfg: ClickSettings) -> None:
        if self.is_active():
            self.stop("user")
        else:
            self.start(cfg)

    def wait(self, timeout: Optional[float] = None) -> bool:
        return self._done.wait(timeout)

    # ---- worker callbacks (run on the worker thread) --------------------------------
    def _on_worker_state(self, state: str) -> None:
        w = self._worker
        reason = w.stop_reason if (w and state == S_IDLE) else ""
        self._emit("state", {"state": state, "reason": reason})

    def _on_worker_done(self, w: ClickWorker) -> None:
        elapsed = w.elapsed()
        total = w.stats.total
        self.last_snapshot = {
            "state": S_IDLE, "total": total, "elapsed": elapsed,
            "avg_cps": (total / elapsed) if elapsed > 0 else 0.0, "instant_cps": 0.0,
            "peak_cps": w.stats.peak_cps, "errors": w.stats.errors,
            "loops_done": w.stats.loops_done, "target_index": w.stats.target_index,
        }
        record = None
        if w.t_start is not None:
            c = w.cfg
            record = {
                "id": int((w.started_wall or time.time()) * 1000),
                "started_at": iso(w.started_wall or time.time()),
                "ended_at": iso(w.ended_wall or time.time()),
                "duration_s": round(elapsed, 3),
                "total_clicks": total,
                "avg_cps": round(self.last_snapshot["avg_cps"], 3),
                "peak_cps": round(w.stats.peak_cps, 1),
                "button": c.button, "mode": c.mode,
                "interval_ms": round(c.interval_ms(), 1),
                "random": c.random_enabled, "position_mode": c.position_mode,
                "targets": len(c.targets) if c.position_mode == "multi" else 0,
                "loops_done": w.stats.loops_done,
                "stop_reason": w.stop_reason, "errors": w.stats.errors,
                "platform": platform.system(),
            }
            self.last_session = record
            if self.sessions:
                self.sessions.append(record)
        code = "engine.stop" if w.stop_reason in ("user", "finished") else f"engine.stop_{w.stop_reason}"
        level = "warn" if w.stop_reason in ("failsafe", "killswitch", "error", "auto_shutdown") else "info"
        self.tasklog.add(level, code, total=total, elapsed=round(elapsed, 2),
                         avg=round(self.last_snapshot["avg_cps"], 2))
        if self.activity:
            self.activity.event("session_end", total=total, duration_s=round(elapsed, 2),
                                reason=w.stop_reason)
        self._done.set()
        if record:
            self._emit("session", record)
