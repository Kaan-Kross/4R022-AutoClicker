"""Qt bootstrap: builds QApplication + AppContext + MainWindow."""
from __future__ import annotations

import sys

from . import APP_NAME


def run(argv: list[str], start_minimized: bool = False) -> int:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from .app import AppContext
    from .core import paths
    from .ui.main_window import MainWindow, apply_style

    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(str(paths.asset("emblem.png"))))
    ctx = AppContext()
    apply_style(app, ctx.settings)
    ctx.startup()
    win = MainWindow(ctx, app)
    ctx.killswitch.exit_callback = lambda: app.quit()
    if start_minimized or ctx.settings.start_minimized:
        if win.tray.available:
            win.hide_to_background()
        else:
            win.showMinimized()
    else:
        win.show()
    code = app.exec()
    try:
        win._finalize()
    except Exception:
        pass
    return code
