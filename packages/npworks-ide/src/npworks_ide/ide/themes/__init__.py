import os

from PyQt5.QtCore import QSettings

from npworks_ide.ide.themes.variables import LIGHT, DARK, LIGHT_VARS, DARK_VARS
from npworks_ide.ide.themes.palette import build_palette

_THEMES_DIR = os.path.dirname(os.path.abspath(__file__))
_QSS_PATH = os.path.join(_THEMES_DIR, "template.qss")


def get_colors(theme_name=None):
    if theme_name is None:
        s = QSettings("npworks", "npworks")
        theme_name = s.value("theme", "light")
    return DARK if theme_name == "dark" else LIGHT


def _build_qss(theme_name):
    v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
    with open(_QSS_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    for key, value in v.items():
        template = template.replace("{" + key + "}", value)
    return template


def apply_theme(app, theme_name):
    s = QSettings("npworks", "npworks")
    s.setValue("theme", theme_name)
    app.setPalette(build_palette(theme_name))
    app.setStyleSheet(_build_qss(theme_name))
