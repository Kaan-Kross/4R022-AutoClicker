from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSpinBox,
                               QComboBox, QRadioButton, QButtonGroup, QWidget, QSizePolicy)

from ...core.config import DEFAULT_HOTKEYS
from ...core.hotkeys import ACTIONS, parse_combo
from ...core.workers import S_IDLE, S_DELAY, S_RUNNING, S_PAUSED
from ..widgets import Card, Tile, HotkeyButton, fill_combo, fmt_time, make_page
from . import BasePage

BUTTON_ITEMS = [("left", "btn.left"), ("right", "btn.right"), ("middle", "btn.middle")]
MODE_ITEMS = [("single", "mode.single"), ("double", "mode.double"), ("burst", "mode.burst")]
POS_ITEMS = [("current", "pos.current"), ("fixed", "pos.fixed"), ("multi", "pos.multi")]


class HomePage(BasePage):
    changed = Signal()
    pick_requested = Signal(str)            # "fixed"
    _captured = Signal(str, str)            # action, combo  (thread-safe bridge)

    def __init__(self, ctx):
        super().__init__(ctx)
        self._loading = False
        self._capturing: tuple[str, HotkeyButton] | None = None
        self._captured.connect(self._on_captured)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget()
        outer.addWidget(make_page(inner))
        root = QVBoxLayout(inner)
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(14)

        # header --------------------------------------------------------------------
        head = QHBoxLayout()
        self.title = QLabel("4R022 AutoClicker"); self.title.setObjectName("Title")
        self.state_badge = QLabel(); self.state_badge.setObjectName("Badge")
        head.addWidget(self.title); head.addStretch(1); head.addWidget(self.state_badge)
        root.addLayout(head)
        self.subtitle = QLabel(); self.subtitle.setObjectName("Muted"); self.subtitle.setWordWrap(True)
        root.addWidget(self.subtitle)

        # live strip ----------------------------------------------------------------
        strip = QHBoxLayout()
        self.t_total = Tile("stat.total"); self.t_cps = Tile("stat.cps_now")
        self.t_avg = Tile("stat.avg_cps"); self.t_time = Tile("stat.elapsed")
        for t in (self.t_total, self.t_cps, self.t_avg, self.t_time):
            strip.addWidget(t)
        root.addLayout(strip)

        # control bar ---------------------------------------------------------------
        bar = QHBoxLayout()
        self.btn_start = QPushButton(); self.btn_start.setObjectName("Primary")
        self.btn_pause = QPushButton(); self.btn_stop = QPushButton()
        self.btn_kill = QPushButton(); self.btn_kill.setObjectName("Danger")
        for b in (self.btn_start, self.btn_pause, self.btn_stop):
            bar.addWidget(b)
        bar.addStretch(1); bar.addWidget(self.btn_kill)
        root.addLayout(bar)
        self.btn_start.clicked.connect(self._start)
        self.btn_stop.clicked.connect(lambda: self.ctx.engine.stop("user"))
        self.btn_pause.clicked.connect(self.ctx.engine.toggle_pause)
        self.btn_kill.clicked.connect(lambda: self.ctx.killswitch.trigger("killswitch"))

        # click settings --------------------------------------------------------------
        self.card_click = Card("card.click")
        g = QGridLayout(); g.setHorizontalSpacing(14); g.setVerticalSpacing(8)
        self.lbl_button = QLabel(); self.lbl_mode = QLabel()
        self.cb_button = QComboBox(); self.cb_mode = QComboBox()
        g.addWidget(self.lbl_button, 0, 0); g.addWidget(self.cb_button, 1, 0)
        g.addWidget(self.lbl_mode, 0, 1); g.addWidget(self.cb_mode, 1, 1)
        self.card_click.body.addLayout(g)
        root.addWidget(self.card_click)

        # interval ----------------------------------------------------------------------
        self.card_int = Card("card.interval")
        row = QHBoxLayout(); self.sp = {}
        self.int_labels = {}
        for key, hi in (("hours", 99), ("minutes", 59), ("seconds", 59), ("millis", 999)):
            col = QVBoxLayout()
            lab = QLabel(); self.int_labels[key] = lab
            sb = QSpinBox(); sb.setRange(0, hi); sb.setMinimumWidth(90)
            sb.valueChanged.connect(self._collect)
            self.sp[key] = sb
            col.addWidget(lab); col.addWidget(sb)
            row.addLayout(col)
        row.addStretch(1)
        self.card_int.body.addLayout(row)
        self.lbl_rate = QLabel(); self.lbl_rate.setObjectName("Muted")
        self.card_int.body.addWidget(self.lbl_rate)
        root.addWidget(self.card_int)

        # count ---------------------------------------------------------------------------
        self.card_count = Card("card.count")
        r = QHBoxLayout()
        self.rb_inf = QRadioButton(); self.rb_lim = QRadioButton()
        self.sp_count = QSpinBox(); self.sp_count.setRange(1, 10**9); self.sp_count.setValue(100)
        self.sp_count.setMinimumWidth(130)
        grp = QButtonGroup(self); grp.addButton(self.rb_inf); grp.addButton(self.rb_lim)
        r.addWidget(self.rb_inf); r.addSpacing(20); r.addWidget(self.rb_lim); r.addWidget(self.sp_count); r.addStretch(1)
        self.card_count.body.addLayout(r)
        self.rb_inf.toggled.connect(self._collect); self.sp_count.valueChanged.connect(self._collect)
        root.addWidget(self.card_count)

        # position ------------------------------------------------------------------------
        self.card_pos = Card("card.position")
        pr = QHBoxLayout()
        self.cb_pos = QComboBox()
        self.lbl_x = QLabel("X"); self.sp_x = QSpinBox(); self.lbl_y = QLabel("Y"); self.sp_y = QSpinBox()
        for s in (self.sp_x, self.sp_y):
            s.setRange(-100000, 100000); s.setMinimumWidth(90); s.valueChanged.connect(self._collect)
        self.btn_pick = QPushButton()
        pr.addWidget(self.cb_pos); pr.addSpacing(12)
        pr.addWidget(self.lbl_x); pr.addWidget(self.sp_x); pr.addWidget(self.lbl_y); pr.addWidget(self.sp_y)
        pr.addWidget(self.btn_pick); pr.addStretch(1)
        self.card_pos.body.addLayout(pr)
        self.lbl_targets = QLabel(); self.lbl_targets.setObjectName("Muted"); self.lbl_targets.setWordWrap(True)
        self.card_pos.body.addWidget(self.lbl_targets)
        root.addWidget(self.card_pos)
        self.btn_pick.clicked.connect(lambda: self.pick_requested.emit("fixed"))

        # hotkeys --------------------------------------------------------------------------
        self.card_hot = Card("card.hotkeys")
        hg = QGridLayout(); hg.setHorizontalSpacing(14)
        self.hk_labels, self.hk_buttons = {}, {}
        for i, action in enumerate(ACTIONS):
            lab = QLabel(); btn = HotkeyButton(ctx.settings.hotkeys.get(action, ""))
            btn.capture_requested.connect(lambda b, a=action: self._begin_capture(a, b))
            self.hk_labels[action] = lab; self.hk_buttons[action] = btn
            hg.addWidget(lab, i, 0); hg.addWidget(btn, i, 1)
        hg.setColumnStretch(2, 1)
        self.card_hot.body.addLayout(hg)
        hr = QHBoxLayout()
        self.btn_hk_reset = QPushButton(); self.lbl_hk_msg = QLabel(); self.lbl_hk_msg.setObjectName("Muted")
        self.lbl_hk_msg.setWordWrap(True)
        hr.addWidget(self.btn_hk_reset); hr.addWidget(self.lbl_hk_msg, 1)
        self.card_hot.body.addLayout(hr)
        self.btn_hk_reset.clicked.connect(self._reset_hotkeys)
        root.addWidget(self.card_hot)
        root.addStretch(1)

        for cb in (self.cb_button, self.cb_mode, self.cb_pos):
            cb.currentIndexChanged.connect(self._collect)
        self.retranslate()
        self.load()

    # ---- actions ---------------------------------------------------------------------------
    def _start(self):
        self._collect()
        self.ctx.engine.start(self.ctx.settings.click)

    # ---- hotkey capture ----------------------------------------------------------------------
    def _begin_capture(self, action: str, btn: HotkeyButton):
        if not self.ctx.hotkeys.is_running():
            self.lbl_hk_msg.setText(self.tr_("hotkey.unavailable"))
            return
        if self._capturing:
            prev_action, prev_btn = self._capturing
            prev_btn.set_capturing(False)
            self.ctx.hotkeys.capture(None)
            self._capturing = None
            if prev_btn is btn:                       # second click cancels
                self.lbl_hk_msg.setText("")
                return
        self._capturing = (action, btn)
        btn.set_prompt(self.tr_("hotkey.press_key"))
        btn.set_capturing(True)
        self.lbl_hk_msg.setText(self.tr_("hotkey.capture_hint"))
        self.ctx.hotkeys.capture(lambda combo, a=action: self._captured.emit(a, combo))

    def _on_captured(self, action: str, combo: str):
        if self._capturing:
            self._capturing[1].set_capturing(False)
        self._capturing = None
        if not parse_combo(combo)[1]:
            return
        for other, c in self.ctx.settings.hotkeys.items():
            if other != action and parse_combo(c) == parse_combo(combo):
                self.lbl_hk_msg.setText(self.tr_("hotkey.conflict", other=self.tr_("hk." + other)))
                self.hk_buttons[action].set_combo(self.ctx.settings.hotkeys[action])
                return
        self.ctx.settings.hotkeys[action] = combo
        self.ctx.apply_hotkeys()
        self.hk_buttons[action].set_combo(combo)
        self.lbl_hk_msg.setText(self.tr_("hotkey.saved"))
        self.ctx.tasklog.info("hotkey.set", action=action, combo=combo)
        self.changed.emit()

    def _reset_hotkeys(self):
        self.ctx.settings.hotkeys = dict(DEFAULT_HOTKEYS)
        self.ctx.apply_hotkeys()
        self.load()
        self.lbl_hk_msg.setText(self.tr_("hotkey.reset_done"))
        self.changed.emit()

    # ---- settings <-> widgets ------------------------------------------------------------------
    def load(self):
        self._loading = True
        c = self.ctx.settings.click
        for cb, val in ((self.cb_button, c.button), (self.cb_mode, c.mode), (self.cb_pos, c.position_mode)):
            cb.setCurrentIndex(max(0, cb.findData(val)))
        for k, sb in self.sp.items():
            sb.setValue(getattr(c, k))
        self.rb_inf.setChecked(c.count_limit == 0); self.rb_lim.setChecked(c.count_limit > 0)
        if c.count_limit > 0:
            self.sp_count.setValue(c.count_limit)
        self.sp_x.setValue(c.fixed_x); self.sp_y.setValue(c.fixed_y)
        for a, b in self.hk_buttons.items():
            b.set_combo(self.ctx.settings.hotkeys.get(a, ""))
        self._loading = False
        self._update_dependents()

    def _collect(self, *_):
        if self._loading:
            return
        c = self.ctx.settings.click
        c.button = self.cb_button.currentData() or "left"
        c.mode = self.cb_mode.currentData() or "single"
        c.position_mode = self.cb_pos.currentData() or "current"
        for k, sb in self.sp.items():
            setattr(c, k, sb.value())
        c.count_limit = 0 if self.rb_inf.isChecked() else self.sp_count.value()
        c.fixed_x, c.fixed_y = self.sp_x.value(), self.sp_y.value()
        self._update_dependents()
        self.changed.emit()

    def _update_dependents(self):
        c = self.ctx.settings.click
        self.sp_count.setEnabled(self.rb_lim.isChecked())
        fixed = self.cb_pos.currentData() == "fixed"
        for w in (self.sp_x, self.sp_y, self.btn_pick, self.lbl_x, self.lbl_y):
            w.setVisible(fixed)
        multi = self.cb_pos.currentData() == "multi"
        self.lbl_targets.setVisible(multi)
        self.lbl_targets.setText(self.tr_("pos.multi_info", n=len(c.targets)))
        ms = c.interval_ms()
        if ms <= 0:
            self.lbl_rate.setText(self.tr_("interval.max_speed"))
        else:
            self.lbl_rate.setText(self.tr_("interval.rate", ms=f"{ms:g}", cps=f"{1000.0 / ms:.2f}"))

    # ---- i18n / state -----------------------------------------------------------------------------
    def retranslate(self):
        t = self.tr_
        self.subtitle.setText(t("home.subtitle"))
        for card in (self.card_click, self.card_int, self.card_count, self.card_pos, self.card_hot):
            card.retitle(t)
        self.lbl_button.setText(t("lbl.button")); self.lbl_mode.setText(t("lbl.mode"))
        fill_combo(self.cb_button, BUTTON_ITEMS, t); fill_combo(self.cb_mode, MODE_ITEMS, t)
        fill_combo(self.cb_pos, POS_ITEMS, t)
        for k, lab in self.int_labels.items():
            lab.setText(t("unit." + k))
        self.rb_inf.setText(t("count.unlimited")); self.rb_lim.setText(t("count.limited"))
        self.btn_pick.setText(t("pos.pick")); self.btn_pick.setToolTip(t("pos.pick_tip"))
        self.btn_start.setText(t("btn.start")); self.btn_stop.setText(t("btn.stop"))
        self.btn_kill.setText(t("btn.kill")); self.btn_kill.setToolTip(t("btn.kill_tip"))
        for a in ACTIONS:
            self.hk_labels[a].setText(t("hk." + a))
        self.btn_hk_reset.setText(t("hotkey.reset"))
        for t_ in (self.t_total, self.t_cps, self.t_avg, self.t_time):
            t_.retitle(t)
        self.btn_start.setAccessibleName(t("btn.start")); self.btn_stop.setAccessibleName(t("btn.stop"))
        self.btn_kill.setAccessibleName(t("btn.kill"))
        self.set_state(self.ctx.engine.state)
        self._update_dependents()

    def set_state(self, state: str):
        t = self.tr_
        running = state in (S_RUNNING, S_DELAY, S_PAUSED)
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_pause.setEnabled(state in (S_RUNNING, S_PAUSED))
        self.btn_pause.setText(t("btn.resume") if state == S_PAUSED else t("btn.pause"))
        self.state_badge.setText("● " + t("state." + state))

    def tick(self, snap: dict):
        self.t_total.set_value(f"{snap['total']:,}".replace(",", " "))
        self.t_cps.set_value(f"{snap['instant_cps']:.0f}")
        self.t_avg.set_value(f"{snap['avg_cps']:.2f}")
        self.t_time.set_value(fmt_time(snap["elapsed"]))
