"""Small always-on-top status panel (frameless, draggable)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from ..core.workers import S_RUNNING, S_PAUSED, S_DELAY
from .widgets import fmt_time


class MiniPanel(QFrame):
    def __init__(self, ctx):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.ctx = ctx
        self.setObjectName("Card")
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        lay = QHBoxLayout(self); lay.setContentsMargins(12, 7, 12, 7); lay.setSpacing(12)
        self.dot = QLabel("●"); self.state = QLabel(); self.count = QLabel("0"); self.cps = QLabel("0 CPS"); self.time = QLabel("00:00:00")
        for w in (self.dot, self.state, self.count, self.cps, self.time):
            lay.addWidget(w)
        self._drag = None
        self.setAccessibleName("4R022 mini status panel")

    def update_snapshot(self, snap: dict) -> None:
        st = snap["state"]
        self.state.setText(self.ctx.t("state." + st))
        self.count.setText(f"{snap['total']:,}".replace(",", " "))
        self.cps.setText(f"{snap['instant_cps']:.0f} CPS")
        self.time.setText(fmt_time(snap["elapsed"]))
        color = {"running": "#3DDC84", "paused": "#FFB020", "delay": "#FFB020"}.get(st, "#888888")
        self.dot.setStyleSheet(f"color:{color}; background: transparent;")

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None
