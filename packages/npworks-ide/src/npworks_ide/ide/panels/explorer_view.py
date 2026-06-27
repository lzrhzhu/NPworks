"""资源管理器视图：顶部"打开的编辑器"列表 + 下方文件夹树。

仿 VS Code：所有已打开标签列于顶部 Open Editors 区（单独打开的文件只出现在这里，
不塞进文件夹树）；下方是文件夹目录结构。
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QToolButton, QHeaderView,
)


class OpenEditorsList(QTreeWidget):
    """列出所有打开的标签：点击聚焦，× 关闭。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setColumnCount(2)
        self.setObjectName("open_editors")
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.itemClicked.connect(self._on_clicked)
        self._tab_widget = None
        self._close_cb = None

    def bind(self, tab_widget, close_callback):
        self._tab_widget = tab_widget
        self._close_cb = close_callback

    def refresh(self):
        if self._tab_widget is None:
            return
        tw = self._tab_widget
        self.clear()
        for i in range(tw.count()):
            widget = tw.widget(i)
            title = tw.tabText(i)
            item = QTreeWidgetItem([title, ""])
            item.setData(0, Qt.UserRole, widget)
            item.setToolTip(0, getattr(widget, "file_path", "") or title)
            self.addTopLevelItem(item)
            close = QToolButton()
            close.setText("\u2715")
            close.setToolTip("关闭")
            close.setCursor(Qt.PointingHandCursor)
            close.setStyleSheet(
                "QToolButton { border: none; padding: 2px; }"
                "QToolButton:hover { background: rgba(255,255,255,40); border-radius: 3px; }"
            )
            close.clicked.connect(lambda _=False, w=widget: self._close(w))
            self.setItemWidget(item, 1, close)

    def _on_clicked(self, item, _col):
        widget = item.data(0, Qt.UserRole)
        if widget is not None:
            idx = self._tab_widget.indexOf(widget)
            if idx >= 0:
                self._tab_widget.setCurrentIndex(idx)

    def _close(self, widget):
        if widget is None or self._close_cb is None:
            return
        idx = self._tab_widget.indexOf(widget)
        if idx >= 0:
            self._close_cb(idx)


class ExplorerView(QWidget):
    """资源管理器：Open Editors 区 + 文件夹树。"""

    def __init__(self, file_tree, parent=None):
        super().__init__(parent)
        self.file_tree = file_tree

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._header = QLabel("  打开的编辑器")
        self._header.setObjectName("sidebar_section")
        f = self._header.font()
        f.setBold(True)
        f.setPointSize(9)
        self._header.setFont(f)
        layout.addWidget(self._header)

        self.open_editors = OpenEditorsList()
        self.open_editors.setFixedHeight(120)
        layout.addWidget(self.open_editors)

        from PyQt5.QtWidgets import QFrame
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setObjectName("sidebar_separator")
        layout.addWidget(sep)

        layout.addWidget(self.file_tree)
