from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSpinBox,
                               QDoubleSpinBox, QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
                               QHeaderView, QWidget, QAbstractItemView)

from ..widgets import Card, fill_combo, make_page
from . import BasePage

ORDER_ITEMS = [("sequential", "order.sequential"), ("random", "order.random"), ("pingpong", "order.pingpong")]


class AdvancedPage(BasePage):
    changed = Signal()
    pick_requested = Signal(str)       # "target"

    def __init__(self, ctx):
        super().__init__(ctx)
        self._loading = False
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget(); outer.addWidget(make_page(inner))
        root = QVBoxLayout(inner); root.setContentsMargins(26, 22, 26, 22); root.setSpacing(14)
        self.title = QLabel(); self.title.setObjectName("Title"); root.addWidget(self.title)

        # timing -----------------------------------------------------------------------
        self.card_time = Card("card.timing")
        g = QGridLayout(); g.setHorizontalSpacing(16); g.setVerticalSpacing(8)
        self.lbl_delay = QLabel(); self.sp_delay = QDoubleSpinBox(); self.sp_delay.setRange(0, 3600); self.sp_delay.setDecimals(1); self.sp_delay.setSuffix(" s")
        self.lbl_hold = QLabel(); self.sp_hold = QSpinBox(); self.sp_hold.setRange(0, 60000); self.sp_hold.setSuffix(" ms")
        self.lbl_loops = QLabel(); self.sp_loops = QSpinBox(); self.sp_loops.setRange(0, 10**9)
        self.lbl_runtime = QLabel(); self.sp_runtime = QSpinBox(); self.sp_runtime.setRange(0, 10**7); self.sp_runtime.setSuffix(" s")
        g.addWidget(self.lbl_delay, 0, 0); g.addWidget(self.sp_delay, 1, 0)
        g.addWidget(self.lbl_hold, 0, 1); g.addWidget(self.sp_hold, 1, 1)
        g.addWidget(self.lbl_loops, 0, 2); g.addWidget(self.sp_loops, 1, 2)
        g.addWidget(self.lbl_runtime, 0, 3); g.addWidget(self.sp_runtime, 1, 3)
        self.card_time.body.addLayout(g)
        self.lbl_loops_hint = QLabel(); self.lbl_loops_hint.setObjectName("Muted"); self.lbl_loops_hint.setWordWrap(True)
        self.card_time.body.addWidget(self.lbl_loops_hint)
        root.addWidget(self.card_time)

        # randomisation ---------------------------------------------------------------------
        self.card_rand = Card("card.random")
        r = QHBoxLayout()
        self.cb_rand = QCheckBox()
        self.lbl_min = QLabel(); self.sp_min = QSpinBox(); self.lbl_max = QLabel(); self.sp_max = QSpinBox()
        for s in (self.sp_min, self.sp_max):
            s.setRange(0, 3_600_000); s.setSuffix(" ms"); s.setMinimumWidth(110)
        self.lbl_jitter = QLabel(); self.sp_jitter = QSpinBox(); self.sp_jitter.setRange(0, 500); self.sp_jitter.setSuffix(" px")
        r.addWidget(self.cb_rand); r.addSpacing(10)
        r.addWidget(self.lbl_min); r.addWidget(self.sp_min); r.addWidget(self.lbl_max); r.addWidget(self.sp_max)
        r.addSpacing(18); r.addWidget(self.lbl_jitter); r.addWidget(self.sp_jitter); r.addStretch(1)
        self.card_rand.body.addLayout(r)
        root.addWidget(self.card_rand)

        # burst -------------------------------------------------------------------------------
        self.card_burst = Card("card.burst")
        b = QHBoxLayout()
        self.lbl_bc = QLabel(); self.sp_bc = QSpinBox(); self.sp_bc.setRange(1, 1000)
        self.lbl_bg = QLabel(); self.sp_bg = QSpinBox(); self.sp_bg.setRange(0, 10000); self.sp_bg.setSuffix(" ms")
        b.addWidget(self.lbl_bc); b.addWidget(self.sp_bc); b.addSpacing(16); b.addWidget(self.lbl_bg); b.addWidget(self.sp_bg); b.addStretch(1)
        self.card_burst.body.addLayout(b)
        root.addWidget(self.card_burst)

        # targets -----------------------------------------------------------------------------
        self.card_tg = Card("card.targets")
        top = QHBoxLayout()
        self.lbl_order = QLabel(); self.cb_order = QComboBox()
        top.addWidget(self.lbl_order); top.addWidget(self.cb_order); top.addStretch(1)
        self.lbl_active = QLabel(); self.lbl_active.setObjectName("Muted")
        top.addWidget(self.lbl_active)
        self.card_tg.body.addLayout(top)
        self.table = QTableWidget(0, 3)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setMinimumHeight(190)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(True)
        self.card_tg.body.addWidget(self.table)
        br = QHBoxLayout()
        self.btn_capture = QPushButton(); self.btn_addrow = QPushButton(); self.btn_del = QPushButton()
        self.btn_up = QPushButton("▲"); self.btn_down = QPushButton("▼"); self.btn_clear = QPushButton()
        for w in (self.btn_capture, self.btn_addrow, self.btn_del, self.btn_up, self.btn_down, self.btn_clear):
            br.addWidget(w)
        br.addStretch(1)
        self.card_tg.body.addLayout(br)
        self.lbl_tg_hint = QLabel(); self.lbl_tg_hint.setObjectName("Muted"); self.lbl_tg_hint.setWordWrap(True)
        self.card_tg.body.addWidget(self.lbl_tg_hint)
        root.addWidget(self.card_tg)

        # safety --------------------------------------------------------------------------------
        self.card_safe = Card("card.safety")
        self.cb_failsafe = QCheckBox()
        self.lbl_fs_hint = QLabel(); self.lbl_fs_hint.setObjectName("Muted"); self.lbl_fs_hint.setWordWrap(True)
        self.card_safe.body.addWidget(self.cb_failsafe); self.card_safe.body.addWidget(self.lbl_fs_hint)
        root.addWidget(self.card_safe)
        root.addStretch(1)

        for w in (self.sp_delay, self.sp_hold, self.sp_loops, self.sp_runtime, self.sp_min, self.sp_max,
                  self.sp_jitter, self.sp_bc, self.sp_bg):
            w.valueChanged.connect(self._collect)
        self.cb_rand.toggled.connect(self._collect); self.cb_failsafe.toggled.connect(self._collect)
        self.cb_order.currentIndexChanged.connect(self._collect)
        self.table.itemChanged.connect(self._on_item_changed)
        self.btn_capture.clicked.connect(lambda: self.pick_requested.emit("target"))
        self.btn_addrow.clicked.connect(self._add_row)
        self.btn_del.clicked.connect(self._del_rows)
        self.btn_clear.clicked.connect(self._clear)
        self.btn_up.clicked.connect(lambda: self._move(-1)); self.btn_down.clicked.connect(lambda: self._move(1))
        self.retranslate(); self.load()

    # ---- targets table ---------------------------------------------------------------------
    def _fill_table(self):
        self._loading = True
        tg = self.ctx.settings.click.targets
        self.table.setRowCount(len(tg))
        for i, t in enumerate(tg):
            for col, key in enumerate(("x", "y", "label")):
                it = QTableWidgetItem(str(t.get(key, "")))
                if col < 2:
                    it.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, col, it)
        self._loading = False

    def _on_item_changed(self, _):
        if self._loading:
            return
        tg = []
        for r in range(self.table.rowCount()):
            def cell(c):
                it = self.table.item(r, c)
                return it.text().strip() if it else ""
            try:
                tg.append({"x": int(cell(0)), "y": int(cell(1)), "label": cell(2)})
            except ValueError:
                tg.append({"x": 0, "y": 0, "label": cell(2)})
        self.ctx.settings.click.targets = tg
        self.changed.emit()

    def _add_row(self):
        self.ctx.settings.click.targets.append({"x": 0, "y": 0, "label": ""})
        self._fill_table(); self.changed.emit()

    def _del_rows(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        tg = self.ctx.settings.click.targets
        for r in rows:
            if 0 <= r < len(tg):
                tg.pop(r)
        self._fill_table(); self.changed.emit()

    def _clear(self):
        self.ctx.settings.click.targets = []
        self._fill_table(); self.changed.emit()

    def _move(self, d: int):
        rows = sorted({i.row() for i in self.table.selectedIndexes()})
        tg = self.ctx.settings.click.targets
        if len(rows) != 1:
            return
        r = rows[0]; n = r + d
        if 0 <= n < len(tg):
            tg[r], tg[n] = tg[n], tg[r]
            self._fill_table(); self.table.selectRow(n); self.changed.emit()

    # ---- settings <-> widgets ----------------------------------------------------------------
    def load(self):
        self._loading = True
        c = self.ctx.settings.click
        self.sp_delay.setValue(c.start_delay_s); self.sp_hold.setValue(c.hold_ms)
        self.sp_loops.setValue(c.loops); self.sp_runtime.setValue(c.max_runtime_s)
        self.cb_rand.setChecked(c.random_enabled); self.sp_min.setValue(c.random_min_ms); self.sp_max.setValue(c.random_max_ms)
        self.sp_jitter.setValue(c.jitter_px); self.sp_bc.setValue(c.burst_clicks); self.sp_bg.setValue(c.burst_gap_ms)
        self.cb_order.setCurrentIndex(max(0, self.cb_order.findData(c.sequence_order)))
        self.cb_failsafe.setChecked(c.failsafe_corner)
        self._loading = False
        self._fill_table(); self._update_enabled()

    def _collect(self, *_):
        if self._loading:
            return
        c = self.ctx.settings.click
        c.start_delay_s = self.sp_delay.value(); c.hold_ms = self.sp_hold.value()
        c.loops = self.sp_loops.value(); c.max_runtime_s = self.sp_runtime.value()
        c.random_enabled = self.cb_rand.isChecked(); c.random_min_ms = self.sp_min.value(); c.random_max_ms = self.sp_max.value()
        if c.random_max_ms < c.random_min_ms:
            c.random_max_ms = c.random_min_ms
            self._loading = True; self.sp_max.setValue(c.random_max_ms); self._loading = False
        c.jitter_px = self.sp_jitter.value(); c.burst_clicks = self.sp_bc.value(); c.burst_gap_ms = self.sp_bg.value()
        c.sequence_order = self.cb_order.currentData() or "sequential"
        c.failsafe_corner = self.cb_failsafe.isChecked()
        self._update_enabled(); self.changed.emit()

    def _update_enabled(self):
        on = self.cb_rand.isChecked()
        for w in (self.sp_min, self.sp_max, self.lbl_min, self.lbl_max):
            w.setEnabled(on)

    # ---- i18n / ticks ------------------------------------------------------------------------------
    def retranslate(self):
        t = self.tr_
        self.title.setText(t("nav.advanced"))
        for card in (self.card_time, self.card_rand, self.card_burst, self.card_tg, self.card_safe):
            card.retitle(t)
        self.lbl_delay.setText(t("adv.delay")); self.lbl_hold.setText(t("adv.hold"))
        self.lbl_loops.setText(t("adv.loops")); self.lbl_runtime.setText(t("adv.max_runtime"))
        self.lbl_loops_hint.setText(t("adv.loops_hint"))
        self.cb_rand.setText(t("adv.random_on")); self.lbl_min.setText(t("adv.min")); self.lbl_max.setText(t("adv.max"))
        self.lbl_jitter.setText(t("adv.jitter"))
        self.lbl_bc.setText(t("adv.burst_clicks")); self.lbl_bg.setText(t("adv.burst_gap"))
        self.lbl_order.setText(t("adv.order")); fill_combo(self.cb_order, ORDER_ITEMS, t)
        self.table.setHorizontalHeaderLabels(["X", "Y", t("adv.label")])
        self.btn_capture.setText(t("adv.capture")); self.btn_addrow.setText(t("adv.add_row"))
        self.btn_del.setText(t("adv.delete")); self.btn_clear.setText(t("adv.clear"))
        self.lbl_tg_hint.setText(t("adv.targets_hint", key=self.ctx.settings.hotkeys.get("add_target", "")))
        self.cb_failsafe.setText(t("adv.failsafe")); self.lbl_fs_hint.setText(t("adv.failsafe_hint"))
        self.btn_up.setAccessibleName(t("adv.move_up")); self.btn_down.setAccessibleName(t("adv.move_down"))

    def tick(self, snap: dict):
        i = snap.get("target_index", -1)
        if snap["state"] in ("running", "paused") and i >= 0 and self.ctx.settings.click.position_mode == "multi":
            self.lbl_active.setText(self.tr_("adv.active_target", n=i + 1))
        else:
            self.lbl_active.setText("")
