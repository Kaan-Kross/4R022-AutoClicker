from __future__ import annotations

import collections
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QTabWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)

from ...core import exporter
from ..widgets import Card, Tile, BarChart, fmt_time, make_page
from . import BasePage


class StatsPage(BasePage):
    def __init__(self, ctx):
        super().__init__(ctx)
        self._spark = collections.deque([0.0] * 60, maxlen=60)
        self._last_sample = 0.0
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget(); outer.addWidget(make_page(inner))
        root = QVBoxLayout(inner); root.setContentsMargins(26, 22, 26, 22); root.setSpacing(14)
        self.title = QLabel(); self.title.setObjectName("Title"); root.addWidget(self.title)

        row = QHBoxLayout()
        self.tiles = {}
        for k in ("total", "elapsed", "avg", "now", "peak", "errors"):
            t = Tile("stat." + k); self.tiles[k] = t; row.addWidget(t)
        root.addLayout(row)

        self.card_chart = Card("stat.chart")
        self.chart = BarChart(); self.chart.setMinimumHeight(110)
        self.card_chart.body.addWidget(self.chart)
        root.addWidget(self.card_chart)

        self.tabs = QTabWidget()
        self.tab_sessions = QWidget(); sv = QVBoxLayout(self.tab_sessions)
        self.tbl_sessions = self._table(7); sv.addWidget(self.tbl_sessions)
        self.tab_activity = QWidget(); av = QVBoxLayout(self.tab_activity)
        self.tbl_activity = self._table(3); av.addWidget(self.tbl_activity)
        self.tabs.addTab(self.tab_sessions, ""); self.tabs.addTab(self.tab_activity, "")
        self.tabs.setMinimumHeight(300)
        root.addWidget(self.tabs)

        self.card_exp = Card("export.title")
        er = QHBoxLayout()
        self.lbl_fmt = QLabel()
        er.addWidget(self.lbl_fmt)
        self.btn_fmt = {f: QPushButton(f.upper()) for f in exporter.FORMATS}
        for f, b in self.btn_fmt.items():
            b.clicked.connect(lambda _=False, ff=f: self._export(ff)); er.addWidget(b)
        er.addStretch(1)
        self.btn_open = QPushButton(); self.btn_clear = QPushButton()
        er.addWidget(self.btn_open); er.addWidget(self.btn_clear)
        self.card_exp.body.addLayout(er)
        self.lbl_dir = QLabel(); self.lbl_dir.setObjectName("Muted"); self.lbl_dir.setWordWrap(True)
        self.lbl_msg = QLabel(); self.lbl_msg.setWordWrap(True)
        self.card_exp.body.addWidget(self.lbl_dir); self.card_exp.body.addWidget(self.lbl_msg)
        root.addWidget(self.card_exp)
        root.addStretch(1)

        self.btn_open.clicked.connect(lambda: exporter.open_folder(self.ctx.settings.export_dir))
        self.btn_clear.clicked.connect(self._clear)
        self.retranslate(); self.refresh()

    @staticmethod
    def _table(cols: int) -> QTableWidget:
        t = QTableWidget(0, cols)
        t.setAlternatingRowColors(True); t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectRows)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return t

    # ---- data -----------------------------------------------------------------------------
    def refresh(self):
        t = self.tr_
        rows = list(reversed(self.ctx.sessions.load(limit=300)))
        tb = self.tbl_sessions
        tb.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = [r.get("started_at", "").replace("T", " "), fmt_time(r.get("duration_s", 0)), r.get("total_clicks", 0),
                    f"{r.get('avg_cps', 0):.2f}", f"{r.get('peak_cps', 0):.0f}",
                    f"{t('btn.' + r.get('button', 'left'))} / {t('mode.' + r.get('mode', 'single'))}",
                    t("reason." + str(r.get("stop_reason", "user")))]
            for j, v in enumerate(vals):
                it = QTableWidgetItem(str(v)); it.setTextAlignment(Qt.AlignCenter); tb.setItem(i, j, it)
        acts = list(reversed(self.ctx.activity.load(limit=300)))
        ta = self.tbl_activity
        ta.setRowCount(len(acts))
        for i, a in enumerate(acts):
            detail = ", ".join(f"{k}={v}" for k, v in a.items() if k not in ("ts", "event"))
            for j, v in enumerate((a.get("ts", "").replace("T", " "), t("act." + a.get("event", "")), detail)):
                it = QTableWidgetItem(str(v)); ta.setItem(i, j, it)
        self.lbl_dir.setText(t("export.dir", dir=self.ctx.settings.export_dir))

    def _export(self, fmt: str):
        which = self.tabs.currentIndex()
        rows = self.ctx.sessions.load() if which == 0 else self.ctx.activity.load()
        base = "sessions" if which == 0 else "activity"
        if not rows:
            self.lbl_msg.setText(self.tr_("export.empty")); return

        def done(path, err):
            if err:
                self.ctx.tasklog.error("export.failed", error=repr(err))
            else:
                self.ctx.tasklog.info("export.done", fmt=fmt, what=base, path=str(path))
        self.ctx.pool.submit(exporter.export_rows, rows, fmt, self.ctx.settings.export_dir, base, on_done=done)
        self.lbl_msg.setText(self.tr_("export.started", fmt=fmt.upper()))

    def _clear(self):
        if self.tabs.currentIndex() == 0:
            self.ctx.sessions.clear()
        else:
            self.ctx.activity.clear()
        self.refresh()

    # ---- ticks / i18n -----------------------------------------------------------------------------
    def tick(self, snap: dict):
        T = self.tiles
        T["total"].set_value(f"{snap['total']:,}".replace(",", " ")); T["elapsed"].set_value(fmt_time(snap["elapsed"]))
        T["avg"].set_value(f"{snap['avg_cps']:.2f}"); T["now"].set_value(f"{snap['instant_cps']:.0f}")
        T["peak"].set_value(f"{snap['peak_cps']:.0f}"); T["errors"].set_value(str(snap["errors"]))
        now = time.monotonic()
        if now - self._last_sample >= 1.0:
            self._last_sample = now
            self._spark.append(snap["instant_cps"])
            self.chart.set_values(self._spark)

    def on_show(self):
        self.refresh()

    def apply_theme(self, name: str):
        self.chart.set_theme(name)

    def retranslate(self):
        t = self.tr_
        self.title.setText(t("nav.stats"))
        for tile in self.tiles.values():
            tile.retitle(t)
        self.card_chart.retitle(t); self.card_exp.retitle(t)
        self.tabs.setTabText(0, t("stat.tab_sessions")); self.tabs.setTabText(1, t("stat.tab_activity"))
        self.tbl_sessions.setHorizontalHeaderLabels([t("cps.h.date"), t("cps.h.duration"), t("cps.h.clicks"),
                                                     t("cps.h.avg"), t("cps.h.peak"), t("stat.h.type"), t("stat.h.reason")])
        self.tbl_activity.setHorizontalHeaderLabels([t("cps.h.date"), t("stat.h.event"), t("stat.h.details")])
        self.lbl_fmt.setText(t("export.label")); self.btn_open.setText(t("export.open")); self.btn_clear.setText(t("stat.clear"))
        self.refresh()
