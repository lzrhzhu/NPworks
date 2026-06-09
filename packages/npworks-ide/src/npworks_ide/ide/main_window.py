import sys
import os

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox,
    QTabWidget, QLabel, QWidget,
    QVBoxLayout,
)

from npworks_ide.ide.activity_bar import ActivityBar
from npworks_ide.ide.file_tree import FileTree
from npworks_ide.ide.editor import CodeEditor
from npworks_ide.ide.output_panel import OutputPanel
from npworks_ide.ide.find_replace import FindReplacePanel
from npworks_ide.ide.sidebar import Sidebar
from npworks_ide.ide.bottom_panel import BottomPanel
from npworks_ide.ide.tab_manager import TabManager
from npworks_ide.ide.actions import ActionManager
from npworks_ide.ide.menu_builder import MenuBuilder
from npworks_ide.ide.run_controller import RunController
from npworks_ide.ide.find_controller import FindController
from npworks_ide.ide.edit_controller import EditController
from npworks_ide.ide.theme_controller import ThemeController
from npworks_ide.ide.preview_image import is_image_file, ImagePreview
from npworks_ide.ide.preview_markdown import is_markdown_file, MarkdownSplitView
from npworks_ide.ide.preview_pdf import is_pdf_file, PdfPreview
from npworks_ide.runner.executor import Executor, _RC_LINE_COUNT

import npworks_content

_IDX_EXPLORER = 0
_IDX_OUTLINE = 1

_SIDEBAR_WIDTH = 260


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPworks")
        self.resize(1280, 860)

        self._settings = QSettings("npworks", "npworks")
        self._restore_geometry()

        self.executor = Executor(self)
        self.file_tree = FileTree(self)
        self.output_panel = OutputPanel(self)
        self.find_replace = FindReplacePanel(self)
        self.activity_bar = ActivityBar(self)

        self._bottom_panel = BottomPanel(self.output_panel, self)

        self._tab_widget = QTabWidget()
        self._tabs = TabManager(self._tab_widget, on_tab_changed_cb=self._on_tab_changed)

        self._actions = ActionManager(
            self, self._tabs, self.file_tree, self.output_panel,
            self.executor, self._bottom_panel,
        )

        self.run_ctrl = RunController(
            self, self.executor, self.output_panel, self._bottom_panel,
        )
        self._bottom_panel.set_factories(self.run_ctrl.create_terminal, self.run_ctrl.create_shell)

        self.find_ctrl = FindController(self, self.find_replace)
        self.edit_ctrl = EditController(self)
        self.theme_ctrl = ThemeController(
            self, self._tab_widget, self._bottom_panel, self._settings,
        )

        self._setup_layout()
        self._build_status_bar()
        self._connect_signals()

        self._menu_builder = MenuBuilder(self)
        theme_actions = self._menu_builder.build_menu_bar()
        self.theme_ctrl.set_theme_actions(theme_actions)

        self._setup_activity_bar()
        self._init_file_tree()

        self._restore_layout()

    def _setup_layout(self):
        self._outline_placeholder = QLabel("\n\n    大纲视图\n    （开发中）")
        self._outline_placeholder.setObjectName("outline_placeholder")
        self._outline_placeholder.setAlignment(Qt.AlignCenter)

        self._sidebar1 = Sidebar(self.file_tree, "文件浏览器")
        self._sidebar1.setObjectName("sidebar_left")
        self._sidebar1.setMinimumWidth(0)

        self._sidebar2 = Sidebar(self._outline_placeholder, "大纲")
        self._sidebar2.setObjectName("sidebar_right")
        self._sidebar2.setMinimumWidth(0)

        self._activity_container = QWidget()
        self._activity_container.setObjectName("activity_bar_container")
        self._activity_container.setMinimumWidth(48)
        self._activity_container.setMaximumWidth(48)
        ac_layout = QVBoxLayout(self._activity_container)
        ac_layout.setContentsMargins(0, 0, 0, 0)
        ac_layout.setSpacing(0)
        ac_layout.addWidget(self.activity_bar)

        self._editor_area = QWidget()
        editor_layout = QVBoxLayout(self._editor_area)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.find_replace)
        self.find_replace.hide()
        editor_layout.addWidget(self._tab_widget)

        self._h_splitter = QSplitter(Qt.Horizontal)
        self._h_splitter.setObjectName("h_splitter")
        self._h_splitter.addWidget(self._activity_container)
        self._h_splitter.addWidget(self._sidebar1)
        self._h_splitter.addWidget(self._editor_area)
        self._h_splitter.addWidget(self._sidebar2)
        self._h_splitter.setStretchFactor(0, 0)
        self._h_splitter.setStretchFactor(1, 0)
        self._h_splitter.setStretchFactor(2, 1)
        self._h_splitter.setStretchFactor(3, 0)
        self._h_splitter.setHandleWidth(1)
        self._h_splitter.setSizes([48, _SIDEBAR_WIDTH, 800, 0])

        self._v_splitter = QSplitter(Qt.Vertical)
        self._v_splitter.setObjectName("v_splitter")
        self._v_splitter.addWidget(self._h_splitter)
        self._v_splitter.addWidget(self._bottom_panel)
        self._v_splitter.setStretchFactor(0, 1)
        self._v_splitter.setStretchFactor(1, 0)
        self._v_splitter.setSizes([700, 200])

        self.setCentralWidget(self._v_splitter)

    def _setup_activity_bar(self):
        self.activity_bar.add_button("📁", "文件浏览器")
        self.activity_bar.add_button("📋", "大纲")
        self.activity_bar.add_button("⚙", "设置", bottom=True)
        self.activity_bar.set_checked(0)

    def _show_sidebar1(self, show=True):
        sizes = self._h_splitter.sizes()
        if show:
            if sizes[1] < 50:
                sizes[1] = _SIDEBAR_WIDTH
                self._h_splitter.setSizes(sizes)
        else:
            sizes[1] = 0
            self._h_splitter.setSizes(sizes)

    def _show_sidebar2(self, show=True):
        sizes = self._h_splitter.sizes()
        if show:
            if sizes[3] < 50:
                sizes[3] = _SIDEBAR_WIDTH
                self._h_splitter.setSizes(sizes)
        else:
            sizes[3] = 0
            self._h_splitter.setSizes(sizes)

    def _is_sidebar1_visible(self):
        return self._h_splitter.sizes()[1] > 50

    def _is_sidebar2_visible(self):
        return self._h_splitter.sizes()[3] > 50

    def _build_status_bar(self):
        sb = self.statusBar()
        sb.setStyleSheet("QStatusBar { border: none; }")

        sep_style = "color: rgba(255,255,255,80); font-size: 12px;"

        self._run_label = QLabel("")
        self._run_label.setFont(QFont("Segoe UI", 9))
        sb.addWidget(self._run_label)

        sep1 = QLabel("|")
        sep1.setStyleSheet(sep_style)
        sb.addWidget(sep1)

        self._pos_label = QLabel(" 行 1, 列 1 ")
        self._pos_label.setFont(QFont("Consolas", 9))
        sb.addPermanentWidget(self._pos_label)

        sep2 = QLabel("|")
        sep2.setStyleSheet(sep_style)
        sb.addPermanentWidget(sep2)

        self._encoding_label = QLabel(" UTF-8 ")
        self._encoding_label.setFont(QFont("Consolas", 9))
        sb.addPermanentWidget(self._encoding_label)

        sep3 = QLabel("|")
        sep3.setStyleSheet(sep_style)
        sb.addPermanentWidget(sep3)

        py_ver = f" Python {sys.version.split()[0]} "
        py_label = QLabel(py_ver)
        py_label.setFont(QFont("Consolas", 9))
        sb.addPermanentWidget(py_label)

    def _connect_signals(self):
        self.activity_bar.button_clicked.connect(self._on_activity_clicked)
        self.file_tree.file_selected.connect(self._on_file_selected)
        self.file_tree.open_folder_requested.connect(self._actions.open_folder)
        self.file_tree.file_renamed.connect(self._on_file_renamed)
        self.file_tree.file_deleted.connect(self._on_file_deleted)
        self.executor.stdout_ready.connect(self.output_panel.append_stdout)
        self.executor.stderr_ready.connect(self.output_panel.append_stderr)
        self.executor.execution_started.connect(self.run_ctrl.on_execution_started)
        self.executor.execution_finished.connect(self.run_ctrl.on_execution_finished)

        self.output_panel.input_submitted.connect(self.run_ctrl.send_input)
        self.output_panel.jump_to_line.connect(self._on_jump_to_line)

        self.find_replace.find_next_btn.clicked.connect(self.find_ctrl.find_next)
        self.find_replace.find_prev_btn.clicked.connect(self.find_ctrl.find_prev)
        self.find_replace.replace_btn.clicked.connect(self.find_ctrl.replace_one)
        self.find_replace.replace_all_btn.clicked.connect(self.find_ctrl.replace_all)
        self.find_replace.closed.connect(self.find_ctrl.clear_find_highlight)

    def _on_activity_clicked(self, index: int):
        if index == _IDX_EXPLORER:
            self._show_sidebar1(not self._is_sidebar1_visible())
        elif index == _IDX_OUTLINE:
            self._show_sidebar2(not self._is_sidebar2_visible())

    def _toggle_explorer(self):
        vis = not self._is_sidebar1_visible()
        self._show_sidebar1(vis)
        self.activity_bar.set_checked(_IDX_EXPLORER if vis else -1)

    def _toggle_outline(self):
        vis = not self._is_sidebar2_visible()
        self._show_sidebar2(vis)
        self.activity_bar.set_checked(_IDX_OUTLINE if vis else -1)

    def _toggle_bottom_panel(self):
        vis = self._bottom_panel.isVisible()
        self._bottom_panel.setVisible(not vis)

    def _current_editor(self) -> CodeEditor:
        widget = self._tab_widget.currentWidget()
        if isinstance(widget, MarkdownSplitView):
            return widget.get_editor()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def _init_file_tree(self):
        self.file_tree.init_textbook()
        saved_folders = self._settings.value("open_folders", [])
        if isinstance(saved_folders, str):
            saved_folders = [saved_folders]
        for folder in saved_folders:
            if os.path.isdir(folder):
                self.file_tree.add_root(folder)
        if self.file_tree.root_count() > 0:
            self.file_tree.expand_first_root()

    def _on_tab_changed(self, index):
        widget = self._tab_widget.currentWidget()
        if isinstance(widget, MarkdownSplitView):
            editor = widget.get_editor()
            editor.setFocus()
            if widget.file_path:
                self.file_tree.select_file(widget.file_path)
        elif isinstance(widget, CodeEditor):
            self._update_status_pos()
            widget.setFocus()
            if widget.file_path:
                self.file_tree.select_file(widget.file_path)
            else:
                self.file_tree.clear_tree_selection()
        elif widget:
            widget.setFocus()

    def _on_file_selected(self, file_path: str):
        self._open_file_by_path(file_path)

    def _new_file(self):
        editor = self._tabs.new_file()
        editor.cursorPositionChanged.connect(self._update_status_pos)
        editor.file_dropped.connect(self._open_file_by_path)
        editor.modificationChanged.connect(lambda m, e=editor: self._on_modification_changed(e, m))

    def _open_file(self):
        default_dir = os.path.expanduser("~/npworks")
        os.makedirs(default_dir, exist_ok=True)
        paths, _ = QFileDialog.getOpenFileNames(
            self, "打开文件", default_dir, "Python 文件 (*.py);;Markdown (*.md);;PDF (*.pdf);;图片 (*.png *.jpg *.bmp *.gif);;所有文件 (*)"
        )
        for path in paths:
            self._open_file_by_path(path)

    def _open_folder(self):
        self._actions.open_folder()

    def _close_current_folder(self):
        self._actions.close_current_folder()

    def _save_code(self):
        self._actions.save_code()

    def _save_as(self):
        self._actions.save_as()

    def _save_all(self):
        self._actions.save_all()

    def _open_file_by_path(self, path):
        if not path or not os.path.isfile(path):
            return
        idx, existing = self._tabs.find_tab_by_path(path)
        if existing:
            self._tabs.switch_to_tab(idx)
            existing.setFocus()
            return

        title = os.path.basename(path)

        if is_image_file(path):
            try:
                preview = ImagePreview(path, self)
                idx = self._tab_widget.addTab(preview, f"\U0001F5BC {title}")
                self._tab_widget.setCurrentIndex(idx)
                self._actions.add_recent_file(path)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", str(e))
            return

        if is_pdf_file(path):
            try:
                preview = PdfPreview(path, self)
                idx = self._tab_widget.addTab(preview, f"\U0001F4D1 {title}")
                self._tab_widget.setCurrentIndex(idx)
                self._actions.add_recent_file(path)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", str(e))
            return

        if is_markdown_file(path):
            try:
                split_view = MarkdownSplitView(path, self)
                idx = self._tab_widget.addTab(split_view, f"\U0001F4C4 {title}")
                self._tab_widget.setCurrentIndex(idx)
                self._actions.add_recent_file(path)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", str(e))
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            _, ext = os.path.splitext(path)
            if ext.lower() == ".py":
                tab_title = f"Py {title}"
            else:
                tab_title = title
            editor = self._tabs.add_editor_tab(tab_title, code, code, file_path=path)
            editor.cursorPositionChanged.connect(self._update_status_pos)
            editor.file_dropped.connect(self._open_file_by_path)
            editor.modificationChanged.connect(lambda m, e=editor: self._on_modification_changed(e, m))
            self._actions.add_recent_file(path)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", str(e))

    def _close_tab(self):
        idx = self._tab_widget.currentIndex()
        if idx >= 0:
            self._tabs.close_tab(idx)

    def _go_to_line(self):
        self._tabs.go_to_line()

    def _show_find(self):
        self.find_replace.show_find()

    def _show_replace(self):
        self.find_replace.show_replace()

    def _show_about(self):
        from npworks_ide import __version__
        QMessageBox.about(
            self, "关于 NPworks",
            f"<h2>NPworks</h2>"
            f"<p style='color: #666;'>计算物理交互式教材</p>"
            f"<hr>"
            f"<p><b>版本:</b> {__version__}</p>"
            f"<p><b>Python:</b> {sys.version.split()[0]}</p>"
            f"<p><b>Qt:</b> PyQt5</p>"
            f"<br>"
            f"<p style='color: #888;'>基于 PyQt5 构建的交互式物理计算学习环境</p>"
        )

    def _update_status_pos(self):
        editor = self._current_editor()
        if not editor:
            return
        line, col = editor.getCursorPosition()
        self._pos_label.setText(f" 行 {line + 1}, 列 {col + 1} ")

    def _on_jump_to_line(self, traceback_line: int):
        editor = self._current_editor()
        if not editor:
            return
        target = traceback_line - _RC_LINE_COUNT - 1
        if target < 0:
            target = 0
        editor.setCursorPosition(target, 0)
        editor.ensureLineVisible(target)
        editor.setFocus()

    def _on_modification_changed(self, editor, modified):
        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            editor_match = (widget is editor) or (
                isinstance(widget, MarkdownSplitView) and widget.get_editor() is editor)
            if editor_match:
                base = editor.tab_title
                self._tab_widget.setTabText(i, f"{'*' if modified else ''}{base}")
                return

    def _on_file_renamed(self, old_path, new_path):
        norm_old = os.path.normpath(old_path)
        norm_new = os.path.normpath(new_path)
        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            fp = getattr(widget, "file_path", None)
            if fp and os.path.normpath(fp) == norm_old:
                widget.file_path = norm_new
                title = os.path.basename(norm_new)
                if hasattr(widget, "tab_title"):
                    widget.tab_title = title
                self._tab_widget.setTabText(i, title)

    def _on_file_deleted(self, path):
        norm = os.path.normpath(path)
        tabs_to_close = []
        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            fp = getattr(widget, "file_path", None)
            if not fp:
                continue
            norm_fp = os.path.normpath(fp)
            if norm_fp == norm or norm_fp.startswith(norm + os.sep):
                tabs_to_close.append(i)
        for i in reversed(tabs_to_close):
            widget = self._tab_widget.widget(i)
            self._tab_widget.removeTab(i)
            widget.deleteLater()

    def _restore_geometry(self):
        size = self._settings.value("window_size")
        if size:
            self.resize(size)
        pos = self._settings.value("window_pos")
        if pos:
            self.move(pos)

    def _restore_layout(self):
        h_sizes = self._settings.value("h_splitter_sizes")
        v_sizes = self._settings.value("v_splitter_sizes")
        if h_sizes:
            self._h_splitter.setSizes([int(s) for s in h_sizes])
        if v_sizes:
            self._v_splitter.setSizes([int(s) for s in v_sizes])

    def closeEvent(self, event):
        self._settings.setValue("window_size", self.size())
        self._settings.setValue("window_pos", self.pos())
        self._settings.setValue("h_splitter_sizes", self._h_splitter.sizes())
        self._settings.setValue("v_splitter_sizes", self._v_splitter.sizes())
        self._actions.save_open_folders()
        self.run_ctrl.cleanup()
        super().closeEvent(event)
