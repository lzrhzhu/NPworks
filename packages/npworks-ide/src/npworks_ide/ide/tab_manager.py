import os

from PyQt5.QtWidgets import QTabWidget, QMessageBox

from npworks_ide.ide.editor import CodeEditor


_UNTITLED = "未命名"


class TabManager:
    def __init__(self, tab_widget: QTabWidget, on_tab_changed_cb=None):
        self._tabs = tab_widget
        self._new_file_counter = 0
        self._on_tab_changed_cb = on_tab_changed_cb

        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.tabCloseRequested.connect(self.close_tab)
        self._tabs.currentChanged.connect(self._on_tab_changed)

    @property
    def widget(self):
        return self._tabs

    def current_editor(self) -> CodeEditor:
        return self._tabs.currentWidget()

    def count(self):
        return self._tabs.count()

    def add_welcome_tab(self):
        editor = CodeEditor(self._tabs)
        editor.tab_title = _UNTITLED
        editor.file_path = None
        self._tabs.addTab(editor, _UNTITLED)
        self._tabs.setCurrentWidget(editor)

    def add_editor_tab(self, title, code, original=None, file_path=None):
        editor = CodeEditor(self._tabs)
        editor.tab_title = title
        editor.file_path = file_path
        editor.set_code(code, original if original is not None else code)
        idx = self._tabs.addTab(editor, title)
        self._tabs.setCurrentIndex(idx)
        editor.setFocus()
        return editor

    def close_tab(self, index):
        editor = self._tabs.widget(index)
        self._tabs.removeTab(index)
        editor.deleteLater()

    def find_tab_by_path(self, file_path: str):
        norm = os.path.normpath(file_path)
        for i in range(self._tabs.count()):
            editor = self._tabs.widget(i)
            if editor.file_path and os.path.normpath(editor.file_path) == norm:
                return i, editor
        return -1, None

    def switch_to_tab(self, index):
        self._tabs.setCurrentIndex(index)

    def new_file(self):
        self._new_file_counter += 1
        title = f"{_UNTITLED}_{self._new_file_counter}"
        return self.add_editor_tab(title, "")

    def _on_tab_changed(self, index):
        if self._on_tab_changed_cb:
            self._on_tab_changed_cb(index)
