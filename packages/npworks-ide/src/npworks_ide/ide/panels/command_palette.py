"""命令面板（Ctrl+Shift+P）与快速打开（Ctrl+P）。

VS Code 风格：一个输入框 + 列表，实时过滤；回车执行命令或打开文件。
"""
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
)


class CommandPalette(QDialog):
    def __init__(self, main_window, mode="commands", parent=None):
        super().__init__(parent)
        self._mw = main_window
        self._mode = mode
        self.setWindowTitle("命令面板" if mode == "commands" else "转到文件")
        self.setModal(True)
        self.resize(520, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(
            "输入命令名筛选…" if mode == "commands" else "输入文件名筛选…")
        self._edit.textChanged.connect(self._filter)
        self._edit.returnPressed.connect(self._activate)
        layout.addWidget(self._edit)

        self._list = QListWidget()
        self._list.itemActivated.connect(lambda _i: self._activate())
        layout.addWidget(self._list)

        if mode == "commands":
            self._entries = self._mw._palette_commands()
        else:
            self._entries = self._mw._palette_files()
        self._populate("")

        self._edit.setFocus()

    def _populate(self, query):
        self._list.clear()
        q = query.strip().lower()
        shown = 0
        for entry in self._entries:
            label = entry[0]
            if q and q not in label.lower():
                continue
            it = QListWidgetItem(label)
            it.setData(Qt.UserRole, entry)
            self._list.addItem(it)
            shown += 1
            if shown >= 200:
                break
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _filter(self, text):
        self._populate(text)

    def _activate(self):
        items = self._list.selectedItems()
        if not items:
            if self._list.count() > 0:
                items = [self._list.item(0)]
            else:
                return
        entry = items[0].data(Qt.UserRole)
        if entry is None:
            return
        self.accept()
        payload = entry[1]
        if self._mode == "commands":
            try:
                payload()
            except Exception:
                pass
        else:
            self._mw._open_file_by_path(payload)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
            return
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            self._list.keyPressEvent(event)
            return
        super().keyPressEvent(event)
