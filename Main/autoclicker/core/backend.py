"""Click backends with automatic fallback chain.

Order (auto): Win32 (Windows only, fastest) -> pynput -> pyautogui.
All backends expose the same tiny interface so the engine never cares which is active.
"""
from __future__ import annotations

import sys
import threading
from typing import Optional

BUTTON_NAMES = ("left", "right", "middle")


class BackendError(RuntimeError):
    pass


class ClickBackend:
    name = "base"

    @classmethod
    def available(cls) -> bool:
        return False

    def position(self) -> Optional[tuple[int, int]]:
        raise NotImplementedError

    def move(self, x: int, y: int) -> None:
        raise NotImplementedError

    def press(self, button: str) -> None:
        raise NotImplementedError

    def release(self, button: str) -> None:
        raise NotImplementedError

    def click(self, button: str) -> None:
        self.press(button)
        self.release(button)

    def release_all(self) -> None:
        for b in BUTTON_NAMES:
            try:
                self.release(b)
            except Exception:
                pass


class DummyBackend(ClickBackend):
    """No-op backend that records events. Used by tests and --selftest."""

    name = "dummy"

    def __init__(self):
        self.events: list[tuple] = []
        self.clicks = 0
        self._pos = (500, 500)
        self._lock = threading.Lock()

    @classmethod
    def available(cls) -> bool:
        return True

    def set_position(self, x: int, y: int) -> None:
        self._pos = (x, y)

    def position(self):
        return self._pos

    def move(self, x, y):
        self._pos = (x, y)
        with self._lock:
            self.events.append(("move", x, y))

    def press(self, button):
        with self._lock:
            self.events.append(("press", button))

    def release(self, button):
        with self._lock:
            self.events.append(("release", button))

    def click(self, button):
        with self._lock:
            self.clicks += 1
            self.events.append(("click", button, self._pos))


class PynputBackend(ClickBackend):
    name = "pynput"

    def __init__(self):
        try:
            from pynput.mouse import Button, Controller
        except Exception as exc:  # ImportError or display errors
            raise BackendError(f"pynput unavailable: {exc}") from exc
        self._ctl = Controller()
        self._btn = {"left": Button.left, "right": Button.right, "middle": Button.middle}
        self._down: set[str] = set()

    @classmethod
    def available(cls) -> bool:
        try:
            import pynput.mouse  # noqa: F401
            return True
        except Exception:
            return False

    def position(self):
        p = self._ctl.position
        return int(p[0]), int(p[1])

    def move(self, x, y):
        self._ctl.position = (x, y)

    def press(self, button):
        self._ctl.press(self._btn[button])
        self._down.add(button)

    def release(self, button):
        self._ctl.release(self._btn[button])
        self._down.discard(button)

    def click(self, button):
        self._ctl.click(self._btn[button])


class PyAutoGuiBackend(ClickBackend):
    name = "pyautogui"

    def __init__(self):
        try:
            import pyautogui
        except Exception as exc:
            raise BackendError(f"pyautogui unavailable: {exc}") from exc
        pyautogui.FAILSAFE = False   # we have our own, configurable failsafe
        pyautogui.PAUSE = 0
        pyautogui.MINIMUM_DURATION = 0
        self._pg = pyautogui

    @classmethod
    def available(cls) -> bool:
        try:
            import pyautogui  # noqa: F401
            return True
        except Exception:
            return False

    def position(self):
        p = self._pg.position()
        return int(p[0]), int(p[1])

    def move(self, x, y):
        self._pg.moveTo(x, y, duration=0)

    def press(self, button):
        self._pg.mouseDown(button=button)

    def release(self, button):
        self._pg.mouseUp(button=button)

    def click(self, button):
        self._pg.click(button=button)


class Win32Backend(ClickBackend):
    name = "win32"
    _DOWN = {"left": 0x0002, "right": 0x0008, "middle": 0x0020}
    _UP = {"left": 0x0004, "right": 0x0010, "middle": 0x0040}

    def __init__(self):
        if not sys.platform.startswith("win"):
            raise BackendError("win32 backend is Windows-only")
        import ctypes
        from ctypes import wintypes
        self._ct = ctypes
        self._user32 = ctypes.windll.user32
        self._pt = wintypes.POINT

    @classmethod
    def available(cls) -> bool:
        return sys.platform.startswith("win")

    def position(self):
        pt = self._pt()
        if not self._user32.GetCursorPos(self._ct.byref(pt)):
            return None
        return int(pt.x), int(pt.y)

    def move(self, x, y):
        self._user32.SetCursorPos(int(x), int(y))

    def press(self, button):
        self._user32.mouse_event(self._DOWN[button], 0, 0, 0, 0)

    def release(self, button):
        self._user32.mouse_event(self._UP[button], 0, 0, 0, 0)

    def click(self, button):
        self._user32.mouse_event(self._DOWN[button], 0, 0, 0, 0)
        self._user32.mouse_event(self._UP[button], 0, 0, 0, 0)


_REGISTRY = {
    "win32": Win32Backend,
    "pynput": PynputBackend,
    "pyautogui": PyAutoGuiBackend,
}


def available_backends() -> list[str]:
    return [n for n, cls in _REGISTRY.items() if cls.available()]


def select_backend(preferred: str = "auto") -> ClickBackend:
    """Return a working backend instance, falling back down the chain."""
    chain = list(_REGISTRY) if preferred in ("auto", "", None) else [preferred] + [
        n for n in _REGISTRY if n != preferred]
    errors = []
    for name in chain:
        cls = _REGISTRY.get(name)
        if cls is None or not cls.available():
            continue
        try:
            return cls()
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    raise BackendError("No click backend available. " + "; ".join(errors))
