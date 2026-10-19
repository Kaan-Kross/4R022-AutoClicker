from __future__ import annotations

import sys

from PySide6.QtCore import QEvent, QObject, QTimer, Qt, Signal
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton,
                               QStackedWidget, QVBoxLayout, QWidget)

from .. import APP_NAME, VERSION_LABEL
from ..core import paths
from ..core.config import AppSettings, save_settings
from ..core.workers import S_IDLE
from . import theme
from .mini_panel import MiniPanel
from .pages.advanced import AdvancedPage
from .pages.cps import CpsPage
from .pages.home import HomePage
from .pages.logs import LogsPage
from .pages.plugins import PluginsPage
from .pages.settings import SettingsPage
from .pages.stats import StatsPage
from .tray import Tray
from .widgets import LogoBox, fmt_time

NAV = [("home", "nav.home", "⌂"), ("advanced", "nav.advanced", "⚙"), ("cps", "nav.cps", "⚡"),
       ("stats", "nav.stats", "▤"), ("logs", "nav.logs", "☰"), ("plugins", "nav.plugins", "✚"),
       ("settings", "nav.settings", "☼")]


class Bridge(QObject):
    """Thread-safe signal hub: worker / hotkey threads -> UI thread."""
    state = Signal(str, str)
    session = Signal(dict)
    hotkey = Signal(str)


def apply_style(app: QApplication, settings: AppSettings) -> None:
    f = app.font()
    f.setPointSizeF(10.0 * settings.font_scale / 100.0)
    app.setFont(f)
    app.setStyleSheet(theme.build_qss(settings.theme))


class MainWindow(QWidget):
    def __init__(self, ctx, app: QApplication):
        super().__init__()
        self.ctx, self.app = ctx, app
        self._really_quit = False
        self._capture_timer: QTimer | None = None
        self.setWindowTitle(f"{APP_NAME} — {VERSION_LABEL}")
        self.setWindowIcon(QIcon(str(paths.asset("emblem.png"))))
        self.resize(1100, 780); self.setMinimumSize(860, 600)

        self.bridge = Bridge()
        ctx.engine.subscribe(lambda ev, p: self.bridge.state.emit(p["state"], p.get("reason", "")) if ev == "state"
                             else self.bridge.session.emit(dict(p)))
        ctx.on_hotkey = self.bridge.hotkey.emit
        self.bridge.state.connect(self._on_state)
        self.bridge.session.connect(self._on_session)
        self.bridge.hotkey.connect(self._on_hotkey)

        # layout -------------------------------------------------------------------------------
        root = QHBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        side = QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(232)
        sl = QVBoxLayout(side); sl.setContentsMargins(14, 14, 14, 14); sl.setSpacing(6)
        sl.addWidget(LogoBox(196))
        sl.addSpacing(10)
        self.nav_btns: dict[str, QPushButton] = {}
        for key, tkey, icon in NAV:
            b = QPushButton(); b.setObjectName("Nav"); b.setCheckable(True); b.setAutoExclusive(True)
            b.setProperty("nav_icon", icon); b.setProperty("nav_key", tkey)
            b.clicked.connect(lambda _=False, k=key: self.open_page(k))
            self.nav_btns[key] = b; sl.addWidget(b)
        sl.addStretch(1)
        self.side_state = QLabel(); self.side_state.setObjectName("Badge"); self.side_state.setAlignment(Qt.AlignCenter)
        self.side_ver = QLabel(VERSION_LABEL); self.side_ver.setObjectName("Muted"); self.side_ver.setAlignment(Qt.AlignCenter)
        sl.addWidget(self.side_state); sl.addWidget(self.side_ver)
        root.addWidget(side)

        self.stack = QStackedWidget(); root.addWidget(self.stack, 1)
        self.pages = {
            "home": HomePage(ctx), "advanced": AdvancedPage(ctx), "cps": CpsPage(ctx), "stats": StatsPage(ctx),
            "logs": LogsPage(ctx), "plugins": PluginsPage(ctx), "settings": SettingsPage(ctx),
        }
        for k, _, _ in NAV:
            self.stack.addWidget(self.pages[k])
        self.current = "home"

        self.mini = MiniPanel(ctx)
        self.tray = Tray(ctx, self)

        # signals from pages ------------------------------------------------------------------------
        for p in (self.pages["home"], self.pages["advanced"], self.pages["settings"]):
            p.changed.connect(self._schedule_save)
        self.pages["home"].pick_requested.connect(self._begin_pick)
        self.pages["advanced"].pick_requested.connect(self._begin_pick)
        st = self.pages["settings"]
        st.language_changed.connect(self._set_language); st.theme_changed.connect(self._set_theme)
        st.font_changed.connect(self._set_font); st.behavior_changed.connect(self._apply_behavior)
        st.reset_requested.connect(self._reset_all)

        self._save_timer = QTimer(self); self._save_timer.setSingleShot(True); self._save_timer.setInterval(700)
        self._save_timer.timeout.connect(ctx.save)
        self._tick_timer = QTimer(self); self._tick_timer.setInterval(100); self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start()

        # keyboard: Ctrl+1..7 jump between pages (accessibility), Ctrl+Q quits
        for i, (k, _, _) in enumerate(NAV, 1):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, activated=lambda kk=k: self.open_page(kk))
        QShortcut(QKeySequence("Ctrl+Q"), self, activated=self.quit_app)

        ctx.i18n.subscribe(self.retranslate)
        self.apply_theme_to_pages()
        self.retranslate()
        self.open_page("home")
        self._apply_behavior()

    # ---- navigation -------------------------------------------------------------------------------------
    def open_page(self, key: str):
        self.current = key
        self.stack.setCurrentWidget(self.pages[key])
        for k, b in self.nav_btns.items():
            b.setChecked(k == key)
        self.pages[key].on_show()
        if not self.isVisible() or self.isMinimized():
            self.show_normal()

    def show_normal(self):
        self.showNormal(); self.raise_(); self.activateWindow()
        self.ctx.set_background(False)

    def toggle_visibility(self):
        if self.isVisible() and not self.isMinimized():
            self.hide_to_background()
        else:
            self.show_normal()

    def hide_to_background(self):
        self.hide()
        self.ctx.set_background(True)

    # ---- engine / hotkeys ----------------------------------------------------------------------------------
    def _on_state(self, state: str, reason: str):
        for p in self.pages.values():
            p.set_state(state)
        self.tray.set_state(state)
        self.side_state.setText("● " + self.ctx.t("state." + state))

    def _on_session(self, rec: dict):
        self.pages["stats"].refresh()

    def _on_hotkey(self, action: str):
        if action == "add_target":
            self.add_target_now()
        elif action in ("start", "pause"):
            self.ctx.handle_ui_action(action)
        # "stop"/"kill" were already executed on the listener thread

    # ---- position capture (fixed point / targets) ---------------------------------------------------------------
    def _begin_pick(self, purpose: str):
        """3-second countdown, then read the cursor position from the active click backend."""
        if self._capture_timer:
            return
        self._pick_left = 3; self._pick_purpose = purpose
        self._capture_timer = QTimer(self); self._capture_timer.setInterval(1000)
        self._capture_timer.timeout.connect(self._pick_step)
        self.side_state.setText(self.ctx.t("pick.countdown", n=3))
        self._capture_timer.start()

    def _pick_step(self):
        self._pick_left -= 1
        if self._pick_left > 0:
            self.side_state.setText(self.ctx.t("pick.countdown", n=self._pick_left)); return
        self._capture_timer.stop(); self._capture_timer.deleteLater(); self._capture_timer = None
        pos = self.ctx.backend.position()
        self._on_state(self.ctx.engine.state, "")
        if pos:
            self._apply_pick(self._pick_purpose, pos)

    def add_target_now(self):
        pos = self.ctx.backend.position()
        if pos:
            self._apply_pick("target", pos)

    def _apply_pick(self, purpose: str, pos):
        c = self.ctx.settings.click
        if purpose == "fixed":
            c.fixed_x, c.fixed_y = pos
        else:
            c.targets.append({"x": pos[0], "y": pos[1], "label": ""})
        self.ctx.tasklog.info("target.added", x=pos[0], y=pos[1])
        for k in ("home", "advanced"):
            self.pages[k].load()
        self._schedule_save()

    # ---- settings handlers -------------------------------------------------------------------------------------------
    def _schedule_save(self):
        self._save_timer.start()

    def _set_language(self, code: str):
        self.ctx.set_language(code)            # triggers retranslate() via i18n listener

    def _set_theme(self, name: str):
        self.ctx.settings.theme = name
        apply_style(self.app, self.ctx.settings)
        self.apply_theme_to_pages(); self.ctx.save()

    def _set_font(self, pct: int):
        self.ctx.settings.font_scale = pct
        apply_style(self.app, self.ctx.settings); self.ctx.save()

    def apply_theme_to_pages(self):
        for p in self.pages.values():
            p.apply_theme(self.ctx.settings.theme)

    def _apply_behavior(self):
        s = self.ctx.settings
        flags = self.windowFlags()
        want_top = bool(s.always_on_top)
        if bool(flags & Qt.WindowStaysOnTopHint) != want_top:
            vis = self.isVisible()
            self.setWindowFlag(Qt.WindowStaysOnTopHint, want_top)
            if vis:
                self.show()
        self.mini.setVisible(bool(s.show_mini_panel))
        self.ctx.apply_hotkeys()

    def _reset_all(self):
        r = QMessageBox.question(self, APP_NAME, self.ctx.t("set.reset_confirm"))
        if r != QMessageBox.Yes:
            return
        lang = self.ctx.settings.language
        fresh = AppSettings().validate(); fresh.language = lang
        self.ctx.settings = fresh
        self.ctx.apply_hotkeys(); self.ctx.save()
        apply_style(self.app, fresh); self.apply_theme_to_pages()
        for p in self.pages.values():
            p.load()
        self._apply_behavior()

    # ---- i18n / ticks ------------------------------------------------------------------------------------------------------
    def retranslate(self):
        t = self.ctx.t
        for key, tkey, icon in NAV:
            self.nav_btns[key].setText(f"  {icon}   {t(tkey)}")
            self.nav_btns[key].setAccessibleName(t(tkey))
        for p in self.pages.values():
            p.retranslate()
        self.tray.retranslate()
        self.side_state.setText("● " + t("state." + self.ctx.engine.state))
        self.setWindowTitle(f"{APP_NAME} — {VERSION_LABEL}")

    def _tick(self):
        snap = self.ctx.engine.snapshot()
        page = self.pages[self.current]
        page.tick(snap)
        if self.current != "home":
            self.pages["home"].tick(snap)       # keeps Home tiles fresh for when we return
        if self.mini.isVisible():
            self.mini.update_snapshot(snap)

    # ---- window lifecycle -------------------------------------------------------------------------------------------------------
    def closeEvent(self, e):
        s = self.ctx.settings
        if not self._really_quit and s.run_in_background and self.tray.available:
            e.ignore(); self.hide_to_background(); return
        if not self._really_quit and s.confirm_exit:
            if QMessageBox.question(self, APP_NAME, self.ctx.t("exit.confirm")) != QMessageBox.Yes:
                e.ignore(); return
        self._finalize(); e.accept()

    def changeEvent(self, e):
        super().changeEvent(e)
        if e.type() == QEvent.WindowStateChange:
            self.ctx.set_background(self.isMinimized())

    def quit_app(self):
        self._really_quit = True
        self.close()
        self.app.quit()

    def _finalize(self):
        self.mini.close(); self.tray.hide()
        self.ctx.shutdown()
