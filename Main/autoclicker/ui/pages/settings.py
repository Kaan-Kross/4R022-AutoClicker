from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QCheckBox, QComboBox,
                               QSlider, QSpinBox, QWidget, QFileDialog, QLineEdit)

from ... import APP_NAME, VERSION_LABEL, TAGLINE
from ...core import exporter, paths
from ...core.backend import available_backends
from ...core.config import AppSettings
from ...i18n import LANGUAGE_NAMES
from ..widgets import Card, LogoBox, make_page
from . import BasePage


class SettingsPage(BasePage):
    changed = Signal()
    language_changed = Signal(str)
    theme_changed = Signal(str)
    font_changed = Signal(int)
    behavior_changed = Signal()
    reset_requested = Signal()

    def __init__(self, ctx):
        super().__init__(ctx)
        self._loading = False
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        inner = QWidget(); outer.addWidget(make_page(inner))
        root = QVBoxLayout(inner); root.setContentsMargins(26, 22, 26, 22); root.setSpacing(14)
        self.title = QLabel(); self.title.setObjectName("Title"); root.addWidget(self.title)

        # appearance -------------------------------------------------------------------------
        self.card_app = Card("set.appearance")
        g = QGridLayout(); g.setHorizontalSpacing(16); g.setVerticalSpacing(10)
        self.lbl_lang = QLabel(); self.cb_lang = QComboBox()
        for code, name in LANGUAGE_NAMES.items():
            self.cb_lang.addItem(name, code)
        self.lbl_theme = QLabel()
        th = QHBoxLayout()
        self.btn_dark = QPushButton(); self.btn_light = QPushButton()
        for b in (self.btn_dark, self.btn_light):
            b.setObjectName("Seg"); b.setCheckable(True); th.addWidget(b)
        th.addStretch(1)
        self.lbl_font = QLabel(); self.sl_font = QSlider(Qt.Horizontal); self.sl_font.setRange(80, 160); self.sl_font.setSingleStep(5)
        self.lbl_font_val = QLabel()
        fr = QHBoxLayout(); fr.addWidget(self.sl_font, 1); fr.addWidget(self.lbl_font_val)
        g.addWidget(self.lbl_lang, 0, 0); g.addWidget(self.cb_lang, 0, 1)
        g.addWidget(self.lbl_theme, 1, 0); g.addLayout(th, 1, 1)
        g.addWidget(self.lbl_font, 2, 0); g.addLayout(fr, 2, 1)
        g.setColumnStretch(1, 1)
        self.card_app.body.addLayout(g)
        root.addWidget(self.card_app)

        # behaviour ---------------------------------------------------------------------------
        self.card_beh = Card("set.behavior")
        self.cb_bg = QCheckBox(); self.cb_min = QCheckBox(); self.cb_top = QCheckBox()
        self.cb_mini = QCheckBox(); self.cb_prot = QCheckBox(); self.cb_confirm = QCheckBox()
        for w in (self.cb_bg, self.cb_min, self.cb_top, self.cb_mini, self.cb_prot):
            self.card_beh.body.addWidget(w)
        self.lbl_prot = QLabel(); self.lbl_prot.setObjectName("Muted"); self.lbl_prot.setWordWrap(True)
        self.card_beh.body.addWidget(self.lbl_prot); self.card_beh.body.addWidget(self.cb_confirm)
        root.addWidget(self.card_beh)

        # killswitch ------------------------------------------------------------------------------
        self.card_kill = Card("set.killswitch")
        self.cb_kill_exit = QCheckBox()
        kr = QHBoxLayout(); self.lbl_auto = QLabel(); self.sp_auto = QSpinBox(); self.sp_auto.setRange(0, 100000); self.sp_auto.setSuffix(" min")
        kr.addWidget(self.lbl_auto); kr.addWidget(self.sp_auto); kr.addStretch(1)
        self.lbl_kill_hint = QLabel(); self.lbl_kill_hint.setObjectName("Muted"); self.lbl_kill_hint.setWordWrap(True)
        self.card_kill.body.addWidget(self.cb_kill_exit); self.card_kill.body.addLayout(kr); self.card_kill.body.addWidget(self.lbl_kill_hint)
        root.addWidget(self.card_kill)

        # backend --------------------------------------------------------------------------------------
        self.card_be = Card("set.backend")
        br = QHBoxLayout(); self.lbl_be = QLabel(); self.cb_be = QComboBox()
        br.addWidget(self.lbl_be); br.addWidget(self.cb_be); br.addStretch(1)
        self.lbl_be_info = QLabel(); self.lbl_be_info.setObjectName("Muted"); self.lbl_be_info.setWordWrap(True)
        self.card_be.body.addLayout(br); self.card_be.body.addWidget(self.lbl_be_info)
        root.addWidget(self.card_be)

        # export -----------------------------------------------------------------------------------------
        self.card_exp = Card("set.export")
        self.ed_dir = QLineEdit(); self.ed_dir.setReadOnly(True)
        er = QHBoxLayout()
        self.btn_choose = QPushButton(); self.btn_open = QPushButton(); self.btn_default = QPushButton(); self.btn_data = QPushButton()
        for b in (self.btn_choose, self.btn_open, self.btn_default, self.btn_data):
            er.addWidget(b)
        er.addStretch(1)
        self.card_exp.body.addWidget(self.ed_dir); self.card_exp.body.addLayout(er)
        root.addWidget(self.card_exp)

        # about --------------------------------------------------------------------------------------------
        self.card_about = Card("set.about")
        ar = QHBoxLayout()
        ar.addWidget(LogoBox(220))
        col = QVBoxLayout()
        self.lbl_about = QLabel(); self.lbl_about.setWordWrap(True); self.lbl_about.setTextFormat(Qt.RichText)
        self.btn_reset = QPushButton(); self.btn_reset.setObjectName("Danger")
        col.addWidget(self.lbl_about); col.addStretch(1); col.addWidget(self.btn_reset, 0, Qt.AlignLeft)
        ar.addLayout(col, 1)
        self.card_about.body.addLayout(ar)
        root.addWidget(self.card_about)
        root.addStretch(1)

        # wiring -------------------------------------------------------------------------------------------
        self.cb_lang.currentIndexChanged.connect(self._lang)
        self.btn_dark.clicked.connect(lambda: self._theme("dark")); self.btn_light.clicked.connect(lambda: self._theme("light"))
        self.sl_font.valueChanged.connect(self._font_live); self.sl_font.sliderReleased.connect(self._font_commit)
        for w in (self.cb_bg, self.cb_min, self.cb_top, self.cb_mini, self.cb_prot, self.cb_confirm, self.cb_kill_exit):
            w.toggled.connect(self._collect)
        self.sp_auto.valueChanged.connect(self._collect)
        self.cb_be.currentIndexChanged.connect(self._backend)
        self.btn_choose.clicked.connect(self._choose_dir); self.btn_default.clicked.connect(self._default_dir)
        self.btn_open.clicked.connect(lambda: exporter.open_folder(self.ctx.settings.export_dir))
        self.btn_data.clicked.connect(lambda: exporter.open_folder(paths.data_dir()))
        self.btn_reset.clicked.connect(self.reset_requested.emit)
        self.retranslate(); self.load()

    # ---- handlers --------------------------------------------------------------------------------------------
    def _lang(self):
        if self._loading:
            return
        code = self.cb_lang.currentData()
        if code and code != self.ctx.settings.language:
            self.language_changed.emit(code)

    def _theme(self, name: str):
        self.btn_dark.setChecked(name == "dark"); self.btn_light.setChecked(name == "light")
        if not self._loading and name != self.ctx.settings.theme:
            self.theme_changed.emit(name)

    def _font_live(self, v: int):
        self.lbl_font_val.setText(f"{v}%")
        if not self.sl_font.isSliderDown() and not self._loading:
            self._font_commit()

    def _font_commit(self):
        if not self._loading:
            self.font_changed.emit(self.sl_font.value())

    def _collect(self, *_):
        if self._loading:
            return
        s = self.ctx.settings
        s.run_in_background = self.cb_bg.isChecked(); s.start_minimized = self.cb_min.isChecked()
        s.always_on_top = self.cb_top.isChecked(); s.show_mini_panel = self.cb_mini.isChecked()
        s.key_protection = self.cb_prot.isChecked(); s.confirm_exit = self.cb_confirm.isChecked()
        s.kill_exit_app = self.cb_kill_exit.isChecked(); s.auto_shutdown_minutes = self.sp_auto.value()
        self.ctx.killswitch.configure(s.kill_exit_app, s.auto_shutdown_minutes)
        self.ctx.apply_hotkeys()
        self.behavior_changed.emit(); self.changed.emit()

    def _backend(self):
        if self._loading:
            return
        name = self.cb_be.currentData()
        ok = self.ctx.switch_backend(name)
        self.lbl_be_info.setText(self.tr_("set.backend_ok", name=self.ctx.backend.name) if ok
                                 else self.tr_("set.backend_busy"))
        self.changed.emit()

    def _choose_dir(self):
        d = QFileDialog.getExistingDirectory(self, self.tr_("set.choose_dir"), self.ctx.settings.export_dir)
        if d:
            self.ctx.settings.export_dir = d; self.ed_dir.setText(d); self.changed.emit()

    def _default_dir(self):
        d = str(paths.default_export_dir())
        self.ctx.settings.export_dir = d; self.ed_dir.setText(d); self.changed.emit()

    # ---- load / i18n -----------------------------------------------------------------------------------------------
    def load(self):
        self._loading = True
        s = self.ctx.settings
        self.cb_lang.setCurrentIndex(max(0, self.cb_lang.findData(s.language)))
        self.btn_dark.setChecked(s.theme == "dark"); self.btn_light.setChecked(s.theme == "light")
        self.sl_font.setValue(s.font_scale); self.lbl_font_val.setText(f"{s.font_scale}%")
        for w, v in ((self.cb_bg, s.run_in_background), (self.cb_min, s.start_minimized), (self.cb_top, s.always_on_top),
                     (self.cb_mini, s.show_mini_panel), (self.cb_prot, s.key_protection), (self.cb_confirm, s.confirm_exit),
                     (self.cb_kill_exit, s.kill_exit_app)):
            w.setChecked(v)
        self.sp_auto.setValue(s.auto_shutdown_minutes)
        self.ed_dir.setText(s.export_dir)
        self._fill_backends()
        self._loading = False

    def _fill_backends(self):
        self.cb_be.blockSignals(True)
        self.cb_be.clear()
        self.cb_be.addItem(self.tr_("set.backend_auto"), "auto")
        for n in available_backends():
            self.cb_be.addItem(n, n)
        self.cb_be.setCurrentIndex(max(0, self.cb_be.findData(self.ctx.settings.backend)))
        self.cb_be.blockSignals(False)
        self.lbl_be_info.setText(self.tr_("set.backend_current", name=self.ctx.backend.name))

    def retranslate(self):
        t = self.tr_
        self.title.setText(t("nav.settings"))
        for c in (self.card_app, self.card_beh, self.card_kill, self.card_be, self.card_exp, self.card_about):
            c.retitle(t)
        self.lbl_lang.setText(t("set.language")); self.lbl_theme.setText(t("set.theme"))
        self.btn_dark.setText(t("set.theme_dark")); self.btn_light.setText(t("set.theme_light"))
        self.lbl_font.setText(t("set.font_scale"))
        self.cb_bg.setText(t("set.background")); self.cb_min.setText(t("set.start_min")); self.cb_top.setText(t("set.on_top"))
        self.cb_mini.setText(t("set.mini")); self.cb_prot.setText(t("set.key_protection")); self.lbl_prot.setText(t("set.key_protection_hint"))
        self.cb_confirm.setText(t("set.confirm_exit"))
        self.cb_kill_exit.setText(t("set.kill_exit")); self.lbl_auto.setText(t("set.auto_shutdown")); self.lbl_kill_hint.setText(t("set.kill_hint"))
        self.lbl_be.setText(t("set.backend_label"))
        self.btn_choose.setText(t("set.choose_dir")); self.btn_open.setText(t("export.open"))
        self.btn_default.setText(t("set.default_dir")); self.btn_data.setText(t("set.open_data"))
        self.btn_reset.setText(t("set.reset"))
        self.lbl_about.setText(f"<h2>{APP_NAME}</h2><p><b>{VERSION_LABEL}</b> — {TAGLINE}</p><p>{t('set.about_text')}</p>")
        if hasattr(self, "cb_be"):
            self._loading = True; self._fill_backends(); self._loading = False
