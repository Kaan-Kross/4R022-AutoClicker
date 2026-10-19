from __future__ import annotations

import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QTabWidget, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPlainTextEdit)

from ...core import exporter, paths
from ...core.logger import read_error_log
from ..widgets import fill_combo
from . import BasePage

FILTERS = [("all", "log.f_all"), ("info", "log.f_info"), ("warn", "log.f_warn"), ("error", "log.f_error")]


class LogsPage(BasePage):
    def __init__(self, ctx):
        super().__init__(ctx)
        root = QVBoxLayout(self); root.setContentsMargins(26, 22, 26, 22); root.setSpacing(12)
        self.title = QLabel(); self.title.setObjectName("Title"); root.addWidget(self.title)
        self.tabs = QTabWidget(); root.addWidget(self.tabs, 1)

        # task tracking -------------------------------------------------------------------------
        t1 = QWidget(); v1 = QVBoxLayout(t1)
        bar = QHBoxLayout()
        self.lbl_filter = QLabel(); self.cb_filter = QComboBox()
        self.btn_clear = QPushButton(); self.btn_export = QPushButton()
        bar.addWidget(self.lbl_filter); bar.addWidget(self.cb_filter); bar.addStretch(1)
        bar.addWidget(self.btn_export); bar.addWidget(self.btn_clear)
        v1.addLayout(bar)
        self.table = QTableWidget(0, 3)
        self.table.setAlternatingRowColors(True); self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        v1.addWidget(self.table)
        self.tabs.addTab(t1, "")

        # error log -----------------------------------------------------------------------------------
        t2 = QWidget(); v2 = QVBoxLayout(t2)
        self.txt_err = QPlainTextEdit(); self.txt_err.setReadOnly(True)
        b2 = QHBoxLayout(); self.btn_err_refresh = QPushButton(); self.btn_err_folder = QPushButton()
        b2.addWidget(self.btn_err_refresh); b2.addWidget(self.btn_err_folder); b2.addStretch(1)
        v2.addLayout(b2); v2.addWidget(self.txt_err)
        self.tabs.addTab(t2, "")

        # diagnostics ----------------------------------------------------------------------------------
        t3 = QWidget(); v3 = QVBoxLayout(t3)
        self.txt_diag = QPlainTextEdit(); self.txt_diag.setReadOnly(True)
        b3 = QHBoxLayout(); self.btn_diag_refresh = QPushButton(); self.btn_diag_copy = QPushButton()
        b3.addWidget(self.btn_diag_refresh); b3.addWidget(self.btn_diag_copy); b3.addStretch(1)
        v3.addLayout(b3); v3.addWidget(self.txt_diag)
        self.tabs.addTab(t3, "")

        self._shown = 0
        self.cb_filter.currentIndexChanged.connect(self._rebuild)
        self.btn_clear.clicked.connect(self._clear)
        self.btn_export.clicked.connect(self._export)
        self.btn_err_refresh.clicked.connect(self._load_err)
        self.btn_err_folder.clicked.connect(lambda: exporter.open_folder(paths.logs_dir()))
        self.btn_diag_refresh.clicked.connect(self._load_diag)
        self.btn_diag_copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.txt_diag.toPlainText()))
        self.retranslate()

    # ---- rendering -------------------------------------------------------------------------------------
    def _render(self, item: dict) -> tuple[str, str, str]:
        t = self.tr_
        key = "log." + item["code"]
        try:
            msg = t(key, **item["params"]) if self.ctx.i18n.has(key) else f"{item['code']} {item['params']}"
        except Exception:
            msg = item["code"]
        return time.strftime("%H:%M:%S", time.localtime(item["ts"])), item["level"].upper(), msg

    def _visible(self, item: dict) -> bool:
        f = self.cb_filter.currentData() or "all"
        return f == "all" or item["level"] == f

    def _append(self, item: dict):
        ts, lvl, msg = self._render(item)
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c, v in enumerate((ts, lvl, msg)):
            it = QTableWidgetItem(v)
            if c == 1:
                it.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, c, it)

    def _rebuild(self):
        self.table.setRowCount(0)
        items = [i for i in self.ctx.tasklog.items() if self._visible(i)]
        for i in items[-1000:]:
            self._append(i)
        self._shown = len(self.ctx.tasklog.items())
        self.table.scrollToBottom()

    def tick(self, snap: dict):
        allitems = self.ctx.tasklog.items()
        if len(allitems) < self._shown:
            self._rebuild(); return
        new = allitems[self._shown:]
        if new:
            for i in new:
                if self._visible(i):
                    self._append(i)
            self._shown = len(allitems)
            self.table.scrollToBottom()

    def _clear(self):
        self.ctx.tasklog.clear(); self._shown = 0; self.table.setRowCount(0)

    def _export(self):
        rows = [dict(zip(("time", "level", "message"), self._render(i))) for i in self.ctx.tasklog.items()]
        if rows:
            self.ctx.pool.submit(exporter.export_rows, rows, "txt", self.ctx.settings.export_dir, "tasklog")

    def _load_err(self):
        self.txt_err.setPlainText(read_error_log() or self.tr_("log.no_errors"))
        self.txt_err.verticalScrollBar().setValue(self.txt_err.verticalScrollBar().maximum())

    def _load_diag(self):
        self.txt_diag.setPlainText(self.ctx.diagnostics())

    def on_show(self):
        self._rebuild(); self._load_err(); self._load_diag()

    def retranslate(self):
        t = self.tr_
        self.title.setText(t("nav.logs"))
        for i, k in enumerate(("log.tab_tasks", "log.tab_errors", "log.tab_diag")):
            self.tabs.setTabText(i, t(k))
        self.lbl_filter.setText(t("log.filter")); fill_combo(self.cb_filter, FILTERS, t)
        self.table.setHorizontalHeaderLabels([t("log.h.time"), t("log.h.level"), t("log.h.message")])
        self.btn_clear.setText(t("log.clear")); self.btn_export.setText(t("log.export"))
        self.btn_err_refresh.setText(t("log.refresh")); self.btn_err_folder.setText(t("log.open_folder"))
        self.btn_diag_refresh.setText(t("log.refresh")); self.btn_diag_copy.setText(t("log.copy"))
        self._rebuild()
