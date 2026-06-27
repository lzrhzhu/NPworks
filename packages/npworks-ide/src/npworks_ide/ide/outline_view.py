"""大纲视图：解析当前编辑器的 Python 符号（class/def），点击跳转。

作为 SideView 挂载到侧边栏容器。
"""
import re

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel


_SYMBOL_RE = re.compile(r"^(\s*)(class|def|async\s+def)\s+(\w+)")


class OutlineView(QWidget):
    jump_requested = pyqtSignal(int, int)   # line, column

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self._mw = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setRootIsDecorated(False)
        self._tree.setObjectName("outline_tree")
        self._tree.itemClicked.connect(self._on_clicked)
        layout.addWidget(self._tree)

        self._placeholder = QLabel("  无可显示的大纲\n  打开一个 Python 文件")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color: gray; padding: 16px;")
        layout.addWidget(self._placeholder)
        self._placeholder.hide()

        self._empty()

    def _empty(self):
        self._tree.clear()
        self._tree.hide()
        self._placeholder.show()

    def refresh(self):
        editor = self._mw._current_editor()
        if editor is None:
            self._empty()
            return
        path = getattr(editor, "file_path", None) or ""
        if not path.lower().endswith(".py"):
            self._empty()
            return
        text = editor.text()
        self._tree.clear()
        self._placeholder.hide()
        self._tree.show()

        stack = []   # (depth, QTreeWidgetItem)
        for i, line in enumerate(text.splitlines()):
            m = _SYMBOL_RE.match(line)
            if not m:
                continue
            indent = len(m.group(1))
            depth = indent // 4
            kind = m.group(2).replace("async ", "")
            name = m.group(3)
            label = f"{name}()" if kind == "def" else name

            while stack and stack[-1][0] >= depth:
                stack.pop()

            item = QTreeWidgetItem([f"{kind} {label}"])
            item.setData(0, Qt.UserRole, (i, indent))
            if stack:
                stack[-1][1].addChild(item)
            else:
                self._tree.addTopLevelItem(item)
            stack.append((depth, item))

        self._tree.expandAll()
        if self._tree.topLevelItemCount() == 0:
            self._empty()

    def _on_clicked(self, item, _col):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        line, col = data
        editor = self._mw._current_editor()
        if editor is None:
            return
        editor.setCursorPosition(line, col)
        editor.ensureLineVisible(line)
        editor.setFocus()
