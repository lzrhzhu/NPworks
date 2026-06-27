import os
import tempfile

from PyQt5.QtCore import QSettings

from npworks_ide.ide.themes.variables import LIGHT, DARK, LIGHT_VARS, DARK_VARS
from npworks_ide.ide.themes.palette import build_palette

_THEMES_DIR = os.path.dirname(os.path.abspath(__file__))
_QSS_PATH = os.path.join(_THEMES_DIR, "template.qss")
_RES_DIR = os.path.join(tempfile.gettempdir(), "npworks_qss_res")

# 16x16 的 X 关闭图标，颜色由 {color} 决定。
_X_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">'
    '<path fill="{color}" d="M8 8.707l-3.646 3.647-.708-.708L7.293 8 3.646 4.354'
    'l.708-.708L8 7.293l3.646-3.647.708.708L8.707 8l3.647 3.646-.708.708L8 8.707z"/></svg>'
)


def get_colors(theme_name=None):
    if theme_name is None:
        s = QSettings("npworks", "npworks")
        theme_name = s.value("theme", "light")
    return DARK if theme_name == "dark" else LIGHT


def _write_close_button_resources(v):
    os.makedirs(_RES_DIR, exist_ok=True)
    # dim 版颜色与标签条背景一致，在非活动标签上近乎隐身（VS Code 仅悬停/活动时显示 X）
    dim = _X_SVG.format(color=v["bg_menu"])
    bright = _X_SVG.format(color=v["fg"])
    for name, content in (("tab_close_dim.svg", dim), ("tab_close_bright.svg", bright)):
        with open(os.path.join(_RES_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
    return _RES_DIR.replace("\\", "/")


def _build_qss(theme_name):
    v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
    res_dir = _write_close_button_resources(v)
    with open(_QSS_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    for key, value in v.items():
        template = template.replace("{" + key + "}", value)
    template = template.replace("{res_dir}", res_dir)
    return template


def apply_theme(app, theme_name):
    s = QSettings("npworks", "npworks")
    s.setValue("theme", theme_name)
    app.setPalette(build_palette(theme_name))
    app.setStyleSheet(_build_qss(theme_name))
