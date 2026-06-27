from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy,
)

from npworks_ide.ide import icons
from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS


def _theme_vars(theme_name):
    return DARK_VARS if theme_name == "dark" else LIGHT_VARS


class ActivityBar(QWidget):
    button_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("activity_bar")
        self.setFixedWidth(48)
        self._buttons = []
        self._keys = []
        self._current_index = -1
        self._theme = "light"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._top_layout = QVBoxLayout()
        self._top_layout.setSpacing(0)
        layout.addLayout(self._top_layout)

        layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        self._bottom_layout = QVBoxLayout()
        self._bottom_layout.setSpacing(0)
        layout.addLayout(self._bottom_layout)

    def add_button(self, icon_key: str, tooltip: str, bottom: bool = False) -> int:
        btn = QPushButton(self)
        btn.setObjectName("activity_btn")
        btn.setFixedSize(48, 48)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setCheckable(True)
        btn.setIconSize(QSize(22, 22))
        index = len(self._buttons)
        btn.clicked.connect(lambda checked, idx=index: self._on_click(idx))
        self._buttons.append(btn)
        self._keys.append(icon_key)
        if bottom:
            self._bottom_layout.addWidget(btn)
        else:
            self._top_layout.addWidget(btn)
        return index

    def _on_click(self, index: int):
        if self._current_index == index:
            self.set_checked(-1)
            self.button_clicked.emit(-1)
        else:
            self.set_checked(index)
            self.button_clicked.emit(index)

    def set_checked(self, index: int):
        self._current_index = index
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
        self._refresh_icons()

    def apply_theme_icons(self, theme_name):
        self._theme = theme_name
        self._refresh_icons()

    def _refresh_icons(self):
        v = _theme_vars(self._theme)
        normal = v["activity_fg"]
        active = v["activity_checked_fg"]
        for i, btn in enumerate(self._buttons):
            key = self._keys[i]
            color = active if i == self._current_index else normal
            btn.setIcon(icons.icon(key, color, 22))

    @property
    def current_index(self):
        return self._current_index
