"""4R022 AutoClicker - entry point.

    python main.py                 start the application
    python main.py --minimized     start hidden in the tray
    python main.py --selftest      headless engine/self check (used by the build system)
    python main.py --selftest-gui  also builds every page offscreen
    python main.py --version
"""
from __future__ import annotations

import os
import sys


def _prepare_environment() -> None:
    # Make the package importable when running from source or frozen.
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("4R022.AutoClicker.1")
        except Exception:
            pass


def _fix_std_streams() -> None:
    # Windowed (no-console) frozen builds have sys.stdout/stderr == None.
    for name in ("stdout", "stderr"):
        if getattr(sys, name) is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    _fix_std_streams()
    _prepare_environment()
    argv = list(sys.argv if argv is None else argv)
    from autoclicker import VERSION_LABEL, APP_NAME, __version__

    if "--version" in argv:
        print(f"{APP_NAME} {VERSION_LABEL} ({__version__})")
        return 0
    if "--selftest" in argv or "--selftest-gui" in argv:
        from autoclicker.selftest import run_selftest
        return run_selftest(gui="--selftest-gui" in argv)
    from autoclicker.qt_app import run
    return run([a for a in argv if a not in ("--minimized",)], start_minimized="--minimized" in argv)


if __name__ == "__main__":
    sys.exit(main())
