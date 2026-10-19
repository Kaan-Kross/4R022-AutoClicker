"""Reusable widgets for the 4R022 UI."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QFont, QPixmap
from PySide6.QtWidgets import (QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                               QComboBox, QSizePolicy, QScrollArea)

from ..core import paths
from ..core.hotkeys import pretty_combo
from . import theme


class Card(QFrame):
    """Titled rounded panel. `retitle()` re-applies the translated title."""

    def __init__(self, title_key: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._title_key = title_key
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(16, 14, 16, 16)
        self.body.setSpacing(10)
        self.title = QLabel()
        self.title.setObjectName("H2")
        self.title.setVisible(bool(title_key))
        self.body.addWidget(self.title)

    def retitle(self, tr) -> None:
        if self._title_key:
            self.title.setText(tr(self._title_key))


class Tile(QFrame):
    def __init__(self, name_key: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Tile")
        self.name_key = name_key
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        self.value = QLabel("0")
        self.value.setObjectName("TileValue")
        self.name = QLabel()
        self.name.setObjectName("TileName")
        self.name.setWordWrap(True)
        lay.addWidget(self.value)
        lay.addWidget(self.name)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def retitle(self, tr) -> None:
        self.name.setText(tr(self.name_key))
        self.setAccessibleName(tr(self.name_key))

    def set_value(self, text: str) -> None:
        self.value.setText(text)
        self.value.setAccessibleName(text)


class LogoBox(QFrame):
    """The 4R022 logo, always on black so the bordeaux artwork keeps its glow in both themes."""

    def __init__(self, width: int = 200, emblem_only: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("LogoBox")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lab = QLabel()
        lab.setAlignment(Qt.AlignCenter)
        pm = QPixmap(str(paths.asset("emblem.png" if emblem_only else "logo.png")))
        lab.setPixmap(pm.scaledToWidth(width, Qt.SmoothTransformation))
        lab.setAccessibleName("4R022 AutoClicker logo")
        lay.addWidget(lab)


class HLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Line")
        self.setFrameShape(QFrame.NoFrame)


def make_page(inner: QWidget) -> QScrollArea:
    """Wrap a page widget in a transparent scroll area."""
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.NoFrame)
    sa.setWidget(inner)
    return sa


def fill_combo(combo: QComboBox, items: list[tuple[str, str]], tr) -> None:
    """items = [(value, i18n_key)]. Keeps the selected value across re-translation."""
    current = combo.currentData()
    combo.blockSignals(True)
    combo.clear()
    for value, key in items:
        combo.addItem(tr(key), value)
    idx = combo.findData(current) if current is not None else 0
    combo.setCurrentIndex(max(0, idx))
    combo.blockSignals(False)


class HotkeyButton(QPushButton):
    """Shows the bound combo; click -> 'press any key' capture mode."""
    capture_requested = Signal(object)     # emits self

    def __init__(self, combo: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Hotkey")
        self.combo = combo
        self._prompt = "…"
        self.clicked.connect(lambda: self.capture_requested.emit(self))
        self.refresh()

    def set_prompt(self, text: str) -> None:
        self._prompt = text

    def set_combo(self, combo: str) -> None:
        self.combo = combo
        self.set_capturing(False)

    def set_capturing(self, on: bool) -> None:
        self.setProperty("capturing", "true" if on else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.refresh(on)

    def refresh(self, capturing: bool = False) -> None:
        self.setText(self._prompt if capturing else pretty_combo(self.combo))


class ClickPad(QPushButton):
    """Big CPS-test button. Counts on mouse *press* (not release) for maximum responsiveness."""
    hit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ClickPad")
        self.setMinimumHeight(190)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)

    def mousePressEvent(self, e):
        if e.button() in (Qt.LeftButton, Qt.RightButton, Qt.MiddleButton) and self.isEnabled():
            self.hit.emit()
            e.accept()
            return
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        e.accept()

    def mouseDoubleClickEvent(self, e):
        self.mousePressEvent(e)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter) and not e.isAutoRepeat():
            self.hit.emit()
            e.accept()
            return
        super().keyPressEvent(e)


class BarChart(QWidget):
    """Lightweight bar chart (per-second CPS, live sparkline)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.values: list[float] = []
        self.theme_name = "dark"
        self.setMinimumHeight(120)
        self.max_hint = 0.0
        self.setAccessibleName("CPS chart")

    def set_theme(self, name: str) -> None:
        self.theme_name = name
        self.update()

    def set_values(self, values, max_hint: float = 0.0) -> None:
        self.values = list(values)
        self.max_hint = max_hint
        self.update()

    def paintEvent(self, _):
        p = theme.palette(self.theme_name)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        qp.fillRect(0, 0, w, h, QColor(p["input"]))
        qp.setPen(QPen(QColor(p["border"]), 1))
        for i in range(1, 4):
            y = h - 18 - (h - 28) * i / 4
            qp.drawLine(6, int(y), w - 6, int(y))
        n = len(self.values)
        if n == 0:
            qp.end()
            return
        vmax = max(max(self.values), self.max_hint, 1.0)
        gap = 3
        bw = max(2.0, (w - 12 - gap * (n - 1)) / n)
        base = h - 18
        qp.setPen(Qt.NoPen)
        for i, v in enumerate(self.values):
            bh = (base - 8) * (v / vmax)
            x = 6 + i * (bw + gap)
            grad = QLinearGradient(QPointF(x, base - bh), QPointF(x, base))
            grad.setColorAt(0, QColor(p["bar2"]))
            grad.setColorAt(1, QColor(p["bar"]))
            qp.setBrush(grad)
            qp.drawRoundedRect(QRectF(x, base - bh, bw, max(bh, 1)), 3, 3)
            if n <= 30:
                qp.setPen(QColor(p["muted"]))
                f = QFont(self.font())
                f.setPointSize(max(7, f.pointSize() - 2))
                qp.setFont(f)
                qp.drawText(QRectF(x - 4, base + 2, bw + 8, 14), Qt.AlignCenter, str(i + 1))
                qp.setPen(Qt.NoPen)
        qp.setPen(QColor(p["muted"]))
        qp.drawText(QRectF(8, 2, 120, 14), Qt.AlignLeft, f"max {vmax:g}")
        qp.end()


def fmt_time(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"
