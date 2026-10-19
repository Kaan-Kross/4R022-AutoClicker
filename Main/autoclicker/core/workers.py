"""Worker system.

* ClickWorker  - dedicated high-precision click thread (one per run).
* TaskPool     - small general-purpose pool for non-realtime jobs (export, plugin load,
                 file IO) so the UI thread and the click thread never block on them.
"""
from __future__ import annotations

import collections
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Optional

from .backend import ClickBackend
from .config import ClickSettings
from .logger import TaskLog, get_logger

S_IDLE, S_DELAY, S_RUNNING, S_PAUSED = "idle", "delay", "running", "paused"


class Stats:
    __slots__ = ("total", "errors", "instant_cps", "peak_cps", "loops_done", "target_index")

    def __init__(self):
        self.total = 0
        self.errors = 0
        self.instant_cps = 0.0
        self.peak_cps = 0.0
        self.loops_done = 0
        self.target_index = -1


def build_pass(n: int, order: str, rng: random.Random) -> list[int]:
    """Indices visited in ONE pass (= one loop) over `n` targets."""
    if n <= 0:
        return [0]
    idx = list(range(n))
    if order == "random":
        rng.shuffle(idx)
    elif order == "pingpong" and n > 2:
        idx = idx + list(range(n - 2, 0, -1))
    return idx


class ClickWorker(threading.Thread):
    MAX_CONSECUTIVE_ERRORS = 5

    def __init__(self, cfg: ClickSettings, backend: ClickBackend, tasklog: TaskLog,
                 on_state: Callable[[str], None], on_finished: Callable[["ClickWorker"], None]):
        super().__init__(name="4R022-ClickWorker", daemon=True)
        self.cfg = cfg
        self.backend = backend
        self.tasklog = tasklog
        self._on_state = on_state
        self._on_finished = on_finished
        self.stop_event = threading.Event()
        self.gate = threading.Event()
        self.gate.set()
        self.state = S_IDLE
        self.stats = Stats()
        self.stop_reason = "finished"
        self.heartbeat = time.monotonic()
        self.t_start: Optional[float] = None       # perf_counter at first click
        self.t_end: Optional[float] = None
        self.started_wall: Optional[float] = None
        self.ended_wall: Optional[float] = None
        self._paused_total = 0.0
        self._pause_started: Optional[float] = None
        self._window: collections.deque = collections.deque()
        self._last_inst = 0.0
        self._rng = random.Random()
        self._consec_err = 0

    # ---- control (called from other threads) ----------------------------------
    def request_stop(self, reason: str = "user") -> None:
        if not self.stop_event.is_set():
            self.stop_reason = reason
        self.stop_event.set()
        self.gate.set()

    def pause(self) -> bool:
        if self.state != S_RUNNING:
            return False
        self._pause_started = time.perf_counter()
        self.gate.clear()
        self._set_state(S_PAUSED)
        return True

    def resume(self) -> bool:
        if self.state != S_PAUSED:
            return False
        if self._pause_started is not None:
            self._paused_total += time.perf_counter() - self._pause_started
            self._pause_started = None
        self._set_state(S_RUNNING)
        self.gate.set()
        return True

    def elapsed(self) -> float:
        if self.t_start is None:
            return 0.0
        end = self.t_end if self.t_end is not None else time.perf_counter()
        paused = self._paused_total
        if self._pause_started is not None and self.t_end is None:
            paused += end - self._pause_started
        return max(0.0, end - self.t_start - paused)

    # ---- internals -------------------------------------------------------------
    def _set_state(self, state: str) -> None:
        self.state = state
        try:
            self._on_state(state)
        except Exception:
            get_logger().exception("state callback failed")

    def _beat(self) -> None:
        self.heartbeat = time.monotonic()

    def _sleep_until(self, t: float) -> None:
        """Stop-aware, drift-free sleep: coarse wait then a short spin for precision."""
        while True:
            if self.stop_event.is_set():
                return
            remaining = t - time.perf_counter()
            if remaining <= 0:
                return
            self._beat()
            if remaining > 0.004:
                self.stop_event.wait(min(remaining - 0.002, 1.0))
            # else: spin the last ~2-4 ms for sub-millisecond accuracy

    def _wait_if_paused(self) -> None:
        while not self.gate.is_set() and not self.stop_event.is_set():
            self._beat()
            self.gate.wait(1.0)

    def _next_interval(self) -> float:
        c = self.cfg
        if c.random_enabled:
            return self._rng.uniform(c.random_min_ms, c.random_max_ms) / 1000.0
        return c.interval_s()

    def _register_click(self) -> None:
        s = self.stats
        s.total += 1
        now = time.perf_counter()
        w = self._window
        w.append(now)
        if now - self._last_inst >= 0.1:
            self._last_inst = now
            while w and now - w[0] > 1.0:
                w.popleft()
            s.instant_cps = float(len(w))
            if s.instant_cps > s.peak_cps:
                s.peak_cps = s.instant_cps
        self._beat()

    def _limit_reached(self) -> bool:
        c = self.cfg
        return bool(c.count_limit and self.stats.total >= c.count_limit)

    def _click_once(self, button: str, hold_s: float) -> bool:
        try:
            if hold_s > 0:
                self.backend.press(button)
                try:
                    self.stop_event.wait(hold_s)
                finally:
                    self.backend.release(button)
            else:
                self.backend.click(button)
            self._consec_err = 0
            self._register_click()
            return True
        except Exception as exc:
            self.stats.errors += 1
            self._consec_err += 1
            self.tasklog.error("engine.click_error", error=repr(exc))
            if self._consec_err >= self.MAX_CONSECUTIVE_ERRORS:
                self.request_stop("error")
            return False

    def _do_action(self) -> None:
        c = self.cfg
        hold = c.hold_ms / 1000.0
        if c.mode == "double":
            n, gap = 2, 0.03
        elif c.mode == "burst":
            n, gap = c.burst_clicks, c.burst_gap_ms / 1000.0
        else:
            n, gap = 1, 0.0
        for i in range(n):
            if i and self.stop_event.is_set():
                break
            self._click_once(c.button, hold)
            if self._limit_reached() or self.stop_event.is_set():
                break
            if i < n - 1 and gap > 0:
                self._sleep_until(time.perf_counter() + gap)

    def _move_to(self, x: int, y: int) -> None:
        j = self.cfg.jitter_px
        if j:
            x += self._rng.randint(-j, j)
            y += self._rng.randint(-j, j)
        try:
            self.backend.move(int(x), int(y))
        except Exception as exc:
            self.stats.errors += 1
            self.tasklog.error("engine.move_error", error=repr(exc))

    # ---- thread body -------------------------------------------------------------
    def run(self) -> None:
        try:
            self._run()
        except Exception as exc:
            self.stats.errors += 1
            self.stop_reason = "error"
            self.tasklog.error("engine.crash", error=repr(exc))
            get_logger().exception("click worker crashed")
        finally:
            try:
                self.backend.release_all()
            except Exception:
                pass
            self.t_end = time.perf_counter() if self.t_start is not None else None
            self.ended_wall = time.time()
            self._set_state(S_IDLE)
            try:
                self._on_finished(self)
            except Exception:
                get_logger().exception("finish callback failed")

    def _run(self) -> None:
        c = self.cfg
        if c.start_delay_s > 0:
            self._set_state(S_DELAY)
            end = time.perf_counter() + c.start_delay_s
            while not self.stop_event.is_set() and time.perf_counter() < end:
                self._beat()
                self.stop_event.wait(min(0.05, max(0.0, end - time.perf_counter())))
            if self.stop_event.is_set():
                return

        targets = [(t["x"], t["y"]) for t in c.targets]
        mode = c.position_mode
        if mode == "multi" and not targets:
            self.tasklog.warn("engine.no_targets")
            mode = "current"
        pass_idx: list[int] = []
        pass_pos = 0

        self._set_state(S_RUNNING)
        self.t_start = time.perf_counter()
        self.started_wall = time.time()
        next_t = self.t_start
        last_fs = 0.0

        while not self.stop_event.is_set():
            if not self.gate.is_set():
                self._wait_if_paused()
                if self.stop_event.is_set():
                    break
                next_t = time.perf_counter()

            now = time.perf_counter()
            if c.max_runtime_s and self.elapsed() >= c.max_runtime_s:
                self.request_stop("max_runtime")
                break

            if c.failsafe_corner and now - last_fs >= 0.05:
                last_fs = now
                try:
                    pos = self.backend.position()
                except Exception:
                    pos = None
                if pos and pos[0] <= 0 and pos[1] <= 0:
                    self.request_stop("failsafe")
                    break

            # choose target
            if mode == "fixed":
                self._move_to(c.fixed_x, c.fixed_y)
            elif mode == "multi":
                if pass_pos >= len(pass_idx):
                    pass_idx = build_pass(len(targets), c.sequence_order, self._rng)
                    pass_pos = 0
                ti = pass_idx[pass_pos]
                pass_pos += 1
                self.stats.target_index = ti
                self._move_to(*targets[ti])

            self._do_action()
            if self.stop_event.is_set():
                break
            if self._limit_reached():
                self.request_stop("count_reached")
                break

            # loop accounting: one loop = one pass over targets (multi) or one action
            if mode == "multi":
                if pass_pos >= len(pass_idx):
                    self.stats.loops_done += 1
                    if c.loops and self.stats.loops_done >= c.loops:
                        self.request_stop("loops_done")
                        break
            else:
                self.stats.loops_done += 1
                if c.loops and self.stats.loops_done >= c.loops:
                    self.request_stop("loops_done")
                    break

            next_t += self._next_interval()
            now = time.perf_counter()
            if next_t < now:
                next_t = now          # never "catch up" with a burst after a stall
            self._sleep_until(next_t)


class TaskPool:
    """General-purpose background pool (exports, plugin loading, disk IO)."""

    def __init__(self, workers: int = 3):
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="4R022-Task")

    def submit(self, fn: Callable, *args, on_done: Optional[Callable[[object, Optional[BaseException]], None]] = None,
               **kwargs) -> Future:
        fut = self._pool.submit(fn, *args, **kwargs)
        if on_done:
            def _cb(f: Future):
                try:
                    on_done(f.result(), None)
                except BaseException as exc:  # noqa: BLE001
                    on_done(None, exc)
            fut.add_done_callback(_cb)
        return fut

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)
