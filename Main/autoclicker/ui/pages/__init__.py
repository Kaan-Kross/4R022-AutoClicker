"""UI pages. Every page implements retranslate(), apply_theme(), load(), tick(), set_state()."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget


class BasePage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def tr_(self, key: str, /, **kw) -> str:
        return self.ctx.t(key, **kw)

    def retranslate(self) -> None: ...
    def apply_theme(self, name: str) -> None: ...
    def load(self) -> None: ...                      # (re)load widgets from ctx.settings
    def tick(self, snap: dict) -> None: ...          # ~10 Hz while the page is visible
    def set_state(self, state: str) -> None: ...     # engine state changed
    def on_show(self) -> None: ...                   # page became visible
