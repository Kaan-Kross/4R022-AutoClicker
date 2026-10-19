import threading
import time
import unittest

from . import __name__ as _pkg  # noqa: F401  (forces env setup)
from autoclicker.core.backend import DummyBackend
from autoclicker.core.config import ClickSettings
from autoclicker.core.engine import ClickEngine
from autoclicker.core.logger import TaskLog
from autoclicker.core.workers import build_pass
import random


def make(**kw):
    base = dict(hours=0, minutes=0, seconds=0, millis=5, failsafe_corner=False)
    base.update(kw)
    return ClickSettings(**base).validate()


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.backend = DummyBackend()
        self.engine = ClickEngine(self.backend, TaskLog())

    def run_cfg(self, cfg, timeout=5.0):
        self.assertTrue(self.engine.start(cfg))
        self.assertTrue(self.engine.wait(timeout), "engine did not finish in time")
        return self.engine.last_session

    def test_count_limit_exact(self):
        rec = self.run_cfg(make(count_limit=25))
        self.assertEqual(rec["total_clicks"], 25)
        self.assertEqual(self.backend.clicks, 25)
        self.assertEqual(rec["stop_reason"], "count_reached")

    def test_double_click_counts_two_and_respects_limit(self):
        rec = self.run_cfg(make(mode="double", count_limit=7))
        self.assertEqual(rec["total_clicks"], 7)

    def test_burst(self):
        rec = self.run_cfg(make(mode="burst", burst_clicks=4, burst_gap_ms=1, count_limit=12))
        self.assertEqual(rec["total_clicks"], 12)

    def test_loops_without_targets(self):
        rec = self.run_cfg(make(loops=9))
        self.assertEqual(rec["total_clicks"], 9)
        self.assertEqual(rec["stop_reason"], "loops_done")

    def test_multi_targets_sequential_order_and_loops(self):
        t = [{"x": 1, "y": 1}, {"x": 2, "y": 2}, {"x": 3, "y": 3}]
        rec = self.run_cfg(make(position_mode="multi", targets=t, loops=2))
        self.assertEqual(rec["total_clicks"], 6)
        moves = [e[1:] for e in self.backend.events if e[0] == "move"]
        self.assertEqual(moves, [(1, 1), (2, 2), (3, 3)] * 2)

    def test_pingpong_pass(self):
        self.assertEqual(build_pass(4, "pingpong", random.Random(1)), [0, 1, 2, 3, 2, 1])
        self.assertEqual(sorted(build_pass(5, "random", random.Random(1))), [0, 1, 2, 3, 4])

    def test_fixed_position(self):
        rec = self.run_cfg(make(position_mode="fixed", fixed_x=40, fixed_y=60, count_limit=3))
        self.assertEqual(rec["total_clicks"], 3)
        self.assertTrue(all(e[1:] == (40, 60) for e in self.backend.events if e[0] == "move"))

    def test_hold_uses_press_release(self):
        self.run_cfg(make(hold_ms=2, count_limit=3, button="right"))
        kinds = [e[0] for e in self.backend.events if e[0] in ("press", "release")]
        # the trailing releases come from the safety release_all() at shutdown
        self.assertEqual(kinds[:6], ["press", "release"] * 3)
        self.assertTrue(all(k == "release" for k in kinds[6:]))

    def test_stop_and_stuck_button_release(self):
        self.engine.start(make(millis=20, hold_ms=500))
        time.sleep(0.15)
        self.assertTrue(self.engine.stop("user"))
        self.assertTrue(self.engine.wait(3))
        self.assertEqual(self.engine.last_session["stop_reason"], "user")
        self.assertEqual(self.backend.events[-1][0], "release")

    def test_pause_resume_freezes_count(self):
        self.engine.start(make(millis=5))
        time.sleep(0.1)
        self.assertTrue(self.engine.pause())
        time.sleep(0.05)
        a = self.engine.snapshot()["total"]
        time.sleep(0.15)
        b = self.engine.snapshot()["total"]
        self.assertEqual(a, b)
        self.assertEqual(self.engine.state, "paused")
        self.assertTrue(self.engine.resume())
        time.sleep(0.1)
        self.assertGreater(self.engine.snapshot()["total"], b)
        self.engine.stop()
        self.engine.wait(3)

    def test_start_delay_then_stop_during_delay(self):
        self.engine.start(make(start_delay_s=5.0))
        time.sleep(0.1)
        self.assertEqual(self.engine.state, "delay")
        self.engine.stop()
        self.assertTrue(self.engine.wait(2))
        self.assertEqual(self.backend.clicks, 0)

    def test_random_interval_bounds(self):
        cfg = make(random_enabled=True, random_min_ms=10, random_max_ms=20, count_limit=15)
        t0 = time.perf_counter()
        self.run_cfg(cfg)
        dt = time.perf_counter() - t0
        self.assertGreaterEqual(dt, 14 * 0.010 * 0.9)
        self.assertLess(dt, 14 * 0.020 + 1.0)

    def test_failsafe_corner(self):
        self.backend.set_position(0, 0)
        rec = self.run_cfg(make(failsafe_corner=True))
        self.assertEqual(rec["stop_reason"], "failsafe") if rec else None

    def test_max_runtime(self):
        rec = self.run_cfg(make(max_runtime_s=1, millis=10))
        self.assertEqual(rec["stop_reason"], "max_runtime")
        self.assertGreater(rec["total_clicks"], 20)

    def test_interval_accuracy(self):
        rec = self.run_cfg(make(millis=10, count_limit=60))
        self.assertAlmostEqual(rec["avg_cps"], 100, delta=12)

    def test_second_start_rejected_while_active(self):
        self.assertTrue(self.engine.start(make(millis=50)))
        self.assertFalse(self.engine.start(make()))
        self.engine.stop()
        self.engine.wait(3)

    def test_events_emitted(self):
        seen = []
        self.engine.subscribe(lambda ev, p: seen.append((ev, p.get("state"))))
        self.run_cfg(make(count_limit=2))
        names = [s for _, s in seen if s]
        self.assertIn("running", names)
        self.assertEqual(names[-1], "idle")
        self.assertIn("session", [e for e, _ in seen])

    def test_backend_errors_stop_engine(self):
        class Broken(DummyBackend):
            def click(self, b):
                raise RuntimeError("boom")
        eng = ClickEngine(Broken(), TaskLog())
        eng.start(make())
        self.assertTrue(eng.wait(3))
        self.assertEqual(eng.last_session["stop_reason"], "error")
        self.assertGreaterEqual(eng.last_session["errors"], 5)


if __name__ == "__main__":
    unittest.main()
