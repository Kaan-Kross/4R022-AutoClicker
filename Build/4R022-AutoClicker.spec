# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for 4R022 AutoClicker.  Run through Build/build.py (recommended).
import os
import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent          # repository root
MAIN = ROOT / "Main"
PKG = MAIN / "autoclicker"
ONEFILE = os.environ.get("AC_ONEFILE", "1") == "1"
NAME = "4R022-AutoClicker"

hidden = ["autoclicker.selftest", "autoclicker.qt_app"]
if sys.platform.startswith("win"):
    hidden += ["pynput.keyboard._win32", "pynput.mouse._win32"]
elif sys.platform == "darwin":
    hidden += ["pynput.keyboard._darwin", "pynput.mouse._darwin"]
else:
    hidden += ["pynput.keyboard._xorg", "pynput.mouse._xorg"]

datas = [
    (str(PKG / "assets"), "autoclicker/assets"),
    (str(PKG / "i18n" / "*.json"), "autoclicker/i18n"),
    (str(PKG / "plugins_examples"), "autoclicker/plugins_examples"),
]

if sys.platform.startswith("win"):
    icon = str(PKG / "assets" / "icon.ico")
elif sys.platform == "darwin":
    icon = str(PKG / "assets" / "icon.icns")
else:
    icon = str(PKG / "assets" / "emblem.png")

excludes = ["tkinter", "unittest", "pydoc", "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
            "PySide6.Qt3DCore", "PySide6.QtQuick", "PySide6.QtQml", "PySide6.QtMultimedia",
            "PySide6.QtNetwork", "PySide6.QtSql", "PySide6.QtPdf", "PySide6.QtCharts"]

a = Analysis(
    [str(MAIN / "main.py")],
    pathex=[str(MAIN)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

if ONEFILE and sys.platform != "darwin":
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name=NAME, debug=False, strip=False, upx=False,
              console=False, icon=icon, disable_windowed_traceback=False)
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=NAME, debug=False, strip=False, upx=False,
              console=False, icon=icon, disable_windowed_traceback=False)
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=NAME)
    if sys.platform == "darwin":
        app = BUNDLE(
            coll, name="4R022 AutoClicker.app", icon=icon, bundle_identifier="com.4r022.autoclicker",
            info_plist={
                "CFBundleDisplayName": "4R022 AutoClicker",
                "CFBundleShortVersionString": "1.0.0b1",
                "NSHighResolutionCapable": True,
                "NSAppleEventsUsageDescription": "4R022 AutoClicker sends mouse clicks on your behalf.",
            },
        )
