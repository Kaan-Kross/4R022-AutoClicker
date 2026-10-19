from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QWidget,
                               QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)

from ...core import exporter
from ...core.cps_test import CPSTest, DURATIONS
from ..widgets import Card, ClickPad, BarChart, Tile, make_page
from . import BasePage


class CpsPage(BasePage):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.test = CPSTest(15)
        self.last_result: dict | None = None
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget(); outer.addWidget(make_page(inner))
        root = QVBoxLayout(inner); root.setContentsMargins(26, 22, 26, 22); root.setSpacing(14)

        head = QHBoxLayout()
        self.title = QLabel(); self.title.setObjectName("Title")
        self.badge = QLabel(); self.badge.setObjectName("Badge")
        head.addWidget(self.title); head.addStretch(1); head.addWidget(self.badge)
        root.addLayout(head)

        seg = QHBoxLayout()
        self.seg_btns = {}
        for d in DURATIONS:
            b = QPushButton(); b.setObjectName("Seg"); b.setCheckable(True)
            b.clicked.connect(lambda _=False, dd=d: self._select(dd))
            self.seg_btns[d] = b; seg.addWidget(b)
        seg.addStretch(1)
        self.btn_reset = QPushButton()
        self.btn_reset.clicked.connect(self.reset)
        seg.addWidget(self.btn_reset)
        root.addLayout(seg)

        live = QHBoxLayout()
        self.t_left = Tile("cps.time_left"); self.t_clicks = Tile("cps.clicks"); self.t_live = Tile("cps.live"); self.t_best = Tile("cps.best")
        for t in (self.t_left, self.t_clicks, self.t_live, self.t_best):
            live.addWidget(t)
        root.addLayout(live)

        self.progress = QProgressBar(); self.progress.setRange(0, 1000); self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        self.pad = ClickPad(); self.pad.hit.connect(self._hit)
        root.addWidget(self.pad)
        self.hint = QLabel(); self.hint.setObjectName("Muted"); self.hint.setAlignment(Qt.AlignCenter); self.hint.setWordWrap(True)
        root.addWidget(self.hint)

        self.card_chart = Card("cps.chart")
        self.chart = BarChart(); self.card_chart.body.addWidget(self.chart)
        root.addWidget(self.card_chart)

        self.card_res = Card("cps.results")
        self.grid = QGridLayout(); self.grid.setHorizontalSpacing(10); self.grid.setVerticalSpacing(10)
        self.res_tiles = {}
        keys = ["total", "avg_cps", "peak_cps", "score", "consistency", "avg_interval", "fastest", "slowest", "first_half", "second_half"]
        for i, k in enumerate(keys):
            t = Tile("cps.r." + k); self.res_tiles[k] = t
            self.grid.addWidget(t, i // 5, i % 5)
        self.card_res.body.addLayout(self.grid)
        self.rank_lbl = QLabel(); self.rank_lbl.setObjectName("H2"); self.rank_lbl.setAlignment(Qt.AlignCenter)
        self.new_best_lbl = QLabel(); self.new_best_lbl.setObjectName("Badge"); self.new_best_lbl.setAlignment(Qt.AlignCenter)
        self.card_res.body.addWidget(self.rank_lbl); self.card_res.body.addWidget(self.new_best_lbl)
        root.addWidget(self.card_res)

        self.card_hist = Card("cps.history")
        self.table = QTableWidget(0, 6)
        self.table.setAlternatingRowColors(True); self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(180)
        self.card_hist.body.addWidget(self.table)
        hb = QHBoxLayout()
        self.btn_exp = {f: QPushButton(f.upper()) for f in exporter.FORMATS}
        self.btn_clear = QPushButton(); self.lbl_exp = QLabel(); self.lbl_exp.setObjectName("Muted"); self.lbl_exp.setWordWrap(True)
        self.lbl_export_caption = QLabel()
        hb.addWidget(self.lbl_export_caption)
        for f, b in self.btn_exp.items():
            b.clicked.connect(lambda _=False, ff=f: self._export(ff)); hb.addWidget(b)
        hb.addStretch(1); hb.addWidget(self.btn_clear)
        self.card_hist.body.addLayout(hb); self.card_hist.body.addWidget(self.lbl_exp)
        self.btn_clear.clicked.connect(self._clear_history)
        root.addWidget(self.card_hist)
        root.addStretch(1)

        self.timer = QTimer(self); self.timer.setInterval(50); self.timer.timeout.connect(self._on_timer)
        self.retranslate(); self._select(15); self._refresh_history()

    # ---- test flow ----------------------------------------------------------------------------
    def _select(self, d: int):
        if self.test.state == CPSTest.RUNNING:
            for k, b in self.seg_btns.items():
                b.setChecked(k == self.test.duration)
            return
        for k, b in self.seg_btns.items():
            b.setChecked(k == d)
        self.test.reset(d)
        self.reset()

    def reset(self):
        self.timer.stop()
        self.test.reset()
        self.pad.setEnabled(True)
        self.pad.setText(self.tr_("cps.click_me"))
        self.progress.setValue(0)
        self.chart.set_values([0] * self.test.duration)
        self.t_left.set_value(f"{self.test.duration:.1f}"); self.t_clicks.set_value("0"); self.t_live.set_value("0")
        self._show_best()
        self.badge.setText("● " + self.tr_("cps.ready"))
        self.hint.setText(self.tr_("cps.hint"))
        self.new_best_lbl.setVisible(False)
        self.card_res.setVisible(self.last_result is not None)

    def _hit(self):
        if self.test.state == CPSTest.FINISHED:
            return
        first = self.test.state == CPSTest.IDLE
        self.test.click()
        if first:
            self.timer.start()
            self.badge.setText("● " + self.tr_("cps.running"))
        self.t_clicks.set_value(str(len(self.test.stamps)))
        self.pad.setText(str(len(self.test.stamps)))

    def _on_timer(self):
        t = self.test
        if t.tick():
            self._finish()
            return
        self.t_left.set_value(f"{t.remaining():.1f}")
        self.t_live.set_value(f"{t.live_cps():.0f}")
        self.progress.setValue(int(1000 * t.elapsed() / t.duration))
        buckets = t.per_second()
        self.chart.set_values(buckets)

    def _finish(self):
        self.timer.stop()
        res = self.test.result()
        self.last_result = res
        self.pad.setEnabled(False)
        self.progress.setValue(1000)
        self.t_left.set_value("0.0"); self.t_live.set_value("0")
        self.t_clicks.set_value(str(res["total"]))
        self.chart.set_values(res["per_second"])
        new_best = self.ctx.cps_store.add(res)
        self.ctx.tasklog.info("cps.finished", total=res["total"], duration=res["duration"], avg=res["avg_cps"])
        self._render_result(res, new_best)
        self._show_best()
        self._refresh_history()
        self.badge.setText("● " + self.tr_("cps.finished"))
        self.hint.setText(self.tr_("cps.again"))
        QTimer.singleShot(900, lambda: self.pad.setEnabled(True) if self.test.state == CPSTest.FINISHED else None)
        QTimer.singleShot(900, lambda: self.pad.setText(self.tr_("cps.retry")) if self.test.state == CPSTest.FINISHED else None)

    def _render_result(self, r: dict, new_best: bool):
        T = self.res_tiles
        T["total"].set_value(str(r["total"])); T["avg_cps"].set_value(f"{r['avg_cps']:.2f}")
        T["peak_cps"].set_value(f"{r['peak_cps']:.0f}"); T["score"].set_value(str(r["score"]))
        T["consistency"].set_value(f"{r['consistency']:.0f}%"); T["avg_interval"].set_value(f"{r['avg_interval_ms']:.0f} ms")
        T["fastest"].set_value(f"{r['fastest_gap_ms']:.0f} ms"); T["slowest"].set_value(f"{r['slowest_gap_ms']:.0f} ms")
        T["first_half"].set_value(f"{r['first_half_cps']:.2f}"); T["second_half"].set_value(f"{r['second_half_cps']:.2f}")
        self.rank_lbl.setText(self.tr_("cps.rank") + ": " + self.tr_(f"rank.{r['rank']}"))
        self.new_best_lbl.setVisible(new_best)
        self.new_best_lbl.setText("🏆 " + self.tr_("cps.new_best"))
        self.card_res.setVisible(True)

    def _show_best(self):
        b = self.ctx.cps_store.best(self.test.duration)
        self.t_best.set_value(f"{b['total']} ({b['avg_cps']:.1f}/s)" if b else "—")

    # ---- history -----------------------------------------------------------------------------------
    def _refresh_history(self):
        rows = list(reversed(self.ctx.cps_store.results()))[:100]
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = [r.get("ts", "").replace("T", " "), f"{r.get('duration')} s", r.get("total"),
                    f"{r.get('avg_cps', 0):.2f}", f"{r.get('peak_cps', 0):.0f}", r.get("score")]
            for j, v in enumerate(vals):
                it = QTableWidgetItem(str(v)); it.setTextAlignment(Qt.AlignCenter); self.table.setItem(i, j, it)

    def _export(self, fmt: str):
        rows = self.ctx.cps_store.results()
        if not rows:
            self.lbl_exp.setText(self.tr_("export.empty")); return
        self.ctx.pool.submit(exporter.export_rows, rows, fmt, self.ctx.settings.export_dir, "cps-results",
                             on_done=lambda p, e: None)
        self.lbl_exp.setText(self.tr_("export.started", fmt=fmt.upper()))
        self.ctx.tasklog.info("export.done", fmt=fmt, what="cps")

    def _clear_history(self):
        self.ctx.cps_store.clear(); self._refresh_history(); self._show_best()

    # ---- i18n / theme ---------------------------------------------------------------------------------
    def retranslate(self):
        t = self.tr_
        self.title.setText(t("nav.cps"))
        for d, b in self.seg_btns.items():
            b.setText(t("cps.seconds", n=d))
        self.btn_reset.setText(t("cps.reset")); self.btn_clear.setText(t("cps.clear"))
        for tile in (self.t_left, self.t_clicks, self.t_live, self.t_best, *self.res_tiles.values()):
            tile.retitle(t)
        for c in (self.card_chart, self.card_res, self.card_hist):
            c.retitle(t)
        self.table.setHorizontalHeaderLabels([t("cps.h.date"), t("cps.h.duration"), t("cps.h.clicks"),
                                              t("cps.h.avg"), t("cps.h.peak"), t("cps.h.score")])
        self.lbl_export_caption.setText(t("export.label"))
        if self.test.state == CPSTest.IDLE:
            self.pad.setText(t("cps.click_me")); self.hint.setText(t("cps.hint")); self.badge.setText("● " + t("cps.ready"))
        if self.last_result:
            self._render_result(self.last_result, self.new_best_lbl.isVisible())

    def apply_theme(self, name: str):
        self.chart.set_theme(name)

    def on_show(self):
        self._refresh_history()
