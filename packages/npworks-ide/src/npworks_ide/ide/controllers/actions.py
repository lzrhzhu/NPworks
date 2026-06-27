import os

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAction

_MAX_RECENT = 10


class ActionManager:
    def __init__(self, main_window, tab_manager, file_tree, output_panel, executor):
        self._main_window = main_window
        self._tabs = tab_manager
        self._file_tree = file_tree
        self._output = output_panel
        self._executor = executor
        self._settings = QSettings("npworks", "npworks")
        self._recent_actions = []
        self._recent_menu = None
        self._recent_folder_actions = []
        self._recent_folders_menu = None

    def new_file(self):
        self._tabs.new_file()

    def _default_open_dir(self):
        """上一次使用的目录；用于打开文件/文件夹对话框的起始目录。"""
        last = self._settings.value("last_dir", "")
        if last and os.path.isdir(last):
            return last
        folders = self._settings.value("recent_folders", [])
        if isinstance(folders, str):
            folders = [folders]
        for f in folders:
            if f and os.path.isdir(f):
                return f
        for f in self._file_tree.get_open_folders():
            if os.path.isdir(f):
                return f
        d = os.path.expanduser("~/npworks")
        os.makedirs(d, exist_ok=True)
        return d

    def open_file(self):
        default_dir = self._default_open_dir()
        paths, _ = QFileDialog.getOpenFileNames(
            self._main_window, "打开文件", default_dir, "Python 文件 (*.py);;Markdown (*.md);;CSV 表格 (*.csv *.tsv);;PDF (*.pdf);;图片 (*.png *.jpg *.bmp *.gif);;所有文件 (*)"
        )
        for path in paths:
            self._open_file_by_path(path)

    def open_file_by_path(self, path):
        self._main_window._open_file_by_path(path)

    def _open_file_by_path(self, path):
        # 统一走注册表（与菜单/文件树一致），保证 .md/.pdf/.csv 等由对应插件渲染
        self._main_window._open_file_by_path(path)

    def save_code(self):
        from npworks_ide.ide.plugin.editor_registry import EditorView
        widget = self._tabs.widget.currentWidget()
        if not isinstance(widget, EditorView) or widget.is_readonly():
            return
        if widget.file_path:
            if widget.save():
                self._output.append_system(f"已保存到: {widget.file_path}")
            else:
                QMessageBox.warning(self._main_window, "保存失败", "无法保存文件")
        else:
            self.save_as()

    def save_as(self):
        widget = self._tabs.widget.currentWidget()
        if hasattr(widget, "get_editor"):
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
        from npworks_ide.ide.plugin.editor_registry import EditorView
        for i in range(self._tabs.widget.count()):
            widget = self._tabs.widget.widget(i)
            if (isinstance(widget, EditorView)
                    and not widget.is_readonly()
                    and widget.is_modified()):
                if widget.file_path and widget.save():
                    self._output.append_system(f"已保存到: {widget.file_path}")

    def open_folder(self):
        path = QFileDialog.getExistingDirectory(
            self._main_window, "打开文件夹", self._default_open_dir()
        )
        if not path:
            return
        self._settings.setValue("last_dir", path)
        self._add_recent_folder(path)
        if self._file_tree.is_content_source_dir(path):
            self._file_tree.focus_textbook_root()
            return
        self._file_tree.add_root(path)
        self._save_open_folders()

    def open_folder_path(self, path):
        """打开一个历史记录中的文件夹。"""
        if not path or not os.path.isdir(path):
            return
        self._settings.setValue("last_dir", path)
        self._add_recent_folder(path)
        if self._file_tree.is_content_source_dir(path):
            self._file_tree.focus_textbook_root()
            return
        self._file_tree.add_root(path)
        self._save_open_folders()

    def close_current_folder(self):
        self._file_tree.close_selected_root()
        self._save_open_folders()

    def save_open_folders(self):
        self._save_open_folders()

    def _save_open_folders(self):
        folders = [f for f in self._file_tree.get_open_folders()
                   if not self._file_tree.is_content_source_dir(f)]
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

    def _add_recent_folder(self, path):
        path = os.path.normpath(path)
        folders = self._settings.value("recent_folders", [])
        if isinstance(folders, str):
            folders = [folders]
        folders = [f for f in folders if os.path.normpath(f) != path]
        folders.insert(0, path)
        folders = folders[:_MAX_RECENT]
        self._settings.setValue("recent_folders", folders)
        self._update_recent_folders_menu()

    def update_recent_folders_menu(self):
        self._update_recent_folders_menu()

    def _update_recent_folders_menu(self):
        if self._recent_folders_menu is None:
            return
        self._recent_folders_menu.clear()
        self._recent_folder_actions.clear()
        folders = self._settings.value("recent_folders", [])
        if isinstance(folders, str):
            folders = [folders]
        for path in folders:
            if not os.path.isdir(path):
                continue
            action = QAction(os.path.basename(path), self._main_window)
            action.setToolTip(path)
            action.setData(path)
            action.triggered.connect(self._open_recent_folder)
            self._recent_folders_menu.addAction(action)
            self._recent_folder_actions.append(action)

    def _open_recent_folder(self):
        action = self._main_window.sender()
        if not action:
            return
        path = action.data()
        if not path:
            return
        if not os.path.isdir(path):
            QMessageBox.warning(self._main_window, "文件夹不存在", path)
            return
        self.open_folder_path(path)

    def set_recent_menu(self, menu):
        self._recent_menu = menu
        self._update_recent_menu()

    def set_recent_folders_menu(self, menu):
        self._recent_folders_menu = menu
        self._update_recent_folders_menu()
