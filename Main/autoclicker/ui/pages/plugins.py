from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem)

from ...core import exporter, paths
from . import BasePage


class PluginsPage(BasePage):
    def __init__(self, ctx):
        super().__init__(ctx)
        self._loading = False
        root = QVBoxLayout(self); root.setContentsMargins(26, 22, 26, 22); root.setSpacing(12)
        self.title = QLabel(); self.title.setObjectName("Title"); root.addWidget(self.title)
        self.lbl_info = QLabel(); self.lbl_info.setWordWrap(True); self.lbl_info.setObjectName("Muted")
        self.lbl_warn = QLabel(); self.lbl_warn.setWordWrap(True)
        root.addWidget(self.lbl_info); root.addWidget(self.lbl_warn)
        self.list = QListWidget(); self.list.setAlternatingRowColors(True)
        root.addWidget(self.list, 1)
        row = QHBoxLayout()
        self.btn_reload = QPushButton(); self.btn_folder = QPushButton()
        row.addWidget(self.btn_reload); row.addWidget(self.btn_folder); row.addStretch(1)
        root.addLayout(row)
        self.lbl_dir = QLabel(); self.lbl_dir.setObjectName("Muted"); self.lbl_dir.setWordWrap(True)
        root.addWidget(self.lbl_dir)
        self.list.itemChanged.connect(self._toggled)
        self.btn_reload.clicked.connect(self.load)
        self.btn_folder.clicked.connect(lambda: exporter.open_folder(paths.plugins_dir()))
        self.retranslate(); self.load()

    def load(self):
        self._loading = True
        self.ctx.plugins.discover()
        self.list.clear()
        for pid, info in self.ctx.plugins.available.items():
            it = QListWidgetItem(f"{info['name']}  v{info['version']}  —  {info['author']}\n{info['description']}")
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if pid in self.ctx.settings.plugins_enabled else Qt.Unchecked)
            it.setData(Qt.UserRole, pid)
            self.list.addItem(it)
        self._loading = False
        self.lbl_dir.setText(self.tr_("plug.dir", dir=str(paths.plugins_dir())))

    def _toggled(self, _):
        if self._loading:
            return
        enabled = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.checkState() == Qt.Checked:
                enabled.append(it.data(Qt.UserRole))
        self.ctx.settings.plugins_enabled = enabled
        self.ctx.plugins.sync(enabled)
        self.ctx.save()

    def on_show(self):
        self.load()

    def retranslate(self):
        t = self.tr_
        self.title.setText(t("nav.plugins"))
        self.lbl_info.setText(t("plug.info")); self.lbl_warn.setText("⚠ " + t("plug.warning"))
        self.btn_reload.setText(t("plug.reload")); self.btn_folder.setText(t("plug.open_folder"))
        self.lbl_dir.setText(t("plug.dir", dir=str(paths.plugins_dir())))
