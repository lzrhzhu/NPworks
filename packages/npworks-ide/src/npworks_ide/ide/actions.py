import os

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAction

from npworks_ide.ide.preview_markdown import MarkdownSplitView

_MAX_RECENT = 10


class ActionManager:
    def __init__(self, main_window, tab_manager, file_tree, output_panel, executor, bottom_panel):
        self._main_window = main_window
        self._tabs = tab_manager
        self._file_tree = file_tree
        self._output = output_panel
        self._executor = executor
        self._bottom = bottom_panel
        self._settings = QSettings("npworks", "npworks")
        self._recent_actions = []
        self._recent_menu = None

    def new_file(self):
        self._tabs.new_file()

    def open_file(self):
        default_dir = os.path.expanduser("~/npworks")
        os.makedirs(default_dir, exist_ok=True)
        paths, _ = QFileDialog.getOpenFileNames(
            self._main_window, "打开文件", default_dir, "Python 文件 (*.py);;Markdown (*.md);;PDF (*.pdf);;图片 (*.png *.jpg *.bmp *.gif);;所有文件 (*)"
        )
        for path in paths:
            self._open_file_by_path(path)

    def open_file_by_path(self, path):
        self._open_file_by_path(path)

    def _open_file_by_path(self, path):
        if not path or not os.path.isfile(path):
            return
        idx, existing = self._tabs.find_tab_by_path(path)
        if existing:
            self._tabs.switch_to_tab(idx)
            existing.setFocus()
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            title = os.path.basename(path)
            editor = self._tabs.add_editor_tab(title, code, code, file_path=path)
            editor.file_dropped.connect(self._open_file_by_path)
            self._add_recent_file(path)
        except Exception as e:
            QMessageBox.warning(self._main_window, "打开失败", str(e))

    def save_code(self):
        widget = self._tabs.widget.currentWidget()
        if isinstance(widget, MarkdownSplitView):
            if widget.save_content():
                self._output.append_system(f"已保存到: {widget.file_path}")
            else:
                QMessageBox.warning(self._main_window, "保存失败", "无法保存文件")
            return
        editor = self._tabs.current_editor()
        if not editor:
            return
        if editor.file_path:
            try:
                with open(editor.file_path, "w", encoding="utf-8") as f:
                    f.write(editor.get_code())
                editor.setModified(False)
                self._output.append_system(f"已保存到: {editor.file_path}")
            except Exception as e:
                QMessageBox.warning(self._main_window, "保存失败", str(e))
        else:
            self.save_as()

    def save_as(self):
        widget = self._tabs.widget.currentWidget()
        if isinstance(widget, MarkdownSplitView):
            editor = widget.get_editor()
            default_dir = os.path.expanduser("~/npworks")
            os.makedirs(default_dir, exist_ok=True)
            filename = os.path.basename(widget.file_path) if widget.file_path else "untitled.md"
            default_path = os.path.join(default_dir, filename)
            path, _ = QFileDialog.getSaveFileName(
                self._main_window, "另存为", default_path, "Markdown (*.md);;所有文件 (*)"
            )
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(editor.text())
                    widget._path = path
                    editor.setModified(False)
                    self._add_recent_file(path)
                    self._output.append_system(f"已保存到: {path}")
                except Exception as e:
                    QMessageBox.warning(self._main_window, "保存失败", str(e))
            return
        editor = self._tabs.current_editor()
        if not editor:
            return
        default_dir = os.path.expanduser("~/npworks")
        os.makedirs(default_dir, exist_ok=True)
        filename = "untitled.py"
        if editor.file_path:
            filename = os.path.basename(editor.file_path)
        default_path = os.path.join(default_dir, filename)
        path, _ = QFileDialog.getSaveFileName(
            self._main_window, "另存为", default_path, "Python 文件 (*.py);;所有文件 (*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(editor.get_code())
                editor.file_path = path
                editor.tab_title = os.path.basename(path)
                idx = self._tabs.widget.indexOf(editor)
                self._tabs.widget.setTabText(idx, editor.tab_title)
                editor.setModified(False)
                self._add_recent_file(path)
                self._output.append_system(f"已保存到: {path}")
            except Exception as e:
                QMessageBox.warning(self._main_window, "保存失败", str(e))

    def save_all(self):
        from npworks_ide.ide.editor import CodeEditor
        for i in range(self._tabs.widget.count()):
            widget = self._tabs.widget.widget(i)
            if isinstance(widget, MarkdownSplitView):
                editor = widget.get_editor()
                if editor and editor.isModified():
                    if widget.save_content():
                        self._output.append_system(f"已保存到: {widget.file_path}")
                    continue
            if isinstance(widget, CodeEditor) and widget.isModified():
                if widget.file_path:
                    try:
                        with open(widget.file_path, "w", encoding="utf-8") as f:
                            f.write(widget.get_code())
                        widget.setModified(False)
                        self._output.append_system(f"已保存到: {widget.file_path}")
                    except Exception as e:
                        QMessageBox.warning(self._main_window, "保存失败", str(e))

    def open_folder(self):
        path = QFileDialog.getExistingDirectory(
            self._main_window, "打开文件夹", os.path.expanduser("~")
        )
        if path:
            self._file_tree.add_root(path)
            self._save_open_folders()

    def close_current_folder(self):
        self._file_tree.close_selected_root()
        self._save_open_folders()

    def save_open_folders(self):
        self._save_open_folders()

    def _save_open_folders(self):
        folders = self._file_tree.get_open_folders()
        self._settings.setValue("open_folders", folders)

    def add_recent_file(self, path):
        self._add_recent_file(path)

    def _add_recent_file(self, path):
        recents = self._settings.value("recent_files", [])
        if isinstance(recents, str):
            recents = [recents]
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        recents = recents[:_MAX_RECENT]
        self._settings.setValue("recent_files", recents)
        self._update_recent_menu()

    def update_recent_menu(self):
        self._update_recent_menu()

    def _update_recent_menu(self):
        if self._recent_menu is None:
            return
        self._recent_menu.clear()
        self._recent_actions.clear()
        recents = self._settings.value("recent_files", [])
        if isinstance(recents, str):
            recents = [recents]
        for path in recents:
            action = QAction(os.path.basename(path), self._main_window)
            action.setToolTip(path)
            action.setData(path)
            action.triggered.connect(self._open_recent_file)
            self._recent_menu.addAction(action)
            self._recent_actions.append(action)

    def _open_recent_file(self):
        action = self._main_window.sender()
        if not action:
            return
        path = action.data()
        if not path:
            return
        if not os.path.isfile(path):
            QMessageBox.warning(self._main_window, "文件不存在", path)
            return
        self._open_file_by_path(path)

    def set_recent_menu(self, menu):
        self._recent_menu = menu
        self._update_recent_menu()
