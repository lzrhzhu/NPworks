"""设置文档页面：以标签页形式呈现的设置（VS Code 风格），实时生效。"""
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox,
    QFrame,
)

from npworks_ide.ide.document_panel import DocumentPanel


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
        root.addStretch()

        self.apply_theme(self._settings.value("theme", "light"))

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
