import os
import sys

os.environ["QT_API"] = "pyqt5"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings

# 允许 QtWebEngine 在 QApplication 之后被插件导入（markdown 渲染插件）
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from npworks_ide.ide.main_window import MainWindow
from npworks_ide.ide.theme import apply_theme
from npworks_ide.ide import icons
from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NPworks")
    app.setOrganizationName("npworks")

    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    settings = QSettings("npworks", "npworks")
    theme = settings.value("theme", "dark")
    apply_theme(app, theme)

    v = DARK_VARS if theme == "dark" else LIGHT_VARS
    app.setWindowIcon(icons.logo_icon(v["activity_checked_fg"], 64))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
