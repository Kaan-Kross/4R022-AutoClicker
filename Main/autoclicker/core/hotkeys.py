"""Global hotkeys. Any key (with optional Ctrl/Shift/Alt/Cmd) can be bound to any action.

`ComboMatcher` is pure Python (unit-tested); `HotkeyManager` feeds it from a pynput listener.
Note: global key capture needs X11/XWayland on Linux and Accessibility permission on macOS.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from .logger import get_logger

MODIFIERS = ("ctrl", "shift", "alt", "cmd")
_MOD_ALIASES = {
    "ctrl_l": "ctrl", "ctrl_r": "ctrl", "ctrl": "ctrl",
    "shift_l": "shift", "shift_r": "shift", "shift": "shift",
    "alt_l": "alt", "alt_r": "alt", "alt_gr": "alt", "alt": "alt",
    "cmd_l": "cmd", "cmd_r": "cmd", "cmd": "cmd",
}
PROTECTED_ACTIONS = {"start", "pause", "toggle", "add_target"}   # need a double-press when protected
ACTIONS = ("start", "stop", "pause", "add_target", "kill")


def parse_combo(text: str) -> tuple[frozenset, str]:
    parts = [p.strip().lower() for p in (text or "").split("+") if p.strip()]
    if not parts:
        return frozenset(), ""
    key = parts[-1]
    mods = frozenset(_MOD_ALIASES.get(p, p) for p in parts[:-1] if _MOD_ALIASES.get(p, p) in MODIFIERS)
    return mods, key


def combo_to_text(mods, key: str) -> str:
    order = [m for m in MODIFIERS if m in mods]
    return "+".join(order + [key])


def pretty_combo(text: str) -> str:
    mods, key = parse_combo(text)
    if not key:
        return "—"
    names = {"ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "cmd": "Cmd"}
    k = key.upper() if (len(key) == 1 or (key.startswith("f") and key[1:].isdigit())) else key.replace("_", " ").title()
    return "+".join([names[m] for m in MODIFIERS if m in mods] + [k])


def key_name(key) -> Optional[str]:
    """Normalize a pynput key object (duck-typed) to a lowercase name."""
    name = getattr(key, "name", None)
    if name:
        return _MOD_ALIASES.get(name, name)
    ch = getattr(key, "char", None)
    if ch and ch.isprintable():
        return ch.lower()
    vk = getattr(key, "vk", None)
    if vk is not None:
        return f"vk{vk}"
    return None


class ComboMatcher:
    REPEAT_RESET = 1.5   # seconds: protects against a missed key-release event

    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self.bindings: dict[str, tuple[frozenset, str]] = {}
        self._held: dict[str, float] = {}

    def set_bindings(self, mapping: dict[str, str]) -> None:
        self.bindings = {a: parse_combo(c) for a, c in mapping.items() if parse_combo(c)[1]}

    def press(self, name: str) -> list[str]:
        now = self._clock()
        last = self._held.get(name)
        if last is not None and now - last < self.REPEAT_RESET:
            self._held[name] = now        # auto-repeat of a held key: ignore
            return []
        self._held[name] = now
        if name in MODIFIERS:
            return []
        mods = frozenset(h for h in self._held if h in MODIFIERS)
        return [a for a, (m, k) in self.bindings.items() if k == name and m == mods]

    def release(self, name: str) -> None:
        self._held.pop(name, None)

    def current_mods(self) -> frozenset:
        return frozenset(h for h in self._held if h in MODIFIERS)

    def clear(self) -> None:
        self._held.clear()


class HotkeyManager:
    DOUBLE_PRESS_WINDOW = 0.6

    def __init__(self, callback: Callable[[str], None], clock=time.monotonic):
        self._callback = callback
        self._clock = clock
        self.matcher = ComboMatcher(clock)
        self.protection = False
        self._last_trigger: dict[str, float] = {}
        self._listener = None
        self._capture_cb: Optional[Callable[[str], None]] = None
        self._lock = threading.Lock()
        self.error: Optional[str] = None

    # ---- configuration ----------------------------------------------------------
    def set_bindings(self, mapping: dict[str, str]) -> None:
        self.matcher.set_bindings(mapping)

    def set_protection(self, on: bool) -> None:
        self.protection = bool(on)

    # ---- lifecycle ----------------------------------------------------------------
    def start(self) -> bool:
        if self._listener is not None:
            return True
        try:
            from pynput import keyboard
            self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            self._listener.daemon = True
            self._listener.start()
            self.error = None
            return True
        except Exception as exc:
            self.error = repr(exc)
            get_logger().error("hotkey listener unavailable: %s", exc)
            self._listener = None
            return False

    def stop(self) -> None:
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def is_running(self) -> bool:
        return self._listener is not None

    # ---- capture mode (UI "press a key") ---------------------------------------------
    def capture(self, cb: Optional[Callable[[str], None]]) -> None:
        with self._lock:
            self._capture_cb = cb

    # ---- events -----------------------------------------------------------------------
    def _canon(self, key):
        try:
            return self._listener.canonical(key) if self._listener else key
        except Exception:
            return key

    def _on_press(self, key) -> None:
        name = key_name(self._canon(key)) or key_name(key)
        if not name:
            return
        self.handle_press(name)

    def _on_release(self, key) -> None:
        name = key_name(self._canon(key)) or key_name(key)
        if name:
            self.matcher.release(name)

    def handle_press(self, name: str) -> list[str]:
        with self._lock:
            cap = self._capture_cb
        if cap is not None and name not in MODIFIERS:
            first = self.matcher.press(name)  # keep held-state bookkeeping consistent
            del first
            combo = combo_to_text(self.matcher.current_mods(), name)
            with self._lock:
                self._capture_cb = None
            try:
                cap(combo)
            except Exception:
                get_logger().exception("capture callback failed")
            return []
        actions = self.matcher.press(name)
        fired = []
        now = self._clock()
        for a in actions:
            if self.protection and a in PROTECTED_ACTIONS:
                last = self._last_trigger.get(a, -10.0)
                self._last_trigger[a] = now
                if now - last > self.DOUBLE_PRESS_WINDOW:
                    continue                    # first press only arms the action
                self._last_trigger[a] = -10.0
            fired.append(a)
            try:
                self._callback(a)
            except Exception:
                get_logger().exception("hotkey callback failed")
        return fired
