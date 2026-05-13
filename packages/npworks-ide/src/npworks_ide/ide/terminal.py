import io
import sys
import contextlib

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager


class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._kernel_manager = None
        self._kernel_client = None
        self._setup_kernel()
        self._setup_ui()

    def _setup_kernel(self):
        self._kernel_manager = QtInProcessKernelManager()
        self._kernel_manager.start_kernel()
        self._kernel_client = self._kernel_manager.client()
        self._kernel_client.start_channels()
        shell = self._kernel_manager.kernel.shell
        if shell is not None:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                shell.run_cell("%automagic on")
                shell.run_cell(
                    "import sys, os, numpy as np, scipy, matplotlib.pyplot as plt"
                )

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._jupyter_widget = RichJupyterWidget()
        self._jupyter_widget.kernel_manager = self._kernel_manager
        self._jupyter_widget.kernel_client = self._kernel_client
        self._jupyter_widget.font = QFont("Consolas", 11)
        self._jupyter_widget.syntax_style = "monokai"
        self._jupyter_widget.set_default_style(colors="Linux")
        self._jupyter_widget.setWindowTitle("IPython")
        self._jupyter_widget.executed.connect(self._on_executed)

        layout.addWidget(self._jupyter_widget)

    def _on_executed(self):
        pass

    def execute_command(self, code):
        code = code.strip()
        if not code:
            return
        self._jupyter_widget.execute(code)

    def cleanup(self):
        if self._kernel_client is not None:
            self._kernel_client.stop_channels()
        if self._kernel_manager is not None:
            self._kernel_manager.shutdown_kernel()

    def set_theme(self, theme_name):
        if theme_name == "dark":
            self._jupyter_widget.set_default_style(colors="Linux")
            self._jupyter_widget.syntax_style = "monokai"
            self._jupyter_widget.setStyleSheet(
                "RichJupyterWidget { background: #1E1E1E; color: #D4D4D4; }"
            )
        else:
            self._jupyter_widget.set_default_style(colors="LightBG")
            self._jupyter_widget.syntax_style = "default"
            self._jupyter_widget.setStyleSheet(
                "RichJupyterWidget { background: #FFFFFF; color: #1E1E1E; }"
            )
        self._jupyter_widget.font = QFont("Consolas", 11)

    def setFocus(self):
        self._jupyter_widget._control.setFocus()
