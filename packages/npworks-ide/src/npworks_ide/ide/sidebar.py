from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
)


class SidebarTitleBar(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar_title")
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(4)
        lbl = QLabel(title)
        lbl.setObjectName("dock_title_label")
        font = lbl.font()
        font.setBold(True)
        font.setPointSize(10)
        lbl.setFont(font)
        layout.addWidget(lbl)
        layout.addStretch()


class Sidebar(QWidget):
    def __init__(self, widget, title, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar_panel")
        self._widget = widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        title_bar = SidebarTitleBar(title, self)
        layout.addWidget(title_bar)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setObjectName("sidebar_separator")
        layout.addWidget(sep)
        layout.addWidget(widget)
