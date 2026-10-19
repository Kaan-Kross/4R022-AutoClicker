"""4R022 themes. Dark = black + bordeaux (bordo) text, Light = clean white + bordeaux accent."""
from __future__ import annotations

PALETTES = {
    "dark": {
        "bg": "#0A0A0C", "surface": "#131317", "surface2": "#1B1B21", "border": "#2C2C34",
        "text": "#F2536D",        # bordeaux, bright enough for AA contrast on near-black
        "muted": "#C85A6E", "accent": "#9B1229", "accent_hover": "#B8152F", "accent_text": "#FFFFFF",
        "danger": "#C4122F", "ok": "#3DDC84", "warn": "#FFB020", "input": "#0F0F13",
        "select": "#5A0D1B", "bar": "#B3122B", "bar2": "#FF5A74",
    },
    "light": {
        "bg": "#F5F3F4", "surface": "#FFFFFF", "surface2": "#F0EBED", "border": "#D8CFD3",
        "text": "#1C1215", "muted": "#6A5A60", "accent": "#8F0F22", "accent_hover": "#A8132A",
        "accent_text": "#FFFFFF", "danger": "#B00F28", "ok": "#12803F", "warn": "#B26A00",
        "input": "#FFFFFF", "select": "#F3C7CF", "bar": "#8F0F22", "bar2": "#D6334F",
    },
}


def palette(name: str) -> dict:
    return PALETTES.get(name, PALETTES["dark"])


def build_qss(name: str) -> str:
    p = palette(name)
    return f"""
* {{ outline: 0; }}
QWidget {{ background: {p['bg']}; color: {p['text']}; font-family: "Segoe UI", "Inter", "Helvetica Neue", "Noto Sans", Arial, sans-serif; }}
QToolTip {{ background: {p['surface2']}; color: {p['text']}; border: 1px solid {p['accent']}; padding: 4px 6px; }}
QLabel {{ background: transparent; }}
QLabel#Title {{ font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }}
QLabel#H2 {{ font-size: 15px; font-weight: 700; }}
QLabel#Muted {{ color: {p['muted']}; }}
QLabel#Badge {{ background: {p['surface2']}; border: 1px solid {p['border']}; border-radius: 10px; padding: 3px 12px; font-weight: 600; }}
QLabel#BigNumber {{ font-size: 30px; font-weight: 800; }}
QLabel#TileValue {{ font-size: 22px; font-weight: 800; }}
QLabel#TileName {{ color: {p['muted']}; font-size: 11px; }}

QFrame#Sidebar {{ background: {p['surface']}; border-right: 1px solid {p['border']}; }}
QFrame#Card, QFrame#Tile {{ background: {p['surface']}; border: 1px solid {p['border']}; border-radius: 12px; }}
QFrame#Card QLabel, QFrame#Tile QLabel {{ background: transparent; }}
QFrame#LogoBox {{ background: #000000; border: 1px solid {p['accent']}; border-radius: 12px; }}
QFrame#LogoBox QLabel {{ background: transparent; }}
QFrame#Line {{ background: {p['border']}; max-height: 1px; min-height: 1px; border: none; }}

QPushButton {{ background: {p['surface2']}; color: {p['text']}; border: 1px solid {p['border']}; border-radius: 8px; padding: 7px 14px; font-weight: 600; }}
QPushButton:hover {{ border-color: {p['accent_hover']}; }}
QPushButton:pressed {{ background: {p['select']}; }}
QPushButton:disabled {{ color: {p['muted']}; background: {p['surface']}; border-color: {p['border']}; }}
QPushButton:focus {{ border: 2px solid {p['accent_hover']}; }}
QPushButton#Primary {{ background: {p['accent']}; color: {p['accent_text']}; border: 1px solid {p['accent_hover']}; padding: 10px 22px; font-size: 14px; }}
QPushButton#Primary:hover {{ background: {p['accent_hover']}; }}
QPushButton#Primary:disabled {{ background: {p['surface2']}; color: {p['muted']}; border-color: {p['border']}; }}
QPushButton#Danger {{ background: {p['danger']}; color: #FFFFFF; border: 1px solid {p['danger']}; padding: 10px 18px; font-weight: 800; letter-spacing: 1px; }}
QPushButton#Danger:hover {{ background: #E0142F; }}
QPushButton#Nav {{ text-align: left; background: transparent; border: none; border-radius: 8px; padding: 10px 14px; font-size: 13px; }}
QPushButton#Nav:hover {{ background: {p['surface2']}; }}
QPushButton#Nav:checked {{ background: {p['accent']}; color: {p['accent_text']}; }}
QPushButton#Hotkey {{ min-width: 130px; font-family: "Consolas", "Menlo", "DejaVu Sans Mono", monospace; }}
QPushButton#Hotkey[capturing="true"] {{ background: {p['select']}; border: 2px dashed {p['accent_hover']}; }}
QPushButton#Seg {{ padding: 8px 18px; }}
QPushButton#Seg:checked {{ background: {p['accent']}; color: {p['accent_text']}; border-color: {p['accent_hover']}; }}
QPushButton#ClickPad {{ background: {p['accent']}; color: {p['accent_text']}; border: 3px solid {p['accent_hover']}; border-radius: 18px; font-size: 26px; font-weight: 900; letter-spacing: 2px; }}
QPushButton#ClickPad:hover {{ background: {p['accent_hover']}; }}
QPushButton#ClickPad:pressed {{ background: {p['select']}; color: {p['text']}; }}
QPushButton#ClickPad:disabled {{ background: {p['surface2']}; color: {p['muted']}; border-color: {p['border']}; }}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{ background: {p['input']}; color: {p['text']}; border: 1px solid {p['border']}; border-radius: 7px; padding: 5px 8px; selection-background-color: {p['accent']}; selection-color: #FFFFFF; }}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QPlainTextEdit:focus {{ border: 1px solid {p['accent_hover']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{ background: {p['surface']}; color: {p['text']}; selection-background-color: {p['accent']}; selection-color: #FFFFFF; border: 1px solid {p['border']}; }}
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 16px; border: none; background: transparent; }}

QCheckBox, QRadioButton {{ spacing: 8px; background: transparent; }}
QCheckBox::indicator, QRadioButton::indicator {{ width: 17px; height: 17px; border: 2px solid {p['muted']}; background: {p['input']}; }}
QCheckBox::indicator {{ border-radius: 4px; }}
QRadioButton::indicator {{ border-radius: 9px; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{ background: {p['accent_hover']}; border-color: {p['accent_hover']}; }}
QCheckBox:focus, QRadioButton:focus {{ color: {p['accent_hover']}; }}

QTabWidget::pane {{ border: 1px solid {p['border']}; border-radius: 10px; top: -1px; background: {p['surface']}; }}
QTabBar::tab {{ background: {p['surface2']}; color: {p['muted']}; padding: 8px 16px; border: 1px solid {p['border']}; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 3px; }}
QTabBar::tab:selected {{ background: {p['surface']}; color: {p['text']}; font-weight: 700; border-color: {p['accent']}; }}

QTableWidget, QListWidget {{ background: {p['surface']}; alternate-background-color: {p['surface2']}; gridline-color: {p['border']}; border: 1px solid {p['border']}; border-radius: 8px; selection-background-color: {p['select']}; selection-color: {p['text']}; }}
QHeaderView::section {{ background: {p['surface2']}; color: {p['text']}; padding: 6px; border: none; border-bottom: 2px solid {p['accent']}; font-weight: 700; }}
QTableCornerButton::section {{ background: {p['surface2']}; border: none; }}

QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 11px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {p['border']}; border-radius: 5px; min-height: 28px; }}
QScrollBar::handle:vertical:hover {{ background: {p['accent']}; }}
QScrollBar:horizontal {{ background: transparent; height: 11px; }}
QScrollBar::handle:horizontal {{ background: {p['border']}; border-radius: 5px; min-width: 28px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}

QSlider::groove:horizontal {{ height: 6px; background: {p['border']}; border-radius: 3px; }}
QSlider::handle:horizontal {{ background: {p['accent_hover']}; width: 16px; margin: -6px 0; border-radius: 8px; }}
QSlider::sub-page:horizontal {{ background: {p['accent']}; border-radius: 3px; }}
QProgressBar {{ background: {p['input']}; border: 1px solid {p['border']}; border-radius: 7px; text-align: center; height: 14px; }}
QProgressBar::chunk {{ background: {p['accent_hover']}; border-radius: 6px; }}
QMenu {{ background: {p['surface']}; color: {p['text']}; border: 1px solid {p['border']}; padding: 4px; }}
QMenu::item {{ padding: 7px 24px; border-radius: 5px; }}
QMenu::item:selected {{ background: {p['accent']}; color: #FFFFFF; }}
QMenu::separator {{ height: 1px; background: {p['border']}; margin: 4px 8px; }}
QStatusBar {{ background: {p['surface']}; border-top: 1px solid {p['border']}; }}
"""
