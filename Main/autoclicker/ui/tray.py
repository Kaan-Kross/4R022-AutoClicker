"""System tray icon with context menu (Home / CPS / Settings / Start-Stop / Kill / Quit)."""
from __future__ import annotations

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from ..core import paths


class Tray:
    def __init__(self, ctx, window):
        self.ctx = ctx
        self.window = window
        self.available = QSystemTrayIcon.isSystemTrayAvailable()
        self.icon = QSystemTrayIcon(QIcon(str(paths.asset("tray.png"))), window)
        self.menu = QMenu()
        self.a_show = QAction(self.menu); self.a_home = QAction(self.menu); self.a_cps = QAction(self.menu)
        self.a_settings = QAction(self.menu); self.a_toggle = QAction(self.menu); self.a_kill = QAction(self.menu)
        self.a_quit = QAction(self.menu)
        for a in (self.a_show, None, self.a_home, self.a_cps, self.a_settings, None, self.a_toggle, self.a_kill, None, self.a_quit):
            if a is None:
                self.menu.addSeparator()
            else:
                self.menu.addAction(a)
        self.a_show.triggered.connect(window.toggle_visibility)
        self.a_home.triggered.connect(lambda: window.open_page("home"))
        self.a_cps.triggered.connect(lambda: window.open_page("cps"))
        self.a_settings.triggered.connect(lambda: window.open_page("settings"))
        self.a_toggle.triggered.connect(lambda: ctx.engine.toggle(ctx.settings.click))
        self.a_kill.triggered.connect(lambda: ctx.killswitch.trigger("killswitch"))
        self.a_quit.triggered.connect(window.quit_app)
        self.icon.setContextMenu(self.menu)
        self.icon.activated.connect(self._activated)
        self.retranslate()
        if self.available:
            self.icon.show()

    def _activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.window.toggle_visibility()

    def retranslate(self):
        t = self.ctx.t
        self.a_show.setText(t("tray.show")); self.a_home.setText(t("nav.home")); self.a_cps.setText(t("nav.cps"))
        self.a_settings.setText(t("nav.settings")); self.a_kill.setText(t("btn.kill")); self.a_quit.setText(t("tray.quit"))
        self.set_state(self.ctx.engine.state)

    def set_state(self, state: str):
        t = self.ctx.t
        self.a_toggle.setText(t("btn.stop") if state != "idle" else t("btn.start"))
        self.icon.setToolTip(f"4R022 AutoClicker — {t('state.' + state)}")

    def hide(self):
        self.icon.hide()
