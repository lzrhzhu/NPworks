import os
import sys
import threading
import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QApplication, QScrollBar,
    QTabBar, QPushButton, QStackedWidget,
)

from winpty import PTY
import pyte


_PAD = 4
_HISTORY = 5000


class _TermView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._font = QFont("Consolas", 11)
        self.setFont(self._font)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self._pty = None
        self._screen = None

        fm = self.fontMetrics()
        self._cell_w = fm.horizontalAdvance("M")
        self._cell_h = fm.height()
        self._ascent = fm.ascent()

        self._bg = QColor("#0C0C0C")
        self._fg = QColor("#CCCCCC")

        self._cursor_on = True
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink)
        self._blink_timer.start(500)

        self._scroll_offset = 0

        self._vscroll = QScrollBar(Qt.Vertical, self)
        self._vscroll.setSingleStep(1)
        self._vscroll.setPageStep(20)
        self._vscroll.setMaximum(0)
        self._vscroll.setValue(0)
        self._vscroll.valueChanged.connect(self._on_scroll_value)

        self._sel_start = None
        self._sel_end = None
        self._selecting = False

    def _blink(self):
        self._cursor_on = not self._cursor_on
        self.update()

    def set_pty(self, pty):
        self._pty = pty

    def set_screen(self, screen):
        self._screen = screen

    def set_colors(self, bg, fg):
        self._bg = QColor(bg)
        self._fg = QColor(fg)
        self.update()

    def _on_scroll_value(self, value):
        self._scroll_offset = self._vscroll.maximum() - value
        self.update()

    def _sync_scrollbar(self):
        if self._screen is None:
            return
        max_s = self._max_scroll()
        self._vscroll.setMaximum(max_s)
        self._vscroll.setValue(max_s - self._scroll_offset)

    def render_screen(self):
        self._scroll_offset = 0
        self._sync_scrollbar()
        self._cursor_on = True
        self._blink_timer.start(500)
        self.update()

    def resizeEvent(self, event):
        sb_w = self._vscroll.sizeHint().width()
        self._vscroll.setGeometry(
            self.width() - sb_w, 0, sb_w, self.height())
        super().resizeEvent(event)
        parent = self.parent()
        while parent:
            if isinstance(parent, ShellTerminalWidget):
                parent._on_display_resize()
                break
            parent = parent.parent()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        steps = max(1, abs(delta) // 120) * 3
        if delta > 0:
            self._scroll_offset = min(
                self._scroll_offset + steps, self._max_scroll())
        else:
            self._scroll_offset = max(self._scroll_offset - steps, 0)
        self._sync_scrollbar()
        self.update()

    def _visible_rows(self):
        return max(1, (self.height() - 2 * _PAD) // self._cell_h)

    def _max_scroll(self):
        if self._screen is None:
            return 0
        total = len(self._screen.history.top) + self._screen.lines
        return max(0, total - self._visible_rows())

    def _build_line(self, row_data, columns):
        parts = []
        for col in range(columns):
            parts.append(row_data[col].data)
        return "".join(parts)

    def paintEvent(self, event):
        if self._screen is None:
            return

        p = QPainter(self)
        p.setFont(self._font)
        p.fillRect(self.rect(), self._bg)
        p.setPen(self._fg)

        history = list(self._screen.history.top)
        history_len = len(history)
        screen_lines = self._screen.lines
        columns = self._screen.columns
        total = history_len + screen_lines
        vis = self._visible_rows()

        if self._scroll_offset == 0:
            view_end = total
            view_start = total - vis
            cursor_total = history_len + self._screen.cursor.y
            if cursor_total < view_start:
                view_start = cursor_total
            view_start = max(0, view_start)
        else:
            view_end = total - self._scroll_offset
            view_start = view_end - vis
            if view_start < 0:
                view_start = 0
                view_end = min(vis, total)

        cursor_vis = -1
        if self._scroll_offset == 0:
            cursor_vis = history_len + self._screen.cursor.y - view_start

        sel_lines = self._selection_lines(view_start, view_end - view_start)

        for i in range(min(vis, view_end - view_start)):
            src = view_start + i
            if src < 0 or src >= total:
                continue
            if src < history_len:
                text = self._build_line(history[src], columns)
            else:
                text = self._build_line(
                    self._screen.buffer[src - history_len], columns)
            y = _PAD + self._ascent + i * self._cell_h

            if src in sel_lines:
                col_start, col_end = sel_lines[src]
                rx1 = _PAD + col_start * self._cell_w
                rx2 = _PAD + col_end * self._cell_w
                sel_color = QColor(self._fg)
                sel_color.setAlpha(40)
                p.fillRect(rx1, _PAD + i * self._cell_h, rx2 - rx1, self._cell_h, sel_color)

            p.drawText(_PAD, y, text)

        if (self._scroll_offset == 0
                and self._cursor_on
                and not self._screen.cursor.hidden
                and 0 <= cursor_vis < vis
                and 0 <= self._screen.cursor.x < columns):
            cx = self._screen.cursor.x
            rx = _PAD + cx * self._cell_w
            ry = _PAD + cursor_vis * self._cell_h
            cursor_w = max(2, self._cell_w // 8)
            p.fillRect(rx, ry, cursor_w, self._cell_h, self._fg)

        p.end()

    def _pos_to_cell(self, pos):
        col = (pos.x() - _PAD) // self._cell_w
        vis = self._visible_rows()
        row = (pos.y() - _PAD) // self._cell_h
        if self._screen is None:
            return -1, -1, -1
        history_len = len(self._screen.history.top)
        total = history_len + self._screen.lines
        if self._scroll_offset == 0:
            abs_row = total - vis + row
        else:
            abs_row = total - self._scroll_offset - vis + row
        return abs_row, col, row

    def _selection_lines(self, view_start, count):
        if self._sel_start is None or self._sel_end is None:
            return {}
        r1, c1 = self._sel_start
        r2, c2 = self._sel_end
        if r1 > r2 or (r1 == r2 and c1 > c2):
            r1, c1, r2, c2 = r2, c2, r1, c1
        if self._screen is None:
            return {}
        columns = self._screen.columns
        result = {}
        for row in range(max(r1, view_start), min(r2 + 1, view_start + count)):
            cs = c1 if row == r1 else 0
            ce = c2 + 1 if row == r2 else columns
            cs = max(0, min(cs, columns))
            ce = max(0, min(ce, columns))
            if cs < ce:
                result[row] = (cs, ce)
        return result

    def _get_selection_text(self):
        if self._sel_start is None or self._sel_end is None or self._screen is None:
            return ""
        r1, c1 = self._sel_start
        r2, c2 = self._sel_end
        if r1 > r2 or (r1 == r2 and c1 > c2):
            r1, c1, r2, c2 = r2, c2, r1, c1
        history = list(self._screen.history.top)
        history_len = len(history)
        columns = self._screen.columns
        lines = []
        for row in range(r1, r2 + 1):
            if row < history_len:
                line_text = self._build_line(history[row], columns)
            elif row - history_len < self._screen.lines:
                line_text = self._build_line(
                    self._screen.buffer[row - history_len], columns)
            else:
                continue
            cs = c1 if row == r1 else 0
            ce = c2 + 1 if row == r2 else columns
            lines.append(line_text[cs:ce])
        return "\n".join(lines)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            abs_row, col, _ = self._pos_to_cell(event.pos())
            self._sel_start = (abs_row, col)
            self._sel_end = (abs_row, col)
            self._selecting = True
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._selecting and event.buttons() & Qt.LeftButton:
            abs_row, col, _ = self._pos_to_cell(event.pos())
            self._sel_end = (abs_row, col)
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._selecting = False
            text = self._get_selection_text()
            if text:
                QApplication.clipboard().setText(text)
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if self._pty is None:
            return
        text = event.text()
        key = event.key()
        mods = event.modifiers()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._pty.write("\r")
        elif key == Qt.Key_Backspace:
            self._pty.write("\x08")
        elif key == Qt.Key_Tab:
            self._pty.write("\t")
        elif key == Qt.Key_Up:
            self._pty.write("\x1b[A")
        elif key == Qt.Key_Down:
            self._pty.write("\x1b[B")
        elif key == Qt.Key_Right:
            self._pty.write("\x1b[C")
        elif key == Qt.Key_Left:
            self._pty.write("\x1b[D")
        elif key == Qt.Key_Home:
            self._pty.write("\x1b[H")
        elif key == Qt.Key_End:
            self._pty.write("\x1b[F")
        elif key == Qt.Key_Delete:
            self._pty.write("\x1b[3~")
        elif key == Qt.Key_PageUp and mods & Qt.ShiftModifier:
            self._scroll_offset = min(
                self._scroll_offset + 20, self._max_scroll())
            self._sync_scrollbar()
            self.update()
        elif key == Qt.Key_PageDown and mods & Qt.ShiftModifier:
            self._scroll_offset = max(self._scroll_offset - 20, 0)
            self._sync_scrollbar()
            self.update()
        elif mods & Qt.ControlModifier and mods & Qt.ShiftModifier and key == Qt.Key_V:
            self._paste()
        elif mods & Qt.ControlModifier:
            ctrl_map = {
                Qt.Key_C: "\x03", Qt.Key_D: "\x04",
                Qt.Key_L: "\x0c", Qt.Key_Z: "\x1a",
                Qt.Key_A: "\x01", Qt.Key_E: "\x05",
                Qt.Key_U: "\x15", Qt.Key_K: "\x0b", Qt.Key_W: "\x17",
            }
            seq = ctrl_map.get(key)
            if seq:
                self._pty.write(seq)
            elif text:
                self._pty.write(text)
        elif text:
            self._pty.write(text)

    def _paste(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text and self._pty:
            self._pty.write(text)


class ShellTerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pty = None
        self._reader_thread = None
        self._running = False
        self._screen = None
        self._stream = None
        self._read_buffer = ""
        self._buffer_lock = threading.Lock()
        self._data_pending = False
        self._setup_ui()
        self._start_pty()

        self._render_timer = QTimer(self)
        self._render_timer.timeout.connect(self._on_render_tick)
        self._render_timer.start(30)

        QTimer.singleShot(100, self._on_display_resize)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._display = _TermView(self)
        layout.addWidget(self._display)

    def _calc_size(self):
        if self._display is None:
            return 120, 30
        dw = self._display.width() - _PAD * 2
        dh = self._display.height() - _PAD * 2
        cols = max(1, dw // self._display._cell_w)
        rows = max(1, dh // self._display._cell_h)
        return cols, rows

    def _on_display_resize(self):
        if self._pty is None or self._screen is None:
            return
        cols, rows = self._calc_size()
        if cols != self._screen.columns or rows != self._screen.lines:
            self._screen.resize(cols, rows)
            try:
                self._pty.set_size(cols, rows)
            except Exception:
                pass

    def _start_pty(self):
        cols = 120
        rows = 30
        self._pty = PTY(cols, rows)
        if sys.platform == "win32":
            ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            if os.path.exists(ps_path):
                self._pty.spawn(ps_path, cmdline="-NoLogo -NoProfile")
            else:
                self._pty.spawn("cmd.exe")
        else:
            self._pty.spawn("/bin/bash")

        self._screen = pyte.HistoryScreen(cols, rows, history=_HISTORY)
        self._screen.set_mode(pyte.modes.LNM)
        self._stream = pyte.Stream(self._screen)
        self._display.set_pty(self._pty)
        self._display.set_screen(self._screen)

        self._running = True
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def _reader_loop(self):
        while self._running:
            try:
                data = self._pty.read()
                if data:
                    with self._buffer_lock:
                        self._read_buffer += data
                    self._data_pending = True
            except OSError:
                break
            except Exception:
                time.sleep(0.1)
                continue
            time.sleep(0.005)

    def _on_render_tick(self):
        with self._buffer_lock:
            data = self._read_buffer
            self._read_buffer = ""
        if data:
            self._stream.feed(data)
            self._data_pending = False
            self._display.render_screen()
        elif self._data_pending:
            self._data_pending = False
            self._display.render_screen()

    def execute_command(self, code):
        for line in code.splitlines():
            line = line.strip()
            if line:
                self._pty.write(line + "\r")

    def set_theme(self, theme_name):
        if theme_name == "dark":
            self._display.set_colors("#0C0C0C", "#CCCCCC")
        else:
            self._display.set_colors("#FFFFFF", "#1E1E1E")

    def setFocus(self):
        self._display.render_screen()
        self._display.setFocus()

    def cleanup(self):
        self._running = False
        self._render_timer.stop()
        if self._pty is not None:
            try:
                self._pty.write("exit\r")
            except Exception:
                pass


class TerminalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._terminals = []
        self._counter = 0
        self._setup_ui()
        self.add_terminal()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(30)
        h = QHBoxLayout(header)
        h.setContentsMargins(4, 0, 4, 0)
        h.setSpacing(2)

        self._tab_bar = QTabBar()
        self._tab_bar.setDocumentMode(True)
        self._tab_bar.setTabsClosable(True)
        self._tab_bar.setExpanding(False)
        self._tab_bar.setDrawBase(False)
        self._tab_bar.currentChanged.connect(self._on_tab_changed)
        self._tab_bar.tabCloseRequested.connect(self.close_terminal)
        h.addWidget(self._tab_bar)

        add_btn = QPushButton("+")
        add_btn.setObjectName("terminal_add_btn")
        add_btn.setFixedSize(26, 26)
        add_btn.setToolTip("新建终端")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_terminal)
        h.addWidget(add_btn)

        h.addStretch()

        layout.addWidget(header)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

    def _on_tab_changed(self, index):
        if 0 <= index < len(self._terminals):
            self._stack.setCurrentIndex(index)
            self._terminals[index].setFocus()

    def add_terminal(self):
        self._counter += 1
        name = f"pwsh {self._counter}"
        t = ShellTerminalWidget(self)
        self._terminals.append(t)
        self._stack.addWidget(t)
        self._tab_bar.addTab(name)
        self._tab_bar.setCurrentIndex(len(self._terminals) - 1)

    def close_terminal(self, index=None):
        if index is None:
            index = self._tab_bar.currentIndex()
        if index < 0 or index >= len(self._terminals):
            return
        if len(self._terminals) <= 1:
            return

        t = self._terminals.pop(index)
        self._tab_bar.removeTab(index)
        self._stack.removeWidget(t)
        t.cleanup()
        t.deleteLater()

        if self._tab_bar.currentIndex() < 0 and self._terminals:
            self._tab_bar.setCurrentIndex(min(index, len(self._terminals) - 1))

    def current_terminal(self):
        idx = self._tab_bar.currentIndex()
        if 0 <= idx < len(self._terminals):
            return self._terminals[idx]
        return None

    def execute_command(self, code):
        t = self.current_terminal()
        if t:
            t.execute_command(code)

    def set_theme(self, name):
        for t in self._terminals:
            t.set_theme(name)

    def setFocus(self):
        t = self.current_terminal()
        if t:
            t.setFocus()

    def cleanup(self):
        for t in self._terminals:
            t.cleanup()
        self._terminals.clear()
