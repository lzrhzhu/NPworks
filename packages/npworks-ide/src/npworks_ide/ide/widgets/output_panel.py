import re

from PyQt5.QtCore import pyqtSignal, QSettings
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QImage
from PyQt5.QtWidgets import (
    QTextBrowser, QWidget, QHBoxLayout, QLineEdit,
    QPushButton, QVBoxLayout, QLabel, QFrame,
)

from npworks_ide.ide.themes import get_colors

_TRACEBACK_RE = re.compile(r'(File\s+"[^"]*",\s*line\s+)(\d+)')
_FIG_MARK = "__NPWORKS_FIG__:"


class OutputPanel(QWidget):
    jump_to_line = pyqtSignal(int)
    input_submitted = pyqtSignal(str)
    figure_ready = pyqtSignal(str)   # 捕获到 matplotlib 图：path

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("output_header")
        header.setFixedHeight(28)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        lbl = QLabel("  📟  输出")
        lbl.setObjectName("output_header_label")
        font = lbl.font()
        font.setBold(True)
        font.setPointSize(10)
        lbl.setFont(font)
        header_layout.addWidget(lbl)
        header_layout.addStretch()
        layout.addWidget(header)

        self._text = QTextBrowser()
        self._text.setObjectName("output_text")
        self._text.setReadOnly(True)
        self._text.setOpenLinks(False)
        self._text.setOpenExternalLinks(False)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self._text.setFont(font)
        self._text.anchorClicked.connect(self._on_anchor_clicked)
        layout.addWidget(self._text)

        self._input_row = QWidget()
        self._input_row.setObjectName("input_row")
        input_layout = QHBoxLayout(self._input_row)
        input_layout.setContentsMargins(8, 4, 8, 4)
        input_layout.setSpacing(6)

        self._input_label = QLabel("⌨ 输入:")
        self._input_label.setFixedWidth(52)
        input_layout.addWidget(self._input_label)

        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText("在此输入后按回车发送到程序...")
        input_layout.addWidget(self._input_field)

        self._send_btn = QPushButton("发送")
        self._send_btn.setFixedWidth(56)
        input_layout.addWidget(self._send_btn)

        self._input_row.setVisible(False)
        layout.addWidget(self._input_row)

        self._input_field.returnPressed.connect(self._on_input_submit)
        self._send_btn.clicked.connect(self._on_input_submit)

        self._out_buf = ""

    def _on_input_submit(self):
        text = self._input_field.text()
        if text:
            self.input_submitted.emit(text)
            self._input_field.clear()

    def show_input(self):
        self._input_row.setVisible(True)
        self._input_field.setFocus()

    def hide_input(self):
        self._input_row.setVisible(False)

    def append_stdout(self, text: str):
        self._out_buf += text
        parts = self._out_buf.split("\n")
        self._out_buf = parts[-1]
        for line in parts[:-1]:
            if line.startswith(_FIG_MARK):
                self.figure_ready.emit(line[len(_FIG_MARK):].strip())
            else:
                self._append_text(line + "\n")

    def flush_output(self):
        """运行结束时冲刷残留缓冲。"""
        if self._out_buf:
            line = self._out_buf
            self._out_buf = ""
            if line.startswith(_FIG_MARK):
                self.figure_ready.emit(line[len(_FIG_MARK):].strip())
            else:
                self._append_text(line + "\n")

    def _append_text(self, text: str):
        c = get_colors()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(c["foreground"]))
        cursor = self._text.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text, fmt)
        self._text.setTextCursor(cursor)
        self._text.ensureCursorVisible()

    def append_stderr(self, text: str):
        c = get_colors()
        base_fmt = QTextCharFormat()
        base_fmt.setForeground(QColor(204, 50, 50))

        parts = _TRACEBACK_RE.split(text)
        cursor = self._text.textCursor()
        cursor.movePosition(cursor.End)

        for i, part in enumerate(parts):
            if i % 3 == 2:
                link_fmt = QTextCharFormat(base_fmt)
                link_fmt.setAnchor(True)
                link_fmt.setAnchorHref(f"line:{part}")
                link_fmt.setFontUnderline(True)
                link_fmt.setToolTip(f"点击跳转到第 {part} 行")
                cursor.insertText(part, link_fmt)
            else:
                cursor.insertText(part, base_fmt)

        self._text.setTextCursor(cursor)
        self._text.ensureCursorVisible()

    def append_system(self, text: str):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(0, 120, 212))
        fmt.setFontItalic(True)
        cursor = self._text.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text + "\n", fmt)
        self._text.setTextCursor(cursor)
        self._text.ensureCursorVisible()

    def clear_output(self):
        self._text.clear()

    def _on_anchor_clicked(self, url):
        href = url.toString()
        if href.startswith("line:"):
            try:
                self.jump_to_line.emit(int(href.split(":")[1]))
            except (ValueError, IndexError):
                pass
