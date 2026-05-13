from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QCheckBox, QShortcut, QFrame,
)


class FindReplacePanel(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._replace_visible = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(3)

        find_row = QHBoxLayout()
        find_row.setSpacing(6)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("查找内容...")
        self.find_input.setMinimumWidth(200)
        self.find_input.setMaximumWidth(360)
        find_row.addWidget(self.find_input)

        self.find_prev_btn = QPushButton(" ▲ ")
        self.find_prev_btn.setFixedWidth(32)
        self.find_prev_btn.setToolTip("上一个 (Shift+Enter)")
        find_row.addWidget(self.find_prev_btn)

        self.find_next_btn = QPushButton(" ▼ ")
        self.find_next_btn.setFixedWidth(32)
        self.find_next_btn.setToolTip("下一个 (Enter)")
        find_row.addWidget(self.find_next_btn)

        self.match_count_label = QLabel("")
        self.match_count_label.setMinimumWidth(50)
        find_row.addWidget(self.match_count_label)

        find_row.addStretch()

        self.case_check = QCheckBox("Aa")
        self.case_check.setToolTip("区分大小写")
        self.case_check.setFixedWidth(42)
        find_row.addWidget(self.case_check)

        self.replace_toggle_btn = QPushButton(" ▼ 替换")
        self.replace_toggle_btn.setFixedWidth(68)
        find_row.addWidget(self.replace_toggle_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setToolTip("关闭 (Escape)")
        find_row.addWidget(self.close_btn)

        layout.addLayout(find_row)

        self.replace_row_widget = QWidget()
        replace_layout = QHBoxLayout(self.replace_row_widget)
        replace_layout.setContentsMargins(0, 0, 0, 0)
        replace_layout.setSpacing(6)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("替换为...")
        self.replace_input.setMinimumWidth(200)
        self.replace_input.setMaximumWidth(360)
        replace_layout.addWidget(self.replace_input)

        self.replace_btn = QPushButton("替换")
        self.replace_btn.setFixedWidth(56)
        replace_layout.addWidget(self.replace_btn)

        self.replace_all_btn = QPushButton("全部替换")
        self.replace_all_btn.setFixedWidth(76)
        replace_layout.addWidget(self.replace_all_btn)

        replace_layout.addStretch()

        self.replace_row_widget.setVisible(False)
        layout.addWidget(self.replace_row_widget)

        self.find_input.returnPressed.connect(self.find_next_btn.click)
        self.replace_input.returnPressed.connect(self.replace_btn.click)
        self.close_btn.clicked.connect(self._on_close)
        self.replace_toggle_btn.clicked.connect(self._toggle_replace)
        self.find_input.textChanged.connect(self._on_text_changed)

        esc = QShortcut(Qt.Key_Escape, self)
        esc.activated.connect(self._on_close)

    def _toggle_replace(self):
        self._replace_visible = not self._replace_visible
        self.replace_row_widget.setVisible(self._replace_visible)
        if self._replace_visible:
            self.replace_toggle_btn.setText(" ▲ 替换")
            self.replace_input.setFocus()
        else:
            self.replace_toggle_btn.setText(" ▼ 替换")

    def _on_close(self):
        self.hide()
        self.closed.emit()

    def _on_text_changed(self):
        self.match_count_label.setText("")

    def show_find(self):
        self.show()
        self.find_input.setFocus()
        self.find_input.selectAll()

    def show_replace(self):
        self._replace_visible = True
        self.replace_row_widget.setVisible(True)
        self.replace_toggle_btn.setText(" ▲ 替换")
        self.show()
        self.find_input.setFocus()
        self.find_input.selectAll()

    def get_find_text(self):
        return self.find_input.text()

    def get_replace_text(self):
        return self.replace_input.text()

    def is_case_sensitive(self):
        return self.case_check.isChecked()

    def is_regex(self):
        return False

    def set_match_count(self, current, total):
        if total > 0:
            self.match_count_label.setText(f" {current}/{total} ")
        else:
            self.match_count_label.setText(" 无匹配 ")
