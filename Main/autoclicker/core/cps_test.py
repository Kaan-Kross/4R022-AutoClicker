"""CPS (clicks-per-second) test logic. Pure Python, GUI-independent and unit-tested."""
from __future__ import annotations

import math
import time
from typing import Optional

DURATIONS = (15, 30, 60)
RANK_THRESHOLDS = (3.0, 5.0, 7.0, 9.0, 11.0, 14.0, 18.0)   # -> rank index 0..7


def rank_index(avg_cps: float) -> int:
    for i, th in enumerate(RANK_THRESHOLDS):
        if avg_cps < th:
            return i
    return len(RANK_THRESHOLDS)


class CPSTest:
    IDLE, RUNNING, FINISHED = "idle", "running", "finished"

    def __init__(self, duration: int = 15, clock=time.perf_counter):
        self.duration = int(duration)
        self._clock = clock
        self.state = self.IDLE
        self.t0: Optional[float] = None
        self.stamps: list[float] = []      # seconds since test start

    def reset(self, duration: Optional[int] = None) -> None:
        if duration:
            self.duration = int(duration)
        self.state = self.IDLE
        self.t0 = None
        self.stamps = []

    def elapsed(self) -> float:
        if self.t0 is None:
            return 0.0
        return min(self.duration, self._clock() - self.t0)

    def remaining(self) -> float:
        return max(0.0, self.duration - self.elapsed())

    def click(self) -> bool:
        """Register a click. The first click starts the test. Returns True if counted."""
        now = self._clock()
        if self.state == self.FINISHED:
            return False
        if self.state == self.IDLE:
            self.state = self.RUNNING
            self.t0 = now
        t = now - self.t0
        if t > self.duration:
            self.tick()
            return False
        self.stamps.append(t)
        return True

    def tick(self) -> bool:
        """Call periodically; finishes the test when time is up. Returns True if just finished."""
        if self.state == self.RUNNING and self._clock() - self.t0 >= self.duration:
            self.state = self.FINISHED
            return True
        return False

    def live_cps(self, window: float = 1.0) -> float:
        if self.state != self.RUNNING:
            return 0.0
        now = self.elapsed()
        lo = now - window
        n = sum(1 for s in self.stamps if s >= lo)
        return (n / now) if 0 < now < window else float(n)

    def per_second(self) -> list[int]:
        buckets = [0] * self.duration
        for s in self.stamps:
            i = min(self.duration - 1, int(s))
            buckets[i] += 1
        return buckets

    def result(self) -> dict:
        d = self.duration
        n = len(self.stamps)
        avg = n / d if d else 0.0
        # peak: best 1-second sliding window
        peak, j = 0, 0
        for i, s in enumerate(self.stamps):
            while self.stamps[j] < s - 1.0:
                j += 1
            peak = max(peak, i - j + 1)
        gaps = [b - a for a, b in zip(self.stamps, self.stamps[1:])]
        if gaps:
            mean = sum(gaps) / len(gaps)
            var = sum((g - mean) ** 2 for g in gaps) / len(gaps)
            std = math.sqrt(var)
            consistency = max(0.0, 100.0 * (1.0 - min(1.0, std / mean))) if mean > 0 else 0.0
            fastest, slowest = min(gaps) * 1000, max(gaps) * 1000
            avg_gap = mean * 1000
        else:
            consistency = fastest = slowest = avg_gap = 0.0
        half = d / 2.0
        first = sum(1 for s in self.stamps if s < half) / half if half else 0.0
        second = sum(1 for s in self.stamps if s >= half) / half if half else 0.0
        score = round(avg * 100 * (0.7 + 0.3 * consistency / 100.0))
        return {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration": d, "total": n,
            "avg_cps": round(avg, 3), "peak_cps": float(peak),
            "avg_interval_ms": round(avg_gap, 2),
            "fastest_gap_ms": round(fastest, 2), "slowest_gap_ms": round(slowest, 2),
            "consistency": round(consistency, 1),
            "first_half_cps": round(first, 2), "second_half_cps": round(second, 2),
            "per_second": self.per_second(),
            "score": score, "rank": rank_index(avg),
        }
