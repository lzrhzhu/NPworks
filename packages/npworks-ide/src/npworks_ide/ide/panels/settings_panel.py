"""设置文档页面：以标签页形式呈现的设置（VS Code 风格），实时生效。"""
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox,
    QFrame, QCheckBox, QPushButton, QLineEdit, QMessageBox,
)

from npworks_ide.ide.dock.document_panel import DocumentPanel


class SettingsPanel(DocumentPanel):
    def __init__(self, main_window, parent=None):
        super().__init__("设置", panel_id="npworks.settings", parent=parent)
        self._mw = main_window
        self._settings = QSettings("npworks", "npworks")
        self.setObjectName("settings_panel")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(10)
        root.setAlignment(Qt.AlignTop)

        self._heading = QLabel("设置")
        f = self._heading.font()
        f.setPointSize(16)
        f.setBold(True)
        self._heading.setFont(f)
        root.addWidget(self._heading)

        self._sub = QLabel("修改即时生效并应用到所有已打开的编辑器；下次启动保持。")
        self._sub.setWordWrap(True)
        root.addWidget(self._sub)

        card = QFrame()
        card.setObjectName("settings_card")
        form = QFormLayout(card)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(12)

        theme = self._settings.value("theme", "light", type=str)
        self._combo_theme = QComboBox()
        self._combo_theme.addItem("亮色 (Light)", "light")
        self._combo_theme.addItem("暗色 (Dark)", "dark")
        self._combo_theme.setCurrentIndex(0 if theme != "dark" else 1)
        self._combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        form.addRow("主题", self._combo_theme)

        size = self._settings.value("editor/font_size", 11, type=int)
        self._spin_font = QSpinBox()
        self._spin_font.setRange(8, 28)
        self._spin_font.setValue(size)
        self._spin_font.setSuffix(" pt")
        self._spin_font.valueChanged.connect(self._on_pref_changed)
        form.addRow("编辑器字号", self._spin_font)

        tw = self._settings.value("editor/tab_width", 4, type=int)
        self._spin_tab = QSpinBox()
        self._spin_tab.setRange(2, 8)
        self._spin_tab.setValue(tw)
        self._spin_tab.valueChanged.connect(self._on_pref_changed)
        form.addRow("缩进宽度", self._spin_tab)

        root.addWidget(card)

        # === 外观 (Appearance) ===
        root.addWidget(self._section_label("外观"))
        root.addWidget(self._appearance_card())

        # === 运行 (Run) ===
        root.addWidget(self._section_label("运行"))
        root.addWidget(self._run_card())

        # === Python 环境 ===
        root.addWidget(self._section_label("Python 环境"))
        root.addWidget(self._env_card())

        root.addStretch()

        self.apply_theme(self._settings.value("theme", "light"))

        # 订阅环境变化以刷新下拉
        self._mw.env_ctrl.manager.environments_changed.connect(self._refresh_env_combo)
        self._mw.env_ctrl.manager.current_changed.connect(self._refresh_env_combo)

    def _section_label(self, text):
        lbl = QLabel(text)
        f = lbl.font()
        f.setPointSize(13)
        f.setBold(True)
        lbl.setFont(f)
        return lbl

    def _run_card(self):
        card = QFrame()
        card.setObjectName("settings_card")
        form = QFormLayout(card)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(10)

        cap = QCheckBox("捕获 matplotlib 图表到侧栏（关闭则用外部窗口）")
        cap.setChecked(self._settings.value("run/capture_figures", "1") != "0")
        cap.stateChanged.connect(
            lambda _st: self._settings.setValue(
                "run/capture_figures", "1" if cap.isChecked() else "0"))
        form.addRow(cap)
        return card

    # --- Python 环境管理 ---
    def _env_card(self):
        mgr = self._mw.env_ctrl.manager
        card = QFrame()
        card.setObjectName("settings_card")
        outer = QVBoxLayout(card)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        hint = QLabel(
            "选择运行用户代码所用的 Python 环境。可添加已有虚拟环境/解释器，"
            "或新建虚拟环境（Windows 与 Linux 均支持）。")
        hint.setWordWrap(True)
        outer.addWidget(hint)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(QLabel("当前环境"))
        self._env_combo = QComboBox()
        self._env_combo.setMinimumWidth(320)
        self._populate_env_combo()
        self._env_combo.currentIndexChanged.connect(self._on_env_selected)
        row.addWidget(self._env_combo, 1)
        outer.addLayout(row)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        b_add = QPushButton("添加现有…")
        b_new = QPushButton("新建…")
        b_pip = QPushButton("安装包…")
        b_remove = QPushButton("移除")
        b_add.clicked.connect(self._add_existing_env)
        b_new.clicked.connect(self._create_new_env)
        b_pip.clicked.connect(self._install_packages)
        b_remove.clicked.connect(self._remove_env)
        for b in (b_add, b_new, b_pip, b_remove):
            btns.addWidget(b)
        btns.addStretch()
        outer.addLayout(btns)
        return card

    def _populate_env_combo(self):
        mgr = self._mw.venv_manager
        self._env_combo.blockSignals(True)
        self._env_combo.clear()
        cur = mgr.current_id()
        select = 0
        for i, e in enumerate(mgr.all_environments()):
            ver = e.get("version") or ""
            label = f"{e.get('name', e['id'])} ({ver})" if ver else e.get("name", e["id"])
            if not e.get("valid", True):
                label += "  ⚠ 无效"
            self._env_combo.addItem(label, e["id"])
            if e["id"] == cur:
                select = i
        self._env_combo.setCurrentIndex(select)
        self._env_combo.blockSignals(False)

    def _refresh_env_combo(self, *_args):
        if hasattr(self, "_env_combo"):
            self._populate_env_combo()

    def _on_env_selected(self, _idx):
        env_id = self._env_combo.currentData()
        if env_id:
            self._mw.venv_manager.set_current(env_id)

    def _add_existing_env(self):
        self._mw.env_ctrl.add_existing()
        self._populate_env_combo()

    def _create_new_env(self):
        self._mw.env_ctrl.create_new()
        self._populate_env_combo()

    def _install_packages(self):
        self._mw.env_ctrl.install_packages()

    def _remove_env(self):
        mgr = self._mw.env_ctrl.manager
        cur = mgr.current_id()
        if cur == mgr.BASE_ID:
            QMessageBox.information(self, "提示", "内置环境不可移除。")
            return
        env = mgr.find(cur)
        name = env.get("name", cur) if env else cur
        btn = QMessageBox.question(
            self, "移除环境",
            f"从环境列表中移除「{name}」？\n（不会删除磁盘上的文件）",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if btn == QMessageBox.Yes:
            mgr.remove(cur)
            self._populate_env_combo()

    def _appearance_card(self):
        mw = self._mw
        card = QFrame()
        card.setObjectName("settings_card")
        form = QFormLayout(card)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(10)

        def chk(getter, setter, label):
            c = QCheckBox(label)
            c.setChecked(getter())
            c.stateChanged.connect(lambda _st, s=setter: s(c.isChecked()))
            return c

        form.addRow(chk(mw.is_menu_bar, mw.set_menu_bar, "显示菜单栏"))
        form.addRow(chk(mw.layout.is_primary_sidebar, mw.layout.set_primary_sidebar, "显示第一侧边栏（主侧边栏）"))
        form.addRow(chk(mw.layout.is_figures_dock, mw.layout.set_figures_dock, "显示图表栏（可拖拽停靠）"))
        form.addRow(chk(mw.layout.is_panel, mw.layout.set_panel, "显示输出面板（可拖拽停靠）"))
        form.addRow(chk(mw.is_status_bar, mw.set_status_bar, "显示状态栏"))

        form.addRow(self._section_label("视图"))
        form.addRow(chk(lambda: mw.layout.is_view_visible("explorer"),
                        lambda on: mw.layout.set_view_visible("explorer", on),
                        "显示文件浏览器"))
        return card

    def _on_theme_changed(self):
        theme = self._combo_theme.currentData()
        self._mw.theme_ctrl.set_theme(theme)

    def _on_pref_changed(self):
        self._settings.setValue("editor/font_size", self._spin_font.value())
        self._settings.setValue("editor/tab_width", self._spin_tab.value())
        self._mw._apply_editor_prefs_to_all()

    def apply_theme(self, theme_name):
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
        self.setStyleSheet(
            f"QWidget#settings_panel {{ background: {v['bg_main']}; }}"
            f"QFrame#settings_card {{ background: {v['bg_input']}; "
            f"border: 1px solid {v['border']}; border-radius: 8px; }}"
        )
        self._heading.setStyleSheet(f"color: {v['fg']};")
        self._sub.setStyleSheet(f"color: {v['fg_dim']}; font-size: 12px;")
