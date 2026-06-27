import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QMessageBox, QMenu, QInputDialog

from npworks_ide.ide.widgets.editor import CodeEditor


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
        self._tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tabs.customContextMenuRequested.connect(self._on_tab_context_menu)

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
        widget = self._tabs.widget(index)
        from npworks_ide.ide.plugin.editor_registry import EditorView

        if isinstance(widget, EditorView) and widget.is_modified():
            title = widget.editor_title()
            reply = QMessageBox.question(
                self._tabs,
                "关闭未保存文件",
                f"文件 \"{title}\" 已修改但未保存。\n是否保存？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                if not widget.save():
                    return
            elif reply == QMessageBox.Cancel:
                return

        if isinstance(widget, EditorView):
            widget.cleanup()

        self._tabs.removeTab(index)
        widget.deleteLater()

    def close_other_tabs(self, index):
        for i in range(self._tabs.count() - 1, -1, -1):
            if i != index:
                widget = self._tabs.widget(i)
                self._tabs.removeTab(i)
                widget.deleteLater()

    def close_all_tabs(self):
        for i in range(self._tabs.count() - 1, -1, -1):
            widget = self._tabs.widget(i)
            self._tabs.removeTab(i)
            widget.deleteLater()

    def _on_tab_context_menu(self, pos):
        index = self._tabs.tabBar().tabAt(pos)
        if index < 0:
            return
        menu = QMenu(self._tabs)
        close_action = menu.addAction("关闭")
        close_others_action = menu.addAction("关闭其他")
        close_all_action = menu.addAction("关闭全部")
        action = menu.exec_(self._tabs.mapToGlobal(pos))
        if action == close_action:
            self.close_tab(index)
        elif action == close_others_action:
            self.close_other_tabs(index)
        elif action == close_all_action:
            self.close_all_tabs()

    def find_tab_by_path(self, file_path: str):
        norm = os.path.normpath(file_path)
        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            fp = getattr(widget, "file_path", None)
            if fp and os.path.normpath(fp) == norm:
                return i, widget
        return -1, None

    def switch_to_tab(self, index):
        self._tabs.setCurrentIndex(index)

    def new_file(self):
        self._new_file_counter += 1
        title = f"{_UNTITLED}_{self._new_file_counter}"
        return self.add_editor_tab(title, "")

    def go_to_line(self):
        max_line = 1
        widget = self._tabs.currentWidget()
        if isinstance(widget, CodeEditor):
            max_line = widget.lines()
        elif hasattr(widget, 'get_editor'):
            max_line = widget.get_editor().lines()
        line, ok = QInputDialog.getInt(
            self._tabs, "跳转到行", f"行号 (1-{max_line}):", 1, 1, max_line,
        )
        if ok:
            editor = None
            if isinstance(widget, CodeEditor):
                editor = widget
            elif hasattr(widget, 'get_editor'):
                editor = widget.get_editor()
            if editor:
                editor.setCursorPosition(line - 1, 0)
                editor.ensureLineVisible(line - 1)
                editor.setFocus()

    def _on_tab_changed(self, index):
        if self._on_tab_changed_cb:
            self._on_tab_changed_cb(index)
