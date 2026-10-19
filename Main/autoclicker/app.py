"""AppContext: wires every core component together (no GUI imports)."""
from __future__ import annotations

import platform
import sys
import threading
from typing import Callable, Optional

from . import APP_NAME, VERSION_LABEL, __version__
from .core import paths
from .core.backend import BackendError, ClickBackend, DummyBackend, available_backends, select_backend
from .core.config import AppSettings, load_settings, save_settings
from .core.cps_test import CPSTest
from .core.engine import ClickEngine
from .core.hotkeys import HotkeyManager
from .core.killswitch import KillSwitch
from .core.logger import TaskLog, get_logger
from .core.plugins import PluginManager
from .core.session import ActivityLog, CpsStore, SessionStore
from .core.workers import TaskPool, S_DELAY, S_IDLE, S_PAUSED, S_RUNNING
from .i18n import I18n


class AppContext:
    def __init__(self, headless_backend: bool = False):
        self.log = get_logger()
        self.tasklog = TaskLog()
        self.settings: AppSettings = load_settings()
        self.i18n = I18n(self.settings.language)
        self.pool = TaskPool()
        self.sessions = SessionStore()
        self.activity = ActivityLog()
        self.cps_store = CpsStore()
        self.backend_error: Optional[str] = None
        self.backend: ClickBackend = self._make_backend(headless_backend)
        self.engine = ClickEngine(self.backend, self.tasklog, self.sessions, self.activity)
        self.killswitch = KillSwitch(self.engine, self.tasklog)
        self.hotkeys = HotkeyManager(self._on_hotkey_raw)
        self.plugins = PluginManager(self.tasklog)
        self.in_background = False            # set by the main window (tray / minimized)
        self.on_hotkey: Optional[Callable[[str], None]] = None   # UI hook (thread-safe via Qt signal)
        self._prev_state = S_IDLE
        self.engine.subscribe(self._on_engine_event)

    # ---- setup ----------------------------------------------------------------------
    def _make_backend(self, headless: bool) -> ClickBackend:
        if headless:
            return DummyBackend()
        try:
            b = select_backend(self.settings.backend)
            self.tasklog.info("backend.selected", backend=b.name)
            return b
        except BackendError as exc:
            self.backend_error = str(exc)
            self.tasklog.error("backend.missing", error=str(exc))
            return DummyBackend()

    def startup(self) -> None:
        self.activity.app_start(__version__)
        self.tasklog.info("app.start", version=VERSION_LABEL)
        self.killswitch.configure(self.settings.kill_exit_app, self.settings.auto_shutdown_minutes)
        self.killswitch.arm()
        self.apply_hotkeys()
        self.hotkeys.start()
        self.plugins.install_examples()
        self.plugins.sync(self.settings.plugins_enabled)

    def shutdown(self) -> None:
        self.engine.stop("app_exit")
        self.engine.wait(2.0)
        self.hotkeys.stop()
        self.killswitch.disarm()
        self.activity.app_exit()
        self.tasklog.info("app.exit")
        self.save()
        self.pool.shutdown()

    # ---- settings -------------------------------------------------------------------------
    def save(self) -> None:
        save_settings(self.settings)

    def apply_hotkeys(self) -> None:
        self.hotkeys.set_bindings(self.settings.hotkeys)
        self.hotkeys.set_protection(self.settings.key_protection and self.in_background)

    def set_background(self, value: bool) -> None:
        self.in_background = value
        self.hotkeys.set_protection(self.settings.key_protection and value)

    def switch_backend(self, name: str) -> bool:
        """Swap the click backend (only while idle)."""
        if self.engine.is_active():
            return False
        self.settings.backend = name
        try:
            b = select_backend(name)
        except BackendError as exc:
            self.backend_error = str(exc)
            self.tasklog.error("backend.missing", error=str(exc))
            return False
        self.backend = b
        self.engine.backend = b
        self.backend_error = None
        self.tasklog.info("backend.selected", backend=b.name)
        return True

    def set_language(self, code: str) -> None:
        self.settings.language = code
        self.i18n.set_language(code)
        self.save()

    def t(self, key: str, /, **kw) -> str:
        return self.i18n.t(key, **kw)

    # ---- hotkeys / engine bridge ----------------------------------------------------------
    def _on_hotkey_raw(self, action: str) -> None:
        # Safety-critical actions are handled right here, on the listener thread, so the
        # emergency stop works even if the UI thread is busy.
        if action == "kill":
            self.killswitch.trigger("killswitch")
        elif action == "stop":
            self.engine.stop("user")
        if self.on_hotkey:
            self.on_hotkey(action)

    def handle_ui_action(self, action: str) -> None:
        """Runs on the UI thread for non-critical actions (start / pause / add_target)."""
        if action == "start":
            if not self.engine.is_active():
                self.engine.start(self.settings.click)
        elif action == "pause":
            self.engine.toggle_pause()

    def _on_engine_event(self, event: str, payload: dict) -> None:
        if event == "state":
            state, prev = payload["state"], self._prev_state
            self._prev_state = state
            if state in (S_RUNNING,) and prev == S_PAUSED:
                self.plugins.dispatch("resume", {})
            elif state == S_RUNNING:
                self.plugins.dispatch("start", {})
            elif state == S_PAUSED:
                self.plugins.dispatch("pause", {})
            elif state == S_IDLE and prev != S_IDLE:
                self.plugins.dispatch("stop", {"reason": payload.get("reason", "")})
        elif event == "session":
            self.plugins.dispatch("session", dict(payload))

    # ---- diagnostics -----------------------------------------------------------------------
    def diagnostics(self) -> str:
        from .core.exporter import FORMATS  # noqa: F401  (import sanity)
        lines = [
            f"{APP_NAME} {VERSION_LABEL} ({__version__})",
            f"OS: {platform.platform()}",
            f"Python: {platform.python_version()} ({'frozen' if paths.is_frozen() else 'source'})",
            f"Backend: {self.backend.name}  (available: {', '.join(available_backends()) or 'none'})",
            f"Backend error: {self.backend_error or '-'}",
            f"Hotkey listener: {'running' if self.hotkeys.is_running() else 'NOT running'}"
            + (f"  [{self.hotkeys.error}]" if self.hotkeys.error else ""),
            f"Language/Theme: {self.settings.language}/{self.settings.theme}",
            f"Data dir: {paths.data_dir()}",
            f"Export dir: {self.settings.export_dir}",
            f"Plugins loaded: {', '.join(sorted(self.plugins.loaded)) or '-'}",
        ]
        if sys.platform == "darwin":
            lines.append("macOS: grant Accessibility + Input Monitoring to this app (System Settings > Privacy & Security).")
        elif sys.platform.startswith("linux"):
            import os
            sess = os.environ.get("XDG_SESSION_TYPE", "?")
            lines.append(f"Linux session: {sess}" + ("  (Wayland: global hotkeys/clicks may be limited; use an X11 session)" if sess == "wayland" else ""))
        return "\n".join(lines)
