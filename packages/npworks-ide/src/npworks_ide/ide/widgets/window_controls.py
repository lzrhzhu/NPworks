from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from npworks_ide.ide.platform import icons
from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS


def _vars(theme):
    return DARK_VARS if theme == "dark" else LIGHT_VARS


class WindowControls(QWidget):
    """窗口控制按钮组：最小化 / 最大化-还原 / 关闭。"""

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self._win = window
        self._theme = "light"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._btn_min = self._mk("wc_btn", "winmin", "最小化", self._minimize)
        self._btn_max = self._mk("wc_btn", "winmax", "最大化", self._toggle_max)
        self._btn_close = self._mk("wc_close", "winclose", "关闭", self._close)

        layout.addWidget(self._btn_min)
        layout.addWidget(self._btn_max)
        layout.addWidget(self._btn_close)

        self.refresh_icons("light")

    def _mk(self, object_name, key, tip, slot):
        btn = QPushButton(self)
        btn.setObjectName(object_name)
        btn.setCursor(Qt.ArrowCursor)
        btn.setToolTip(tip)
        btn.setIconSize(QSize(12, 12))
        btn.setFixedSize(46, 32)
        btn.clicked.connect(slot)
        btn._icon_key = key
        return btn

    def _minimize(self):
        self._win.showMinimized()

    def _toggle_max(self):
        if self._win.isMaximized():
            self._win.showNormal()
        else:
            self._win.showMaximized()

    def _close(self):
        self._win.close()

    def refresh_icons(self, theme):
        self._theme = theme
        self._update_max_icon()

    def _update_max_icon(self):
        v = _vars(self._theme)
        color = v["fg"]
        self._btn_min.setIcon(icons.icon(self._btn_min._icon_key, color, 12))
        max_key = "winrestore" if self._win.isMaximized() else "winmax"
        self._btn_max.setIcon(icons.icon(max_key, color, 12))
        self._btn_close.setIcon(icons.icon(self._btn_close._icon_key, color, 12))

    # 兼容别名
    update_icons = _update_max_icon
