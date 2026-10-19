#!/usr/bin/env python3
"""Generates the README screenshots automatically (offscreen Qt, demo data, no display needed).

    python Build/screenshots.py            -> docs/screenshots/*.png
"""
from __future__ import annotations

import os
import random
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["AUTOCLICKER_4R022_HOME"] = tempfile.mkdtemp(prefix="4r022-shots-")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Main"))

from PySide6.QtWidgets import QApplication  # noqa: E402

from autoclicker.app import AppContext  # noqa: E402
from autoclicker.core.cps_test import CPSTest  # noqa: E402
from autoclicker.ui.main_window import MainWindow, apply_style  # noqa: E402

OUT = ROOT / "docs" / "screenshots"
PAGES = ["home", "advanced", "cps", "stats", "logs", "plugins", "settings"]


def seed(ctx: AppContext) -> None:
    rnd = random.Random(4022)
    for i in range(7):
        n = rnd.randint(400, 9000)
        dur = rnd.uniform(20, 600)
        ctx.sessions.append({
            "started_at": f"2026-10-1{i}T1{i}:2{i}:00", "ended_at": "", "duration_s": round(dur, 1),
            "total_clicks": n, "avg_cps": round(n / dur, 2), "peak_cps": round(n / dur * 1.2),
            "button": "left", "mode": rnd.choice(["single", "double", "burst"]),
            "stop_reason": rnd.choice(["user", "count_reached", "failsafe"])})
    ctx.activity.app_start("1.0.0b1")
    for d, avg in ((15, 8.6), (30, 7.9), (60, 7.1)):
        t = [0.0]
        c = CPSTest(d, clock=lambda: t[0])
        for _ in range(int(avg * d)):
            c.click()
            t[0] += (1 / avg) * rnd.uniform(0.7, 1.3)
            if t[0] >= c.t0 + d:
                break
        t[0] = c.t0 + d + 0.01
        c.tick()
        ctx.cps_store.add(c.result())
    for code, kw in (("app.start", {"version": "1.0V Beta"}), ("backend.selected", {"backend": "pynput"}),
                     ("engine.start", {"button": "left", "mode": "single", "interval": 100, "position": "current"}),
                     ("engine.stop", {"total": 1234, "elapsed": 123.4, "avg": 10.0})):
        ctx.tasklog.info(code, **kw)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv[:1])
    ctx = AppContext(headless_backend=True)
    ctx.settings.language = "en"
    ctx.i18n.set_language("en")
    seed(ctx)
    ctx.settings.click.targets = [{"x": 320, "y": 240, "label": "Accept"}, {"x": 840, "y": 512, "label": "Next"},
                                  {"x": 1280, "y": 700, "label": "Confirm"}]
    apply_style(app, ctx.settings)
    win = MainWindow(ctx, app)
    win.resize(1180, 900)
    win.show()
    for theme_name in ("dark", "light"):
        win._set_theme(theme_name)
        for page in PAGES:
            if theme_name == "light" and page not in ("home", "cps", "settings"):
                continue
            win.open_page(page)
            if page == "cps":
                cp = win.pages["cps"]
                cp.last_result = ctx.cps_store.results()[-1]
                cp._render_result(cp.last_result, True)
                cp.chart.set_values(cp.last_result["per_second"])
            for _ in range(3):
                app.processEvents()
            win.grab().save(str(OUT / f"{page}-{theme_name}.png"))
            print("saved", f"{page}-{theme_name}.png")
    win._really_quit = True
    win.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
