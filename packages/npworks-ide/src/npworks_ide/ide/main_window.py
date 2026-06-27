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
from npworks_ide.ide.outline_view import OutlineView
from npworks_ide.ide.explorer_view import ExplorerView
from npworks_ide.ide.dock_manager import DockManager, DockZone
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
_RIGHT_WIDTH = 320
_BOTTOM_HEIGHT = 240

# 固定栏位 -> (所在 splitter 属性名, 在 splitter 中的索引, 默认尺寸)
_ZONE_LAYOUT = {
    "left": ("_h_splitter", 1, _SIDEBAR_WIDTH),
    "right": ("_h_splitter", 3, _RIGHT_WIDTH),
    "bottom": ("_v_splitter", 1, _BOTTOM_HEIGHT),
}


class _LazyPanel(QWidget):
    """懒创建的容器面板：首次显示时才调用 factory 构建内部控件（如终端）。"""

    def __init__(self, factory, parent=None):
        super().__init__(parent)
        self._factory = factory
        self._inner = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def ensure(self):
        if self._inner is None and self._factory is not None:
            try:
                self._inner = self._factory()
            except Exception:
                self._inner = None
            if self._inner is not None:
                self.layout().addWidget(self._inner)
        return self._inner

    def showEvent(self, event):
        super().showEvent(event)
        self.ensure()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPworks")
        self.resize(1280, 860)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._win_controls = None

        self._settings = QSettings("npworks", "npworks")
        self._restore_geometry()
        self._zone_actions = {}   # zone name -> checkable QAction（视图菜单栏位开关）

        self.executor = Executor(self)
        register_builtin_editors()
        self._activity_handlers = {}
        self.command_registry = CommandRegistry()
        self.setting_sections = []
        self.file_tree = FileTree(self)
        self.output_panel = OutputPanel(self)
        self.find_replace = FindReplacePanel(self)
        self.activity_bar = ActivityBar(self)

        self._tab_widget = QTabWidget()
        self._tabs = TabManager(self._tab_widget, on_tab_changed_cb=self._on_tab_changed)

        self._actions = ActionManager(
            self, self._tabs, self.file_tree, self.output_panel,
            self.executor,
        )

        self.run_ctrl = RunController(
            self, self.executor, self.output_panel,
        )

        self.find_ctrl = FindController(self, self.find_replace)
        self.edit_ctrl = EditController(self)
        self.theme_ctrl = ThemeController(
            self, self._tab_widget, self._settings,
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

    def _open_command_palette(self):
        from npworks_ide.ide.command_palette import CommandPalette
        CommandPalette(self, "commands", self).exec_()

    def _open_quick_open(self):
        from npworks_ide.ide.command_palette import CommandPalette
        CommandPalette(self, "files", self).exec_()

    def _palette_commands(self):
        cmds = [
            ("文件: 新建", self._new_file),
            ("文件: 打开…", self._open_file),
            ("文件: 打开文件夹…", self._open_folder),
            ("文件: 保存", self._save_code),
            ("文件: 全部保存", self._save_all),
            ("运行: 运行 (F5)", self.run_ctrl.run_code),
            ("运行: 停止 (Shift+F5)", self.run_ctrl.stop_code),
            ("运行: 重置代码 (Ctrl+R)", self.run_ctrl.reset_code),
            ("编辑: 查找 (Ctrl+F)", self._show_find),
            ("编辑: 查找替换 (Ctrl+H)", self._show_replace),
            ("编辑: 跳转到行 (Ctrl+G)", self._go_to_line),
            ("视图: 文件浏览器", self._toggle_explorer),
            ("视图: 大纲", self._toggle_outline),
            ("视图: 底部面板 (Ctrl+`)", self._toggle_bottom_panel),
            ("视图: 设置", self._open_settings),
            ("视图: 插件", self._open_plugins),
            ("视图: 暗色主题", lambda: self.theme_ctrl.set_theme("dark")),
            ("视图: 亮色主题", lambda: self.theme_ctrl.set_theme("light")),
        ]
        for cid, title in self.command_registry.items():
            cmds.append((f"插件: {title}", lambda c=cid: self.command_registry.run(c)))
        return cmds

    def _palette_files(self):
        out = []
        recents = self._settings.value("recent_files", [])
        if isinstance(recents, str):
            recents = [recents]
        import os as _os
        for p in recents:
            if _os.path.isfile(p):
                out.append((_os.path.basename(p), p))
        # 扫描已打开文件夹下的文件（限制数量）
        count = 0
        for root in self.file_tree.get_open_folders():
            for dirpath, _dirs, files in _os.walk(root):
                for fn in files:
                    if fn.lower().endswith((".py", ".md", ".csv", ".tsv", ".pdf")):
                        full = _os.path.join(dirpath, fn)
                        out.append((fn + "  —  " + _os.path.relpath(full, root), full))
                        count += 1
                        if count >= 300:
                            return out
        return out

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
        self.dock = DockManager(self)

        # 三个固定的停靠栏位
        self._left_zone = DockZone("left", self.dock, self)
        self._right_zone = DockZone("right", self.dock, self)
        self._bottom_zone = DockZone("bottom", self.dock, self)
        self.dock.add_zone("left", self._left_zone)
        self.dock.add_zone("right", self._right_zone)
        self.dock.add_zone("bottom", self._bottom_zone)

        self._explorer_view = ExplorerView(self.file_tree)
        self._open_editors = self._explorer_view.open_editors
        self._open_editors.bind(self._tab_widget, self._tabs.close_tab)

        # 教材控件：独立的 NPWORKS 内容（教材配套程序）文件树，从浏览器中抽出
        self._textbook_tree = FileTree(self, textbook_only=True)
        self._textbook_tree.file_selected.connect(self._on_file_selected)
        self._textbook_tree.file_renamed.connect(self._on_file_renamed)
        self._textbook_tree.file_deleted.connect(self._on_file_deleted)

        # 可拖拽停靠的组件
        from npworks_ide.ide.figures_view import FiguresView
        self._figures_view = FiguresView(self)

        # IPython / Shell 终端：懒创建的独立可停靠面板
        self._ipython_panel = _LazyPanel(self.run_ctrl.create_terminal, self)
        self._shell_panel = _LazyPanel(self.run_ctrl.create_shell, self)
        self.run_ctrl.set_terminal_panels(self._ipython_panel, self._shell_panel)

        self._all_panels = ("explorer", "outline", "textbook", "figures",
                            "output", "ipython", "shell")
        self._hidden_panels = {}
        self._panel_titles = {
            "explorer": "文件浏览器",
            "outline": "大纲",
            "textbook": "教材",
            "figures": "图表",
            "output": "输出",
            "ipython": "IPython",
            "shell": "终端",
        }
        # 面板 -> 图标 key（用于栏位标签图标，随主题刷新）
        self._panel_icon_keys = {
            "explorer": "explorer",
            "outline": "outline",
            "textbook": "book",
            "figures": "chart",
            "output": None,
            "ipython": None,
            "shell": None,
        }
        self.dock.register_panel(
            "explorer", self._explorer_view, "文件浏览器", "left",
            icon=self._icon_for_key("explorer"))
        self.dock.register_panel(
            "outline", self._outline_view, "大纲", "left",
            icon=self._icon_for_key("outline"))
        self.dock.register_panel(
            "textbook", self._textbook_tree, "教材", "left",
            icon=self._icon_for_key("book"))
        self.dock.register_panel(
            "figures", self._figures_view, "图表", "right",
            icon=self._icon_for_key("chart"))
        self.dock.register_panel(
            "output", self.output_panel, "输出", "bottom")
        self.dock.register_panel(
            "ipython", self._ipython_panel, "IPython", "bottom")
        self.dock.register_panel(
            "shell", self._shell_panel, "终端", "bottom")

        self.dock.panel_moved.connect(self._on_panel_moved)

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

        # 横向：活动栏 | 左栏 | 编辑器 | 右栏（栏位固定，不可拖动）
        self._h_splitter = QSplitter(Qt.Horizontal)
        self._h_splitter.setObjectName("h_splitter")
        self._h_splitter.addWidget(self._activity_container)
        self._h_splitter.addWidget(self._left_zone)
        self._h_splitter.addWidget(self._editor_area)
        self._h_splitter.addWidget(self._right_zone)
        self._h_splitter.setStretchFactor(0, 0)
        self._h_splitter.setStretchFactor(1, 0)
        self._h_splitter.setStretchFactor(2, 1)
        self._h_splitter.setStretchFactor(3, 0)
        self._h_splitter.setHandleWidth(1)
        self._h_splitter.setSizes([48, _SIDEBAR_WIDTH, 1000, _RIGHT_WIDTH])

        # 纵向：上部主体 | 底栏（栏位固定，不可拖动）
        self._v_splitter = QSplitter(Qt.Vertical)
        self._v_splitter.setObjectName("v_splitter")
        self._v_splitter.addWidget(self._h_splitter)
        self._v_splitter.addWidget(self._bottom_zone)
        self._v_splitter.setStretchFactor(0, 1)
        self._v_splitter.setStretchFactor(1, 0)
        self._v_splitter.setHandleWidth(1)
        self._v_splitter.setSizes([600, _BOTTOM_HEIGHT])

        self.setCentralWidget(self._v_splitter)

    def _icon_for_key(self, key):
        from npworks_ide.ide import icons
        from npworks_ide.ide.themes.variables import LIGHT_VARS
        if key and key in icons._ICONS:
            return icons.icon(key, LIGHT_VARS["fg"], 16)
        return None

    def _on_panel_moved(self, panel_id, zone):
        self._settings.setValue(f"dock/panel_{panel_id}", zone)
        self._auto_adjust_zones()

    def _auto_adjust_zones(self):
        """空栏位自动收起，被拖入面板的栏位自动展开。"""
        for name, zone in self.dock.zones.items():
            if zone.count() == 0:
                self._set_zone_visible(name, False)
        for panel_id in self.dock.panel_ids():
            zone = self.dock.zone_of(panel_id)
            if zone and not self._is_zone_visible(zone):
                self._set_zone_visible(zone, True)
        self._sync_zone_actions()

    # --- 栏位可见性（栏位固定，仅控制展开/收起） ---
    def _zone_splitter_index(self, name):
        attr, idx, default = _ZONE_LAYOUT[name]
        return getattr(self, attr), idx, default

    def _is_zone_visible(self, name):
        splitter, idx, _ = self._zone_splitter_index(name)
        return splitter.sizes()[idx] > 50

    def _set_zone_visible(self, name, on):
        splitter, idx, default = self._zone_splitter_index(name)
        sizes = splitter.sizes()
        if on:
            if sizes[idx] < 50:
                sizes[idx] = default
                splitter.setSizes(sizes)
        else:
            if sizes[idx] > 0:
                sizes[idx] = 0
                splitter.setSizes(sizes)

    def _ensure_panel_zone_visible(self, panel_id):
        zone = self.dock.zone_of(panel_id)
        if zone and not self._is_zone_visible(zone):
            self._set_zone_visible(zone, True)
        return zone

    def _show_panel(self, panel_id):
        """显示某面板所在的栏位并聚焦该面板。"""
        zone = self.dock.zone_of(panel_id)
        if not zone:
            return
        self._set_zone_visible(zone, True)
        self.dock.focus_panel(panel_id)
        self._sync_zone_actions()

    def _show_output_panel(self):
        self._show_panel("output")

    def _setup_activity_bar(self):
        self.activity_bar.add_button("explorer", "文件浏览器")
        self.activity_bar.add_button("outline", "大纲")
        self.activity_bar.add_button("book", "教材")
        self.activity_bar.add_button("chart", "图表")
        self.activity_bar.add_button("extensions", "插件", bottom=True)
        self.activity_bar.add_button("settings", "设置", bottom=True)
        self.activity_bar.set_checked(0)
        self._activity_handlers[3] = self._toggle_figures_dock
        self._activity_handlers[4] = self._open_plugins
        self._activity_handlers[5] = self._open_settings

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

    _ACTIVITY_PANEL = {0: "explorer", 1: "outline", 2: "textbook"}

    def _activate_panel(self, panel_id):
        """活动栏入口：切换/聚焦某面板所在的栏位。"""
        zone = self.dock.zone_of(panel_id)
        if zone is None:
            return
        same = (self.dock.zones[zone].current_panel_id() == panel_id
                and self._is_zone_visible(zone))
        if same:
            self._set_zone_visible(zone, False)
            self.activity_bar.set_checked(-1)
            self._sync_zone_actions()
            return
        self._set_zone_visible(zone, True)
        self.dock.focus_panel(panel_id)
        idx = next((k for k, v in self._ACTIVITY_PANEL.items()
                    if v == panel_id), None)
        if idx is not None:
            self.activity_bar.set_checked(idx)
        self._sync_zone_actions()

    # 兼容旧调用名
    def _activate_view(self, view_id):
        self._activate_panel(view_id)

    def _toggle_figures_dock(self):
        zone = self.dock.zone_of("figures")
        if zone is None:
            return
        visible = self._is_zone_visible(zone)
        self._set_zone_visible(zone, not visible)
        if not visible:
            self.dock.focus_panel("figures")
        self.activity_bar.set_checked(3 if not visible else -1)
        self._sync_zone_actions()

    def _on_figure_ready(self, path):
        self._figures_view.add_figure(path)
        zone = self.dock.zone_of("figures")
        if zone:
            self._set_zone_visible(zone, True)
            self.dock.focus_panel("figures")
        self.activity_bar.set_checked(3)

    def _refresh_sidebar_icons(self):
        # 栏位标签图标随主题刷新
        from npworks_ide.ide import icons
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        theme = self.theme_ctrl.get_current_theme()
        v = DARK_VARS if theme == "dark" else LIGHT_VARS
        for panel_id, key in self._panel_icon_keys.items():
            if not key:
                continue
            zone_name = self.dock.zone_of(panel_id)
            if not zone_name:
                continue
            zone = self.dock.zones[zone_name]
            idx = zone.index_of(panel_id)
            if idx >= 0:
                zone.setTabIcon(idx, icons.icon(key, v["fg"], 16))

    def add_plugin_view(self, view, side="primary"):
        """插件贡献的视图注册为可停靠面板（默认挂到左栏）。"""
        zone = "left" if side == "primary" else "right"
        view_id = getattr(view, "view_id", None) or f"plugin_{id(view)}"
        title = getattr(view, "title", view_id)
        icon_key = getattr(view, "icon_key", None)
        self._all_panels = self._all_panels + (view_id,)
        self._panel_titles[view_id] = title
        self._panel_icon_keys[view_id] = icon_key
        self.dock.register_panel(view_id, view.widget, title, zone,
                                 icon=self._icon_for_key(icon_key))

    # --- 外观开关（设置页 / 持久化） ---
    def _persist(self, key, on):
        self._settings.setValue(key, "1" if on else "0")

    def _sync_zone_actions(self):
        """同步视图菜单中三个栏位开关的勾选状态。"""
        for zone, act in self._zone_actions.items():
            act.setChecked(self._is_zone_visible(zone))

    def is_primary_sidebar(self):
        return self._is_zone_visible("left")

    def set_primary_sidebar(self, on):
        self._set_zone_visible("left", on)
        self._persist("appearance/primary", on)
        self._sync_zone_actions()

    def is_figures_dock(self):
        zone = self.dock.zone_of("figures")
        return bool(zone) and self._is_zone_visible(zone)

    def set_figures_dock(self, on):
        zone = self.dock.zone_of("figures")
        if zone:
            self._set_zone_visible(zone, on)
        self._persist("appearance/figures", on)
        self._sync_zone_actions()

    def is_secondary_sidebar(self):
        return self._is_zone_visible("right")

    def set_secondary_sidebar(self, on):
        self._set_zone_visible("right", on)
        self._persist("appearance/secondary", on)
        self._sync_zone_actions()

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
        return self._is_zone_visible("bottom")

    def set_panel(self, on):
        self._set_zone_visible("bottom", on)
        self._persist("appearance/panel", on)
        self._sync_zone_actions()

    def is_view_visible(self, view_id):
        return self.dock.zone_of(view_id) is not None

    def set_view_visible(self, view_id, on):
        if on:
            info = self._hidden_panels.pop(view_id, None)
            if info is None:
                return
            self.dock.register_panel(
                view_id, info["widget"], info["title"], info["zone"],
                icon=info.get("icon"))
            self._set_zone_visible(info["zone"], True)
        else:
            zone = self.dock.zone_of(view_id)
            if zone is None:
                return
            info = self.dock.detach_panel(view_id)
            if info:
                self._hidden_panels[view_id] = info
                if self.dock.zones[zone].count() == 0:
                    self._set_zone_visible(zone, False)
        self._persist(f"appearance/view_{view_id}", on)

    def _restore_appearance(self):
        s = self._settings
        # 恢复面板停靠栏位
        for panel_id in self._all_panels:
            saved_zone = s.value(f"dock/panel_{panel_id}")
            if saved_zone in self.dock.zones:
                self.dock.move_panel(panel_id, saved_zone)
        # 恢复组件显隐
        for vid in self._all_panels:
            if s.value(f"appearance/view_{vid}", "1") != "1":
                self.set_view_visible(vid, False)
        # 恢复栏位展开/收起
        self.set_primary_sidebar(s.value("appearance/primary", "1") == "1")
        self.set_secondary_sidebar(
            s.value("appearance/secondary",
                    s.value("appearance/figures", "0")) == "1")
        self.set_menu_bar(s.value("appearance/menu_bar", "1") == "1")
        self.set_status_bar(s.value("appearance/status_bar", "1") == "1")
        self.set_panel(s.value("appearance/panel", "1") == "1")
        self._sync_zone_actions()

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
        self.output_panel.figure_ready.connect(self._on_figure_ready)

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
        panel_id = self._ACTIVITY_PANEL.get(index)
        if panel_id:
            self._activate_panel(panel_id)

    def _toggle_explorer(self):
        self._activate_panel("explorer")

    def _toggle_outline(self):
        self._activate_panel("outline")

    def _toggle_bottom_panel(self):
        self._set_zone_visible("bottom", not self._is_zone_visible("bottom"))
        self._sync_zone_actions()

    def _current_editor(self) -> CodeEditor:
        widget = self._tab_widget.currentWidget()
        if hasattr(widget, "get_editor"):
            return widget.get_editor()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def _init_file_tree(self):
        # 教材内容已独立为"教材"控件（_textbook_tree），主浏览器只加载用户文件夹
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
        # 首次启动若无历史文件夹记录，用当前已打开的文件夹初始化
        if not self._settings.value("recent_folders", []):
            for folder in self.file_tree.get_open_folders():
                if not self.file_tree.is_content_source_dir(folder):
                    self._actions._add_recent_folder(folder)

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
        default_dir = self._actions._default_open_dir()
        paths, _ = QFileDialog.getOpenFileNames(
            self, "打开文件", default_dir, "Python 文件 (*.py);;Markdown (*.md);;CSV 表格 (*.csv *.tsv);;PDF (*.pdf);;图片 (*.png *.jpg *.bmp *.gif);;所有文件 (*)"
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
        self._settings.setValue("last_dir", os.path.dirname(path))

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
        h_sizes = self._settings.value("dock/h_sizes")
        if h_sizes and len(h_sizes) == 4:
            self._h_splitter.setSizes([int(s) for s in h_sizes])
        v_sizes = self._settings.value("dock/v_sizes")
        if v_sizes and len(v_sizes) == 2:
            self._v_splitter.setSizes([int(s) for s in v_sizes])

    def closeEvent(self, event):
        self._settings.setValue("window_size", self.size())
        self._settings.setValue("window_pos", self.pos())
        self._settings.setValue("dock/h_sizes", self._h_splitter.sizes())
        self._settings.setValue("dock/v_sizes", self._v_splitter.sizes())
        self._settings.setValue("window_state", self.saveState())
        self._actions.save_open_folders()
        self.run_ctrl.cleanup()
        super().closeEvent(event)
