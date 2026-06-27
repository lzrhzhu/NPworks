from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
)


class BottomPanel(QWidget):
    def __init__(self, output_panel, parent=None):
        super().__init__(parent)
        self._output = output_panel
        self._terminal = None
        self._shell_terminal = None
        self._current_index = 0
        self._terminal_factory = None
        self._shell_factory = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("bottom_header")
        header.setFixedHeight(32)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 0, 8, 0)
        h_layout.setSpacing(0)

        self._btn_output = QPushButton("输出")
        self._btn_output.setObjectName("bottom_tab_btn")
        self._btn_output.setCheckable(True)
        self._btn_output.setChecked(True)
        self._btn_output.setCursor(Qt.PointingHandCursor)
        self._btn_output.clicked.connect(lambda: self._switch(0))
        h_layout.addWidget(self._btn_output)

        self._btn_terminal = QPushButton("IPython")
        self._btn_terminal.setObjectName("bottom_tab_btn")
        self._btn_terminal.setCheckable(True)
        self._btn_terminal.setCursor(Qt.PointingHandCursor)
        self._btn_terminal.clicked.connect(lambda: self._switch(1))
        h_layout.addWidget(self._btn_terminal)

        self._btn_shell = QPushButton("终端")
        self._btn_shell.setObjectName("bottom_tab_btn")
        self._btn_shell.setCheckable(True)
        self._btn_shell.setCursor(Qt.PointingHandCursor)
        self._btn_shell.clicked.connect(lambda: self._switch(2))
        h_layout.addWidget(self._btn_shell)

        h_layout.addStretch()
        layout.addWidget(header)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._output)
        self._stack.addWidget(QWidget())
        self._stack.addWidget(QWidget())
        layout.addWidget(self._stack)

        self._update_tab_style()

    def set_factories(self, terminal_factory, shell_factory):
        self._terminal_factory = terminal_factory
        self._shell_factory = shell_factory

    def ensure_terminal(self):
        self._ensure_terminal()

    def _ensure_terminal(self):
        if self._terminal is None and self._terminal_factory:
            self._terminal = self._terminal_factory()
            old = self._stack.widget(1)
            self._stack.removeWidget(old)
            old.deleteLater()
            self._stack.insertWidget(1, self._terminal)

    def ensure_shell(self):
        self._ensure_shell()

    def _ensure_shell(self):
        if self._shell_terminal is None and self._shell_factory:
            self._shell_terminal = self._shell_factory()
            old = self._stack.widget(2)
            self._stack.removeWidget(old)
            old.deleteLater()
            self._stack.insertWidget(2, self._shell_terminal)

    def _switch(self, index):
        if index == 1:
            self._ensure_terminal()
        elif index == 2:
            self._ensure_shell()
        self._current_index = index
        self._stack.setCurrentIndex(index)
        self._update_tab_style()
        if index == 1 and self._terminal:
            self._terminal.setFocus()
        elif index == 2 and self._shell_terminal:
            self._shell_terminal.setFocus()

    def _update_tab_style(self):
        self._btn_output.setChecked(self._current_index == 0)
        self._btn_terminal.setChecked(self._current_index == 1)
        self._btn_shell.setChecked(self._current_index == 2)

    def show_output_tab(self):
        self._switch(0)

    def show_terminal_tab(self):
        self._switch(1)

    def show_shell_tab(self):
        self._switch(2)

    @property
    def terminal(self):
        return self._terminal

    @property
    def shell_terminal(self):
        return self._shell_terminal
