import sys
import os
from datetime import datetime

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox,
    QTabWidget, QMenu, QAction, QLabel, QWidget,
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
from npworks_ide.ide.theme import apply_theme
from npworks_ide.ide.preview_image import is_image_file, ImagePreview
from npworks_ide.ide.preview_markdown import is_markdown_file, MarkdownPreview
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
        self.terminal = None
        self.shell_terminal = None
        self.find_replace = FindReplacePanel(self)
        self.activity_bar = ActivityBar(self)

        self._bottom_panel = BottomPanel(self.output_panel, self)
        self._bottom_panel.set_factories(self._create_terminal, self._create_shell)

        self._tab_widget = QTabWidget()
        self._tabs = TabManager(self._tab_widget, on_tab_changed_cb=self._on_tab_changed)

        self._actions = ActionManager(
            self, self._tabs, self.file_tree, self.output_panel,
            self.executor, self._bottom_panel,
        )

        self._setup_layout()
        self._build_menu_bar()
        self._build_status_bar()
        self._connect_signals()

        self._start_time = None

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

    def _build_menu_bar(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("文件(&F)")
        self._add_action(file_menu, "新建(&N)", self._new_file, QKeySequence.New)
        self._add_action(file_menu, "打开(&O)...", self._open_file, QKeySequence.Open)
        self._add_action(file_menu, "打开文件夹(&F)...", self._open_folder)
        recent_menu = file_menu.addMenu("最近文件(&R)")
        self._actions.set_recent_menu(recent_menu)
        file_menu.addSeparator()
        self._add_action(file_menu, "关闭文件夹(&W)", self._close_current_folder)
        file_menu.addSeparator()
        self._add_action(file_menu, "保存(&S)", self._save_code, QKeySequence.Save)
        self._add_action(file_menu, "另存为(&A)...", self._save_as, QKeySequence.SaveAs)
        file_menu.addSeparator()
        self._add_action(file_menu, "退出(&Q)", self.close, QKeySequence.Quit)

        edit_menu = mb.addMenu("编辑(&E)")
        self._add_action(edit_menu, "撤销(&U)", self._undo, QKeySequence.Undo)
        self._add_action(edit_menu, "重做(&R)", self._redo, QKeySequence.Redo)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "剪切(&X)", self._cut, QKeySequence.Cut)
        self._add_action(edit_menu, "复制(&C)", self._copy, QKeySequence.Copy)
        self._add_action(edit_menu, "粘贴(&V)", self._paste, QKeySequence.Paste)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "全选(&A)", self._select_all, QKeySequence.SelectAll)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "注释/取消注释(&C)", self._toggle_comment,
                         QKeySequence(Qt.ControlModifier | Qt.Key_Slash))
        edit_menu.addSeparator()
        self._add_action(edit_menu, "查找(&F)...", self._show_find, QKeySequence.Find)
        self._add_action(edit_menu, "查找替换(&H)...", self._show_replace, QKeySequence.Replace)

        run_menu = mb.addMenu("运行(&R)")
        self._add_action(run_menu, "运行(&R)", self._run_code, QKeySequence(Qt.Key_F5))
        self._add_action(run_menu, "停止(&S)", self._stop_code, QKeySequence(Qt.ShiftModifier | Qt.Key_F5))
        run_menu.addSeparator()
        self._add_action(run_menu, "重置代码(&E)", self._reset_code, QKeySequence(Qt.ControlModifier | Qt.Key_R))
        run_menu.addSeparator()
        self._add_action(run_menu, "在终端中运行当前行", self._run_line_in_terminal)
        self._add_action(run_menu, "在终端中运行当前行 (Shell)", self._run_line_in_shell)
        run_menu.addSeparator()
        self._add_action(run_menu, "新建终端", self._new_terminal,
                         QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_QuoteLeft))
        self._add_action(run_menu, "关闭当前终端", self._close_terminal)

        view_menu = mb.addMenu("视图(&V)")
        self._add_action(view_menu, "文件浏览器(&E)", self._toggle_explorer)
        self._add_action(view_menu, "大纲(&O)", self._toggle_outline)
        self._add_action(view_menu, "底部面板(&B)", self._toggle_bottom_panel,
                         QKeySequence(Qt.ControlModifier | Qt.Key_QuoteLeft))
        view_menu.addSeparator()
        self._add_action(view_menu, "IPython 终端(&I)", self._show_ipython_terminal)
        self._add_action(view_menu, "Shell 终端(&S)", self._show_shell_terminal)
        view_menu.addSeparator()

        light_action = QAction("亮色主题(&L)", self, checkable=True, checked=True)
        light_action.triggered.connect(lambda: self._set_theme("light"))
        dark_action = QAction("暗色主题(&D)", self, checkable=True)
        dark_action.triggered.connect(lambda: self._set_theme("dark"))
        self._theme_group = [light_action, dark_action]
        theme_menu = view_menu.addMenu("主题(&T)")
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)

        saved_theme = self._settings.value("theme", "light")
        if saved_theme == "dark":
            dark_action.setChecked(True)
            light_action.setChecked(False)

        help_menu = mb.addMenu("帮助(&H)")
        self._add_action(help_menu, "关于(&A)", self._show_about)

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

    def _add_action(self, menu, text, slot, shortcut=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _connect_signals(self):
        self.activity_bar.button_clicked.connect(self._on_activity_clicked)
        self.file_tree.file_selected.connect(self._on_file_selected)
        self.file_tree.open_folder_requested.connect(self._actions.open_folder)
        self.executor.stdout_ready.connect(self.output_panel.append_stdout)
        self.executor.stderr_ready.connect(self.output_panel.append_stderr)
        self.executor.execution_started.connect(self._on_execution_started)
        self.executor.execution_finished.connect(self._on_execution_finished)

        self.output_panel.input_submitted.connect(self._send_input)
        self.output_panel.jump_to_line.connect(self._on_jump_to_line)

        self.find_replace.find_next_btn.clicked.connect(self._find_next)
        self.find_replace.find_prev_btn.clicked.connect(self._find_prev)
        self.find_replace.replace_btn.clicked.connect(self._replace_one)
        self.find_replace.replace_all_btn.clicked.connect(self._replace_all)
        self.find_replace.closed.connect(self._clear_find_highlight)

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
        return self._tabs.current_editor()

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
        editor = self._current_editor()
        if isinstance(editor, CodeEditor):
            self._update_status_pos()
            editor.setFocus()
            if editor.file_path:
                self.file_tree.select_file(editor.file_path)
            else:
                self.file_tree.clear_tree_selection()
        elif editor:
            editor.setFocus()

    def _on_file_selected(self, file_path: str):
        self._open_file_by_path(file_path)

    def _create_terminal(self):
        from npworks_ide.ide.terminal import TerminalWidget
        self.terminal = TerminalWidget(self)
        theme = self._settings.value("theme", "light")
        self.terminal.set_theme(theme)
        return self.terminal

    def _create_shell(self):
        from npworks_ide.ide.shell_terminal import TerminalPanel
        self.shell_terminal = TerminalPanel(self)
        theme = self._settings.value("theme", "light")
        self.shell_terminal.set_theme(theme)
        return self.shell_terminal

    def _new_file(self):
        editor = self._tabs.new_file()
        editor.cursorPositionChanged.connect(self._update_status_pos)
        editor.file_dropped.connect(self._open_file_by_path)

    def _open_file(self):
        default_dir = os.path.expanduser("~/npworks")
        os.makedirs(default_dir, exist_ok=True)
        paths, _ = QFileDialog.getOpenFileNames(
            self, "打开文件", default_dir, "Python 文件 (*.py);;Markdown (*.md);;图片 (*.png *.jpg *.bmp *.gif);;所有文件 (*)"
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
                self._actions._add_recent_file(path)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", str(e))
            return

        if is_markdown_file(path):
            try:
                preview = MarkdownPreview(path, self)
                idx = self._tab_widget.addTab(preview, f"\U0001F4C4 {title}")
                self._tab_widget.setCurrentIndex(idx)
                self._actions._add_recent_file(path)
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
            self._actions._add_recent_file(path)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", str(e))

    def _run_code(self):
        editor = self._current_editor()
        if not editor:
            return
        code = editor.get_code()
        if not code.strip():
            return
        self.output_panel.clear_output()
        self._start_time = datetime.now()
        self.output_panel.append_system(">>> 运行中...")
        self._bottom_panel.show()
        self._bottom_panel.show_output_tab()
        if not self.executor.execute(code):
            self._start_time = None

    def _stop_code(self):
        self.executor.stop()
        self.output_panel.append_system("已手动终止")

    def _reset_code(self):
        editor = self._current_editor()
        if editor:
            editor.reset_to_original()
            self.output_panel.append_system("已重置为原始代码")

    def _run_line_in_terminal(self):
        editor = self._current_editor()
        if not editor:
            return
        line, _ = editor.getCursorPosition()
        text = editor.text(line).strip()
        if text:
            self._bottom_panel.show()
            self._bottom_panel.show_terminal_tab()

    def _run_line_in_shell(self):
        editor = self._current_editor()
        if not editor:
            return
        line, _ = editor.getCursorPosition()
        text = editor.text(line).strip()
        if text:
            self._bottom_panel.show()
            self._bottom_panel.show_shell_tab()

    def _new_terminal(self):
        self._bottom_panel.show()
        self._bottom_panel.show_shell_tab()
        if self.shell_terminal:
            self.shell_terminal.add_terminal()

    def _close_terminal(self):
        if self.shell_terminal:
            self.shell_terminal.close_terminal()

    def _show_ipython_terminal(self):
        self._bottom_panel.show()
        self._bottom_panel.show_terminal_tab()

    def _show_shell_terminal(self):
        self._bottom_panel.show()
        self._bottom_panel.show_shell_tab()

    def _send_input(self, text):
        self.executor.send_input(text)

    def _undo(self):
        editor = self._current_editor()
        if editor:
            editor.undo()

    def _redo(self):
        editor = self._current_editor()
        if editor:
            editor.redo()

    def _cut(self):
        editor = self._current_editor()
        if editor:
            editor.cut()

    def _copy(self):
        editor = self._current_editor()
        if editor:
            editor.copy()

    def _paste(self):
        editor = self._current_editor()
        if editor:
            editor.paste()

    def _select_all(self):
        editor = self._current_editor()
        if editor:
            editor.selectAll()

    def _show_find(self):
        self.find_replace.show_find()

    def _show_replace(self):
        self.find_replace.show_replace()

    def _find_next(self):
        editor = self._current_editor()
        if not editor:
            return
        text = self.find_replace.get_find_text()
        if not text:
            return
        cs = self.find_replace.is_case_sensitive()
        line, col = editor.getCursorPosition()
        col += 1
        found = editor.findFirst(text, False, cs, False, True, line, col)
        if found:
            self.find_replace.set_match_count(1, 1)
        else:
            found = editor.findFirst(text, False, cs, False, True, 0, 0)
            if found:
                self.find_replace.set_match_count(1, 1)
            else:
                self.find_replace.set_match_count(0, 0)

    def _find_prev(self):
        editor = self._current_editor()
        if not editor:
            return
        text = self.find_replace.get_find_text()
        if not text:
            return
        cs = self.find_replace.is_case_sensitive()
        line, col = editor.getCursorPosition()
        found = editor.findFirst(text, False, cs, False, False, line, col)
        if not found:
            last_line = editor.lines() - 1
            line_len = len(editor.text(last_line))
            editor.findFirst(text, False, cs, False, False, last_line, line_len)

    def _replace_one(self):
        editor = self._current_editor()
        if not editor:
            return
        find_text = self.find_replace.get_find_text()
        replace_text = self.find_replace.get_replace_text()
        if not find_text:
            return
        if editor.hasSelectedText() and editor.selectedText() == find_text:
            editor.replaceSelectedText(replace_text)
        self._find_next()

    def _replace_all(self):
        editor = self._current_editor()
        if not editor:
            return
        find_text = self.find_replace.get_find_text()
        replace_text = self.find_replace.get_replace_text()
        if not find_text:
            return
        cs = self.find_replace.is_case_sensitive()
        editor.beginUndoAction()
        editor.setCursorPosition(0, 0)
        count = 0
        found = editor.findFirst(find_text, False, cs, False, True, 0, 0)
        while found:
            editor.replaceSelectedText(replace_text)
            count += 1
            found = editor.findNext()
        editor.endUndoAction()
        self.find_replace.set_match_count(count, count)

    def _clear_find_highlight(self):
        pass

    def _toggle_comment(self):
        editor = self._current_editor()
        if editor:
            editor.toggle_comment()

    def _set_theme(self, name):
        from PyQt5.QtWidgets import QApplication
        apply_theme(QApplication.instance(), name)
        for i in range(self._tab_widget.count()):
            editor = self._tab_widget.widget(i)
            if isinstance(editor, CodeEditor):
                editor.apply_theme()
        if self.terminal:
            self.terminal.set_theme(name)
        if self.shell_terminal:
            self.shell_terminal.set_theme(name)
        for action in self._theme_group:
            action.setChecked(False)
        if name == "dark":
            self._theme_group[1].setChecked(True)
        else:
            self._theme_group[0].setChecked(True)

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

    def _on_execution_started(self):
        self._run_label.setText(" ● 运行中 ")
        self.output_panel.show_input()

    def _on_execution_finished(self, exit_code, exit_status):
        self.output_panel.hide_input()
        if self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            self._run_label.setText("")
            self.output_panel.append_system(
                f"[运行完毕] 退出码={exit_code} 耗时={elapsed:.2f}s"
            )
            self._start_time = None
        else:
            self._run_label.setText("")

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
        self._actions._save_open_folders()
        if self.terminal:
            self.terminal.cleanup()
        if self.shell_terminal:
            self.shell_terminal.cleanup()
        super().closeEvent(event)
