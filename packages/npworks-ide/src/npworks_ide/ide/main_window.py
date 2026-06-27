import sys
import os

from PyQt5.QtCore import Qt, QSettings, QSize, QPoint, QEvent
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox,
    QTabWidget, QLabel, QWidget, QFrame, QAction,
    QVBoxLayout,
)

from npworks_ide.ide.activity_bar import ActivityBar
from npworks_ide.ide.file_tree import FileTree
from npworks_ide.ide.editor import CodeEditor
from npworks_ide.ide.output_panel import OutputPanel
from npworks_ide.ide.find_replace import FindReplacePanel
from npworks_ide.ide.sidebar_panel import SideBarPanel, SideView
from npworks_ide.ide.outline_view import OutlineView
from npworks_ide.ide.explorer_view import ExplorerView
from npworks_ide.ide.bottom_panel import BottomPanel
from npworks_ide.ide.tab_manager import TabManager
from npworks_ide.ide.actions import ActionManager
from npworks_ide.ide.menu_builder import MenuBuilder
from npworks_ide.ide.run_controller import RunController
from npworks_ide.ide.find_controller import FindController
from npworks_ide.ide.edit_controller import EditController
from npworks_ide.ide.theme_controller import ThemeController
from npworks_ide.ide.editor_registry import registry
from npworks_ide.ide.builtin_editors import register_builtin_editors
from npworks_ide.ide.command_registry import CommandRegistry
from npworks_ide.ide.plugin_api import PluginAPI
from npworks_ide.ide.plugin_loader import PluginLoader
from npworks_ide.runner.executor import Executor, _RC_LINE_COUNT

import npworks_content

_IDX_EXPLORER = 0
_IDX_OUTLINE = 1
_IDX_SETTINGS = 2

_SIDEBAR_WIDTH = 260


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPworks")
        self.resize(1280, 860)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._win_controls = None

        self._settings = QSettings("npworks", "npworks")
        self._restore_geometry()

        self.executor = Executor(self)
        register_builtin_editors()
        self._activity_handlers = {}
        self.command_registry = CommandRegistry()
        self.setting_sections = []
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

        self._setup_window_controls()

        self._setup_activity_bar()
        self._build_toolbar()
        self._init_file_tree()

        self._restore_layout()

        self.theme_ctrl.apply_window_icon()
        self.activity_bar.apply_theme_icons(self.theme_ctrl.get_current_theme())
        self._refresh_sidebar_icons()
        self._outline_view.refresh()
        self._restore_appearance()
        self._load_plugins()
        self._apply_titlebar(self.theme_ctrl.get_current_theme())

    def _load_plugins(self):
        self.plugin_loader = PluginLoader()
        self.plugin_api = PluginAPI(self)
        self.plugin_loader.discover()
        self.plugin_loader.load(self.plugin_api)

    def _open_plugins(self):
        from npworks_ide.ide.plugins_panel import PluginsPanel
        self.activity_bar.set_checked(-1)
        self.open_panel(PluginsPanel(self, self))

    def _apply_titlebar(self, theme):
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        from npworks_ide.ide.native_window import apply_titlebar_theme
        v = DARK_VARS if theme == "dark" else LIGHT_VARS
        apply_titlebar_theme(self, theme, v["bg_menu"], v["border"])

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_titlebar(self.theme_ctrl.get_current_theme())

    def _setup_layout(self):
        self._outline_view = OutlineView(self)

        self._primary = SideBarPanel("primary", self)
        self._primary.set_move_callback(self._move_view)
        self._secondary = SideBarPanel("secondary", self)
        self._secondary.set_move_callback(self._move_view)

        self._explorer_view = ExplorerView(self.file_tree)
        self._open_editors = self._explorer_view.open_editors
        self._open_editors.bind(self._tab_widget, self._tabs.close_tab)

        self._explorer_sideview = SideView("explorer", "文件浏览器", "explorer", self._explorer_view)
        self._outline_sideview = SideView("outline", "大纲", "outline", self._outline_view)
        self._all_side_views = {"explorer": self._explorer_sideview, "outline": self._outline_sideview}
        self._hidden_side_views = {}

        self._primary.add_view(self._explorer_sideview)
        self._primary.add_view(self._outline_sideview)

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
        self._h_splitter.addWidget(self._primary)
        self._h_splitter.addWidget(self._editor_area)
        self._h_splitter.addWidget(self._secondary)
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
        self.activity_bar.add_button("explorer", "文件浏览器")
        self.activity_bar.add_button("outline", "大纲")
        self.activity_bar.add_button("extensions", "插件", bottom=True)
        self.activity_bar.add_button("settings", "设置", bottom=True)
        self.activity_bar.set_checked(0)
        self._activity_handlers[2] = self._open_plugins
        self._activity_handlers[3] = self._open_settings

    def _setup_window_controls(self):
        from npworks_ide.ide.window_controls import WindowControls
        self._win_controls = WindowControls(self, self)
        self._win_controls.refresh_icons(self.theme_ctrl.get_current_theme())
        self.menuBar().setCornerWidget(self._win_controls, Qt.TopRightCorner)

    def _handle_nchittest(self, lparam):
        import ctypes
        x = ctypes.c_short(lparam & 0xFFFF).value
        y = ctypes.c_short((lparam >> 16) & 0xFFFF).value
        local = self.mapFromGlobal(QPoint(x, y))
        b = 6
        w, h = self.width(), self.height()
        on_l = local.x() <= b
        on_r = local.x() >= w - b
        on_t = local.y() <= b
        on_b = local.y() >= h - b
        HT = {"L": 0xA, "R": 0xB, "T": 0xC, "B": 0xF,
              "TL": 0xD, "TR": 0xE, "BL": 0x10, "BR": 0x11}
        if on_t and on_l:
            return (True, HT["TL"])
        if on_t and on_r:
            return (True, HT["TR"])
        if on_b and on_l:
            return (True, HT["BL"])
        if on_b and on_r:
            return (True, HT["BR"])
        if on_l:
            return (True, HT["L"])
        if on_r:
            return (True, HT["R"])
        if on_t:
            return (True, HT["T"])
        if on_b:
            return (True, HT["B"])
        # 菜单栏空白区域作为标题栏（拖动移动 + 双击最大化）
        mb = self.menuBar()
        mbl = mb.mapFrom(self, local)
        if mb.rect().contains(mbl) and mb.actionAt(mbl) is None:
            corner = mb.cornerWidget(Qt.TopRightCorner)
            if corner is not None and corner.geometry().contains(mbl):
                return (False, 0)
            return (True, 0x2)   # HTCAPTION
        return (False, 0)

    def nativeEvent(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            try:
                import ctypes
                from ctypes import wintypes
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == 0x0084:   # WM_NCHITTEST
                    return self._handle_nchittest(msg.lParam)
            except Exception:
                pass
        return super().nativeEvent(eventType, message)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self._win_controls is not None:
            self._win_controls.update_icons()
        super().changeEvent(event)

    def _build_toolbar(self):
        from npworks_ide.ide import icons

        tb = self.addToolBar("main")
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        tb.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._toolbar = tb
        self._toolbar_actions = {}

        def add(key, slot, tip):
            act = QAction(self)
            act.setToolTip(tip)
            act.triggered.connect(slot)
            tb.addAction(act)
            self._toolbar_actions[key] = act
            return act

        add("new", self._new_file, "新建 (Ctrl+N)")
        add("open", self._open_file, "打开 (Ctrl+O)")
        add("save", self._save_code, "保存 (Ctrl+S)")
        tb.addSeparator()
        add("run", self.run_ctrl.run_code, "运行 (F5)")
        add("stop", self.run_ctrl.stop_code, "停止 (Shift+F5)")
        add("reset", self.run_ctrl.reset_code, "重置代码 (Ctrl+R)")
        self._refresh_toolbar_icons()
        self._update_toolbar_state()

    def _refresh_toolbar_icons(self):
        from npworks_ide.ide import icons
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        theme = self.theme_ctrl.get_current_theme()
        v = DARK_VARS if theme == "dark" else LIGHT_VARS
        for key, act in self._toolbar_actions.items():
            act.setIcon(icons.icon(key, v["fg"], 18))

    def _update_toolbar_state(self):
        from npworks_ide.ide.editor_registry import EditorView
        widget = self._tab_widget.currentWidget()
        is_view = isinstance(widget, EditorView)
        readonly = is_view and widget.is_readonly()
        has_editor = self._editor_of(widget) is not None
        self._toolbar_actions["save"].setEnabled(is_view and not readonly)
        for key in ("run", "stop", "reset"):
            self._toolbar_actions[key].setEnabled(has_editor)

    def _open_settings(self):
        from npworks_ide.ide.settings_panel import SettingsPanel
        self.activity_bar.set_checked(-1)
        self.open_panel(SettingsPanel(self, self))

    def open_panel(self, panel):
        """以"文档页面"标签页形式打开任意插件面板（VS Code 风格）。

        面板需继承 DocumentPanel(EditorView)。按 panel_id 去重：已打开则聚焦。
        """
        from npworks_ide.ide.editor_registry import EditorView
        if not isinstance(panel, EditorView):
            return None
        pid = getattr(panel, "panel_id", None)
        if pid:
            for i in range(self._tab_widget.count()):
                w = self._tab_widget.widget(i)
                if getattr(w, "panel_id", None) == pid:
                    self._tab_widget.setCurrentIndex(i)
                    return panel
        idx = self._tab_widget.addTab(panel, panel.editor_title())
        self._tab_widget.setCurrentIndex(idx)
        panel.apply_theme(self.theme_ctrl.get_current_theme())
        return panel

    def _apply_editor_prefs_to_all(self):
        from npworks_ide.ide.editor_registry import EditorView
        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            if isinstance(widget, EditorView):
                widget.apply_editor_prefs()

    _ACTIVITY_VIEW = {0: "explorer", 1: "outline"}

    def _panel_index(self, panel):
        return 1 if panel is self._primary else 3

    def _panel_having(self, view_id):
        if self._primary.has_view(view_id):
            return self._primary
        if self._secondary.has_view(view_id):
            return self._secondary
        return None

    def _is_sidebar_open(self, panel):
        return self._h_splitter.sizes()[self._panel_index(panel)] > 50

    def _open_sidebar(self, panel):
        sizes = self._h_splitter.sizes()
        idx = self._panel_index(panel)
        if sizes[idx] < 50:
            sizes[idx] = _SIDEBAR_WIDTH
            self._h_splitter.setSizes(sizes)

    def _close_sidebar(self, panel):
        sizes = self._h_splitter.sizes()
        sizes[self._panel_index(panel)] = 0
        self._h_splitter.setSizes(sizes)

    def _activate_view(self, view_id):
        panel = self._panel_having(view_id)
        if panel is None:
            return
        if panel.current_view_id() == view_id and self._is_sidebar_open(panel):
            self._close_sidebar(panel)
            self.activity_bar.set_checked(-1)
        else:
            panel.show_view(view_id)
            self._open_sidebar(panel)
            idx = next((k for k, v in self._ACTIVITY_VIEW.items() if v == view_id), None)
            if idx is not None:
                self.activity_bar.set_checked(idx)

    def _move_view(self, view_id):
        src = self._panel_having(view_id)
        if src is None:
            return
        dst = self._secondary if src is self._primary else self._primary
        view = src.remove_view(view_id)
        if view is None:
            return
        dst.add_view(view)
        dst.show_view(view_id)
        self._open_sidebar(dst)
        self._refresh_sidebar_icons()

    def _refresh_sidebar_icons(self):
        from npworks_ide.ide import icons
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        theme = self.theme_ctrl.get_current_theme()
        v = DARK_VARS if theme == "dark" else LIGHT_VARS
        icon = icons.icon("panels", v["fg"], 14)
        self._primary.set_move_icon(icon)
        self._secondary.set_move_icon(icon)

    # --- 外观开关（设置页 / 持久化） ---
    def _persist(self, key, on):
        self._settings.setValue(key, "1" if on else "0")

    def is_primary_sidebar(self):
        return self._is_sidebar_open(self._primary)

    def set_primary_sidebar(self, on):
        self._open_sidebar(self._primary) if on else self._close_sidebar(self._primary)
        self._persist("appearance/primary", on)

    def is_secondary_sidebar(self):
        return self._is_sidebar_open(self._secondary)

    def set_secondary_sidebar(self, on):
        self._open_sidebar(self._secondary) if on else self._close_sidebar(self._secondary)
        self._persist("appearance/secondary", on)

    def is_menu_bar(self):
        acts = self.menuBar().actions()
        return acts[0].isVisible() if acts else True

    def set_menu_bar(self, on):
        for a in self.menuBar().actions():
            a.setVisible(on)
        self._persist("appearance/menu_bar", on)

    def is_status_bar(self):
        return self.statusBar().isVisible()

    def set_status_bar(self, on):
        self.statusBar().setVisible(on)
        self._persist("appearance/status_bar", on)

    def is_panel(self):
        return self._bottom_panel.isVisible()

    def set_panel(self, on):
        self._bottom_panel.setVisible(on)
        self._persist("appearance/panel", on)

    def is_view_visible(self, view_id):
        return self._panel_having(view_id) is not None

    def set_view_visible(self, view_id, on):
        if on:
            view = self._hidden_side_views.pop(view_id, None) or self._all_side_views.get(view_id)
            if view is None:
                return
            if not self._panel_having(view_id):
                self._primary.add_view(view)
                self._primary.show_view(view_id)
        else:
            panel = self._panel_having(view_id)
            if panel:
                view = panel.remove_view(view_id)
                if view:
                    self._hidden_side_views[view_id] = view
        self._persist(f"appearance/view_{view_id}", on)

    def _restore_appearance(self):
        s = self._settings
        self.set_primary_sidebar(s.value("appearance/primary", "1") == "1")
        self.set_secondary_sidebar(s.value("appearance/secondary", "0") == "1")
        self.set_menu_bar(s.value("appearance/menu_bar", "1") == "1")
        self.set_status_bar(s.value("appearance/status_bar", "1") == "1")
        self.set_panel(s.value("appearance/panel", "1") == "1")
        for vid in self._all_side_views:
            self.set_view_visible(vid, s.value(f"appearance/view_{vid}", "1") == "1")

    def _build_status_bar(self):
        sb = self.statusBar()
        sb.setStyleSheet("QStatusBar { border: none; }")

        self._run_label = QLabel("")
        self._run_label.setFont(QFont("Segoe UI", 9))
        sb.addWidget(self._run_label)

        sb.addWidget(self._make_status_sep())

        self._pos_label = QLabel(" 行 1, 列 1 ")
        self._pos_label.setFont(QFont("Consolas", 9))
        sb.addPermanentWidget(self._pos_label)

        sb.addPermanentWidget(self._make_status_sep())

        self._encoding_label = QLabel(" UTF-8 ")
        self._encoding_label.setFont(QFont("Consolas", 9))
        sb.addPermanentWidget(self._encoding_label)

        sb.addPermanentWidget(self._make_status_sep())

        py_ver = f" Python {sys.version.split()[0]} "
        py_label = QLabel(py_ver)
        py_label.setFont(QFont("Consolas", 9))
        sb.addPermanentWidget(py_label)

    @staticmethod
    def _make_status_sep():
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(14)
        sep.setStyleSheet(
            "QFrame { color: rgba(255,255,255,70); background: transparent; }"
        )
        return sep

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
        self._tab_widget.tabCloseRequested.connect(lambda _i: self._open_editors.refresh())

    def _on_activity_clicked(self, index: int):
        if index in self._activity_handlers:
            self._activity_handlers[index]()
            return
        view_id = self._ACTIVITY_VIEW.get(index)
        if view_id:
            self._activate_view(view_id)

    def _toggle_explorer(self):
        self._activate_view("explorer")

    def _toggle_outline(self):
        self._activate_view("outline")

    def _toggle_bottom_panel(self):
        vis = self._bottom_panel.isVisible()
        self._bottom_panel.setVisible(not vis)

    def _current_editor(self) -> CodeEditor:
        widget = self._tab_widget.currentWidget()
        if hasattr(widget, "get_editor"):
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
            if not os.path.isdir(folder):
                continue
            if self.file_tree.is_content_source_dir(folder):
                continue
            self.file_tree.add_root(folder)
        if self.file_tree.root_count() > 0:
            self.file_tree.expand_first_root()
        # 规范化：清掉历史持久化里残留的 content 目录
        self._actions.save_open_folders()

    def _on_tab_changed(self, index):
        widget = self._tab_widget.currentWidget()
        if hasattr(widget, "get_editor"):
            editor = widget.get_editor()
            editor.setFocus()
            if getattr(widget, "file_path", None):
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
        self._update_toolbar_state()
        if self._outline_view is not None:
            self._outline_view.refresh()
        self._open_editors.refresh()

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

        view = None
        try:
            view = registry.open(path, self)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", str(e))
            return
        if view is None:
            return
        tab_title = registry.title_for(path)
        idx = self._tab_widget.addTab(view, tab_title)
        self._tab_widget.setCurrentIndex(idx)
        self._actions.add_recent_file(path)

        editor = self._editor_of(view)
        if editor is not None:
            editor.cursorPositionChanged.connect(self._update_status_pos)
            editor.file_dropped.connect(self._open_file_by_path)
            editor.modificationChanged.connect(
                lambda m, e=editor: self._on_modification_changed(e, m)
            )
        self._open_editors.refresh()

    def _editor_of(self, widget):
        """返回某标签视图底层用于编辑/光标/查找的 CodeEditor（查看器返回 None）。"""
        from npworks_ide.ide.editor import CodeEditor
        if isinstance(widget, CodeEditor):
            return widget
        if hasattr(widget, "get_editor"):
            return widget.get_editor()
        return None

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
                hasattr(widget, "get_editor") and widget.get_editor() is editor)
            if editor_match:
                base = registry.title_for(getattr(widget, "file_path", "") or "")
                self._tab_widget.setTabText(i, f"{'*' if modified else ''}{base}")
                self._open_editors.refresh()
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
