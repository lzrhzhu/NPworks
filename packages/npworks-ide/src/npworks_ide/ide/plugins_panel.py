"""插件管理文档页：列出已发现的插件、启用/禁用、加载状态。"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QFrame,
)

from npworks_ide.ide.document_panel import DocumentPanel


class _PluginRow(QFrame):
    def __init__(self, plugin, loader, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_card")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)

        name = QLabel(plugin.name)
        f = name.font()
        f.setBold(True)
        name.setFont(f)
        lay.addWidget(name)

        meta = QLabel(
            ("入口点 " if plugin.kind == "entrypoint" else "本地 ")
            + plugin.source
        )
        meta.setStyleSheet("color: gray; font-size: 11px;")
        lay.addWidget(meta)
        lay.addStretch()

        if plugin.error:
            status = QLabel("加载失败")
            status.setStyleSheet("color: #C14545;")
            lay.addWidget(status)
            tip = QLabel(plugin.error)
            tip.setStyleSheet("color: gray; font-size: 11px;")
            lay.addWidget(tip)
        elif plugin.loaded:
            ok = QLabel("已加载")
            ok.setStyleSheet("color: #4EC9B0;")
            lay.addWidget(ok)
        elif not plugin.enabled:
            off = QLabel("已禁用")
            off.setStyleSheet("color: gray;")
            lay.addWidget(off)

        self._chk = QCheckBox("启用")
        self._chk.setChecked(plugin.enabled)
        self._chk.stateChanged.connect(lambda _st: loader.set_enabled(plugin.name, self._chk.isChecked()))
        lay.addWidget(self._chk)


class PluginsPanel(DocumentPanel):
    def __init__(self, main_window, parent=None):
        super().__init__("插件", panel_id="npworks.plugins_manager", parent=parent)
        self._mw = main_window
        self.setObjectName("settings_panel")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(8)
        root.setAlignment(Qt.AlignTop)

        heading = QLabel("插件")
        f = heading.font()
        f.setPointSize(16)
        f.setBold(True)
        heading.setFont(f)
        root.addWidget(heading)

        note = QLabel(
            "通过 pip 安装声明了入口点 npworks.plugins 的包，或放入 "
            "%USERPROFILE%/.npworks/extensions/ 的 .py 脚本，重启后即被发现。\n"
            "启用/禁用改动在下次启动生效。"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray; font-size: 12px;")
        root.addWidget(note)

        plugins = main_window.plugin_loader.plugins()
        if not plugins:
            empty = QLabel("  尚未发现任何插件")
            empty.setStyleSheet("color: gray; padding: 16px;")
            root.addWidget(empty)
        for p in plugins:
            root.addWidget(_PluginRow(p, main_window.plugin_loader))
        root.addStretch()

        self.apply_theme(main_window.theme_ctrl.get_current_theme())

    def apply_theme(self, theme_name):
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
        self.setStyleSheet(
            f"QWidget#settings_panel {{ background: {v['bg_main']}; }}"
            f"QFrame#settings_card {{ background: {v['bg_input']}; "
            f"border: 1px solid {v['border']}; border-radius: 6px; }}"
        )
