import json
import tempfile
import unittest
from pathlib import Path

from . import __name__ as _pkg  # noqa: F401
from autoclicker.core import config, exporter
from autoclicker.core.cps_test import CPSTest, rank_index
from autoclicker.core.hotkeys import (ComboMatcher, HotkeyManager, parse_combo, pretty_combo, key_name)
from autoclicker.core.plugins import PluginManager
from autoclicker.core.logger import TaskLog


class FakeClock:
    def __init__(self): self.t = 100.0
    def __call__(self): return self.t
    def advance(self, s): self.t += s


class ConfigTests(unittest.TestCase):
    def test_roundtrip_and_clamp(self):
        s = config.AppSettings()
        s.click.hours = 500
        s.click.random_min_ms, s.click.random_max_ms = 300, 100
        s.click.targets = [{"x": "5", "y": 6}, {"bad": 1}]
        s.validate()
        self.assertEqual(s.click.hours, 99)
        self.assertLessEqual(s.click.random_min_ms, s.click.random_max_ms)
        self.assertEqual(s.click.targets, [{"x": 5, "y": 6, "label": ""}])
        p = Path(tempfile.mkdtemp()) / "c.json"
        self.assertTrue(config.save_settings(s, p))
        s2 = config.load_settings(p)
        self.assertEqual(s2.to_dict(), s.to_dict())

    def test_corrupt_file_falls_back(self):
        p = Path(tempfile.mkdtemp()) / "c.json"
        p.write_text("{not json", encoding="utf-8")
        s = config.load_settings(p)
        self.assertEqual(s.language, "tr")
        self.assertTrue(p.with_suffix(".json.bak").exists())

    def test_unknown_keys_ignored_and_interval(self):
        s = config.AppSettings.from_dict({"language": "xx", "theme": "neon", "zzz": 1,
                                          "click": {"seconds": 1, "millis": 500, "evil": True}})
        self.assertEqual((s.language, s.theme), ("tr", "dark"))
        self.assertAlmostEqual(s.click.interval_s(), 1.5)


class HotkeyTests(unittest.TestCase):
    def test_parse_and_pretty(self):
        self.assertEqual(parse_combo("Ctrl+Shift+F12"), (frozenset({"ctrl", "shift"}), "f12"))
        self.assertEqual(pretty_combo("ctrl+shift+f12"), "Ctrl+Shift+F12")
        self.assertEqual(pretty_combo("a"), "A")
        self.assertEqual(pretty_combo(""), "—")

    def test_key_name(self):
        class K:  # duck-typed pynput keys
            def __init__(self, **kw): self.__dict__.update(kw)
        self.assertEqual(key_name(K(name="ctrl_l")), "ctrl")
        self.assertEqual(key_name(K(name="f6")), "f6")
        self.assertEqual(key_name(K(char="A")), "a")

    def test_matcher_modifiers_and_repeat(self):
        clk = FakeClock()
        m = ComboMatcher(clk)
        m.set_bindings({"start": "f6", "kill": "ctrl+shift+f12", "x": "x"})
        self.assertEqual(m.press("f6"), ["start"])
        clk.advance(0.03)
        self.assertEqual(m.press("f6"), [])           # auto-repeat ignored
        m.release("f6")
        self.assertEqual(m.press("f6"), ["start"])
        m.release("f6")
        m.press("ctrl"); m.press("shift")
        self.assertEqual(m.press("f12"), ["kill"])
        m.release("f12"); m.release("ctrl"); m.release("shift")
        self.assertEqual(m.press("f12"), [])           # no binding for bare f12
        m.release("f12")
        m.press("ctrl")
        self.assertEqual(m.press("x"), [])             # ctrl+x != x

    def test_stuck_key_recovers(self):
        clk = FakeClock()
        m = ComboMatcher(clk)
        m.set_bindings({"start": "f6"})
        self.assertEqual(m.press("f6"), ["start"])
        clk.advance(3.0)                               # release event was lost
        self.assertEqual(m.press("f6"), ["start"])

    def test_protection_double_press_and_critical_actions(self):
        clk = FakeClock()
        fired = []
        hk = HotkeyManager(fired.append, clock=clk)
        hk.set_bindings({"start": "f6", "stop": "f7"})
        hk.set_protection(True)
        hk.handle_press("f6"); hk.matcher.release("f6")
        self.assertEqual(fired, [])                    # armed only
        clk.advance(0.3)
        hk.handle_press("f6"); hk.matcher.release("f6")
        self.assertEqual(fired, ["start"])
        hk.handle_press("f7"); hk.matcher.release("f7")
        self.assertEqual(fired, ["start", "stop"])     # stop is never protected
        clk.advance(2)
        hk.handle_press("f6"); hk.matcher.release("f6")
        clk.advance(1.0)
        hk.handle_press("f6")
        self.assertEqual(fired, ["start"] + ["stop"])  # too slow -> not fired

    def test_capture(self):
        got = []
        hk = HotkeyManager(lambda a: None)
        hk.capture(got.append)
        hk.handle_press("ctrl")
        self.assertEqual(got, [])                      # modifier alone does not finish capture
        hk.handle_press("q")
        self.assertEqual(got, ["ctrl+q"])


class CpsTests(unittest.TestCase):
    def test_flow_and_stats(self):
        clk = FakeClock()
        t = CPSTest(15, clock=clk)
        for i in range(150):                           # steady 10 CPS for 15 s
            t.click(); clk.advance(0.1)
        clk.t = t.t0 + 15.0001
        self.assertTrue(t.tick())
        self.assertFalse(t.click())
        r = t.result()
        self.assertEqual(r["total"], 150)
        self.assertAlmostEqual(r["avg_cps"], 10.0, places=2)
        self.assertGreaterEqual(r["peak_cps"], 10)
        self.assertGreater(r["consistency"], 95)
        self.assertEqual(sum(r["per_second"]), 150)
        self.assertEqual(len(r["per_second"]), 15)
        self.assertEqual(r["rank"], rank_index(10.0))

    def test_first_click_starts_clock(self):
        clk = FakeClock()
        t = CPSTest(15, clock=clk)
        clk.advance(50)
        self.assertEqual(t.state, "idle")
        t.click()
        self.assertEqual(t.state, "running")
        self.assertAlmostEqual(t.remaining(), 15.0, places=3)

    def test_empty_result(self):
        r = CPSTest(30).result()
        self.assertEqual((r["total"], r["avg_cps"], r["peak_cps"]), (0, 0.0, 0.0))


class ExportTests(unittest.TestCase):
    rows = [{"id": 1, "total_clicks": 10, "stop_reason": "user"},
            {"id": 2, "total_clicks": 20, "stop_reason": "failsafe", "extra": [1, 2]}]

    def test_all_formats(self):
        d = tempfile.mkdtemp()
        j = exporter.export_rows(self.rows, "json", d)
        self.assertEqual(json.loads(j.read_text(encoding="utf-8"))["count"], 2)
        c = exporter.export_rows(self.rows, "csv", d)
        text = c.read_text(encoding="utf-8-sig").splitlines()
        self.assertEqual(text[0].split(",")[:2], ["id", "total_clicks"])
        self.assertEqual(len(text), 3)
        t = exporter.export_rows(self.rows, "txt", d, "stats")
        self.assertIn("total_clicks", t.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            exporter.export_rows(self.rows, "xml", d)


class PluginTests(unittest.TestCase):
    def test_example_plugins_load_and_dispatch(self):
        tl = TaskLog()
        pm = PluginManager(tl)
        pm.install_examples()
        found = pm.discover()
        self.assertIn("session_notes", found)
        self.assertEqual(found["session_notes"]["name"], "Session Notes")
        self.assertEqual(pm.loaded, set())             # nothing runs until enabled
        pm.sync(["session_notes"])
        self.assertIn("session_notes", pm.loaded)
        pm.dispatch("session", {"started_at": "x", "total_clicks": 1, "avg_cps": 2, "stop_reason": "user"})
        pm.sync([])
        self.assertEqual(pm.loaded, set())

    def test_broken_plugin_is_contained(self):
        from autoclicker.core import paths
        (paths.plugins_dir() / "broken_one.py").write_text("def register(api):\n    raise RuntimeError('x')\n")
        tl = TaskLog()
        pm = PluginManager(tl)
        pm.discover()
        self.assertFalse(pm.load("broken_one"))
        self.assertTrue(any(i["code"] == "plugin.error" for i in tl.items()))


if __name__ == "__main__":
    unittest.main()
