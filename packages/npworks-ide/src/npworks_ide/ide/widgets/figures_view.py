"""图表视图：展示运行脚本时捕获的 matplotlib 图。

作为 SideView 挂载到次侧边栏。图随侧栏宽度自适应，并支持缩放（+/-/还原）。
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
)

_MARGIN = 24


class FiguresView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("figures_view")
        self._items = []          # [{"pix": QPixmap, "label": QLabel}]
        self._zoom = 1.0          # 1.0 = 适配侧栏宽度

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        bar = QWidget()
        bar.setObjectName("sidebar_title")
        bar.setFixedHeight(28)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 0, 6, 0)
        bl.setSpacing(4)
        self._info = QLabel("无图表")
        self._info.setStyleSheet("color: gray; font-size: 11px;")
        bl.addWidget(self._info)
        bl.addStretch()

        self._zoom_out = QPushButton("-")
        self._zoom_label = QPushButton("100%")
        self._zoom_in = QPushButton("+")
        self._clear = QPushButton("清空")
        for b in (self._zoom_out, self._zoom_label, self._zoom_in, self._clear):
            b.setObjectName("file_tree_btn")
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(22)
        self._zoom_label.setCheckable(False)
        self._zoom_out.clicked.connect(lambda: self._zoom_by(-0.1))
        self._zoom_in.clicked.connect(lambda: self._zoom_by(0.1))
        self._zoom_label.clicked.connect(self._zoom_reset)
        self._clear.clicked.connect(self.clear)
        bl.addWidget(self._zoom_out)
        bl.addWidget(self._zoom_label)
        bl.addWidget(self._zoom_in)
        bl.addWidget(self._clear)
        root.addWidget(bar)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._layout = QVBoxLayout(self._container)
        self._layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._layout.setSpacing(10)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.addStretch()
        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll)

    def _target_width(self):
        return max(120, (self._scroll.viewport().width() - _MARGIN) * self._zoom)

    def _zoom_by(self, delta):
        self._zoom = max(0.2, min(4.0, round(self._zoom + delta, 2)))
        self._update_zoom_label()
        self._relayout()

    def _zoom_reset(self):
        self._zoom = 1.0
        self._update_zoom_label()
        self._relayout()

    def _update_zoom_label(self):
        self._zoom_label.setText(f"{int(self._zoom * 100)}%")

    def add_figure(self, path):
        pix = QPixmap(path)
        if pix.isNull():
            return
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignCenter)
        idx = self._layout.count() - 1
        self._layout.insertWidget(idx, lbl)
        self._items.append({"pix": pix, "label": lbl})
        self._relayout_item(self._items[-1])
        self._info.setText(f"{len(self._items)} 张图表")

    def _relayout_item(self, item):
        pix = item["pix"]
        w = int(self._target_width())
        if w > 0 and (pix.width() > w or self._zoom != 1.0):
            item["label"].setPixmap(pix.scaledToWidth(w, Qt.SmoothTransformation))
        else:
            item["label"].setPixmap(pix)

    def _relayout(self):
        for item in self._items:
            self._relayout_item(item)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout()

    def clear(self):
        for item in self._items:
            self._layout.removeWidget(item["label"])
            item["label"].deleteLater()
        self._items.clear()
        self._info.setText("无图表")

    def apply_theme(self, theme_name):
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
        self.setStyleSheet(
            f"QWidget#figures_view {{ background: {v['bg_main']}; }}"
            f"QWidget#sidebar_title {{ background: {v['bg_menu']}; border-bottom: 1px solid {v['border']}; }}"
        )
