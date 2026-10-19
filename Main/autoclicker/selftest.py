"""Headless self check. Exit code 0 = healthy. Used by CI against the BUILT executable."""
from __future__ import annotations

import os
import sys
import tempfile
import time
import traceback


def run_selftest(gui: bool = False) -> int:
    os.environ["AUTOCLICKER_4R022_HOME"] = tempfile.mkdtemp(prefix="4r022-selftest-")
    results: list[tuple[str, bool, str]] = []

    def check(name):
        def deco(fn):
            try:
                detail = fn() or ""
                results.append((name, True, str(detail)))
            except Exception as exc:  # noqa: BLE001
                results.append((name, False, f"{exc!r}\n{traceback.format_exc(limit=3)}"))
            return fn
        return deco

    from . import APP_NAME, VERSION_LABEL, __version__
    from .core import paths

    @check("resources (logo, icons, i18n)")
    def _():
        for n in ("logo.png", "emblem.png", "tray.png", "icon.ico"):
            assert paths.asset(n).exists(), f"missing asset {n}"
        for code in ("tr", "en", "ru"):
            assert (paths.resource_dir() / "i18n" / f"{code}.json").exists(), f"missing {code}.json"

    @check("i18n catalogs complete (TR/EN/RU)")
    def _():
        from .i18n import I18n
        i = I18n("en")
        base = i.keys("en")
        assert len(base) > 100, "catalog suspiciously small"
        for code in ("tr", "ru"):
            missing = base - i.keys(code)
            assert not missing, f"{code} missing: {sorted(missing)[:5]}"
        i.set_language("ru")
        assert i.t("btn.start") != "btn.start"
        return f"{len(base)} keys"

    @check("settings roundtrip")
    def _():
        from .core.config import AppSettings, load_settings, save_settings
        s = AppSettings().validate()
        s.click.millis = 37
        assert save_settings(s)
        assert load_settings().click.millis == 37

    @check("click engine (dummy backend)")
    def _():
        from .core.backend import DummyBackend
        from .core.config import ClickSettings
        from .core.engine import ClickEngine
        from .core.logger import TaskLog
        b = DummyBackend()
        e = ClickEngine(b, TaskLog())
        cfg = ClickSettings(millis=5, count_limit=30, failsafe_corner=False).validate()
        assert e.start(cfg)
        assert e.wait(10), "engine timeout"
        assert b.clicks == 30, f"expected 30 clicks, got {b.clicks}"
        assert e.last_session["stop_reason"] == "count_reached"
        return "30/30 clicks"

    @check("pause / resume / stop")
    def _():
        from .core.backend import DummyBackend
        from .core.config import ClickSettings
        from .core.engine import ClickEngine
        from .core.logger import TaskLog
        e = ClickEngine(DummyBackend(), TaskLog())
        e.start(ClickSettings(millis=5, failsafe_corner=False).validate())
        time.sleep(0.15)
        assert e.pause()
        n = e.snapshot()["total"]
        time.sleep(0.15)
        assert e.snapshot()["total"] == n
        assert e.resume()
        e.stop()
        assert e.wait(5)

    @check("CPS test logic")
    def _():
        from .core.cps_test import CPSTest
        t = [0.0]
        c = CPSTest(15, clock=lambda: t[0])
        for _ in range(30):
            c.click()
            t[0] += 0.1
        t[0] = c.t0 + 15.5
        c.tick()
        r = c.result()
        assert r["total"] == 30 and r["duration"] == 15

    @check("exporter TXT/JSON/CSV")
    def _():
        from .core import exporter
        d = tempfile.mkdtemp()
        rows = [{"a": 1, "b": "x"}]
        for f in exporter.FORMATS:
            assert exporter.export_rows(rows, f, d).exists()

    @check("hotkey matcher")
    def _():
        from .core.hotkeys import ComboMatcher
        m = ComboMatcher()
        m.set_bindings({"start": "f6"})
        assert m.press("f6") == ["start"]

    @check("plugins")
    def _():
        from .core.logger import TaskLog
        from .core.plugins import PluginManager
        pm = PluginManager(TaskLog())
        pm.install_examples()
        assert "session_notes" in pm.discover()

    @check("click backends available")
    def _():
        from .core.backend import available_backends
        av = available_backends()
        return ", ".join(av) if av else "none (GUI mode will fall back to a safe no-op backend)"

    if gui:
        @check("GUI: all pages build and render (offscreen)")
        def _():
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            from PySide6.QtWidgets import QApplication
            from .app import AppContext
            from .ui.main_window import MainWindow, NAV, apply_style
            app = QApplication.instance() or QApplication(sys.argv[:1])
            ctx = AppContext(headless_backend=True)
            apply_style(app, ctx.settings)
            win = MainWindow(ctx, app)
            win.show()
            for lang in ("tr", "en", "ru"):
                ctx.set_language(lang)
                for theme_name in ("dark", "light"):
                    win._set_theme(theme_name)
                    for key, _, _ in NAV:
                        win.open_page(key)
                        app.processEvents()
                        assert not win.grab().isNull()
            ctx.engine.start(ctx.settings.click)
            time.sleep(0.2)
            for _ in range(5):
                app.processEvents()
            ctx.engine.stop()
            ctx.engine.wait(3)
            win._really_quit = True
            win.mini.close()
            win.close()
            return "7 pages x 3 languages x 2 themes"

    lines = [f"\n  {APP_NAME} {VERSION_LABEL} ({__version__}) - self test", "  " + "-" * 60]
    failed = 0
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        first = detail.splitlines()[0] if detail else ""
        lines.append(f"  [{mark}] {name}" + (f"  -> {first}" if first else ""))
        if not ok:
            failed += 1
            lines.extend("         " + ln for ln in detail.splitlines()[1:])
    lines += ["  " + "-" * 60, f"  {len(results) - failed}/{len(results)} checks passed\n"]
    text = "\n".join(lines)
    print(text)
    report = os.environ.get("AUTOCLICKER_SELFTEST_REPORT")
    if report:                      # windowed builds have no console: write a report file too
        try:
            with open(report, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError:
            pass
    return 1 if failed else 0
