import os
import sys

os.environ["QT_API"] = "pyqt5"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings

from npworks_ide.ide.main_window import MainWindow
from npworks_ide.ide.theme import apply_theme


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

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
