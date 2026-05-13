import keyword
import builtins
import os

from PyQt5.QtCore import Qt, QMimeData, QUrl, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.Qsci import (
    QsciScintilla, QsciLexerPython, QsciAPIs,
    QsciScintillaBase,
)

from npworks_ide.ide.theme import get_colors


_COMPLETION_WORDS = sorted(set(
    keyword.kwlist
    + list(dir(builtins))
    + [
        "self", "True", "False", "None",
        "print", "range", "len", "int", "float", "str", "list", "dict", "tuple", "set",
        "append", "extend", "insert", "remove", "pop", "sort", "reverse",
        "keys", "values", "items", "get", "update",
        "numpy", "np", "scipy", "matplotlib", "plt",
    ]
))


class PythonLexer(QsciLexerPython):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_colors()

    def _apply_colors(self):
        c = get_colors()
        self.setDefaultColor(QColor(c["foreground"]))
        self.setDefaultPaper(QColor(c["background"]))
        self.setColor(QColor(c["foreground"]))
        self.setPaper(QColor(c["background"]))
        self._set_style_color(c["keyword"], QsciLexerPython.Keyword)
        self._set_style_color(c["class_"], QsciLexerPython.ClassName)
        self._set_style_color(c["function"], QsciLexerPython.FunctionMethodName)
        self._set_style_color(c["builtin"], QsciLexerPython.HighlightedIdentifier)
        self._set_style_color(c["decorator"], QsciLexerPython.Decorator)
        self._set_style_color(c["string"], QsciLexerPython.DoubleQuotedString)
        self._set_style_color(c["string"], QsciLexerPython.SingleQuotedString)
        self._set_style_color(c["string"], QsciLexerPython.TripleDoubleQuotedString)
        self._set_style_color(c["string"], QsciLexerPython.TripleSingleQuotedString)
        self._set_style_color(c["comment"], QsciLexerPython.Comment)
        self._set_style_color(c["comment"], QsciLexerPython.CommentBlock)
        self._set_style_color(c["number"], QsciLexerPython.Number)
        self._set_style_color(c["operator"], QsciLexerPython.Operator)
        self.setFont(QFont("Consolas", 11))

    def _set_style_color(self, color_tuple, style_id):
        color, bold, italic = color_tuple
        self.setColor(QColor(color), style_id)
        font = QFont("Consolas", 11)
        if bold:
            font.setBold(True)
        if italic:
            font.setItalic(True)
        self.setFont(font, style_id)

    def refresh_theme(self):
        self._apply_colors()


class CodeEditor(QsciScintilla):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._original_code = ""
        self._file_path = None
        self._chapter_id = None
        self._section_filename = None
        self._tab_title = "未命名"

        self._setup_editor()
        self._setup_lexer()
        self._setup_api()
        self._setup_folding()
        self._apply_theme()

        self.setAcceptDrops(True)
        self.SCN_CHARADDED.connect(self._on_char_added)

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    @property
    def tab_title(self):
        return self._tab_title

    @tab_title.setter
    def tab_title(self, value):
        self._tab_title = value

    def _setup_editor(self):
        self.setFont(QFont("Consolas", 11))
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationGuidesBackgroundColor(QColor("#E0E0E0"))
        self.setIndentationGuidesForegroundColor(QColor("#E0E0E0"))
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, "0000")
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setMatchedBraceBackgroundColor(QColor("#FFD700"))
        self.setMatchedBraceForegroundColor(QColor("#000000"))
        self.setUnmatchedBraceBackgroundColor(QColor("#FF0000"))
        self.setUnmatchedBraceForegroundColor(QColor("#FFFFFF"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#F3F3F3"))
        self.setEdgeMode(QsciScintilla.EdgeNone)
        self.setEolMode(QsciScintilla.EolUnix)
        self.setWrapMode(QsciScintilla.WrapNone)
        self.setWhitespaceVisibility(QsciScintilla.WsInvisible)
        self.setAnnotationDisplay(QsciScintilla.AnnotationHidden)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
        self.setAutoCompletionCaseSensitivity(False)
        self.setSelectionBackgroundColor(QColor("#ADD6FF"))
        self.setSelectionForegroundColor(QColor("#000000"))
        self.SendScintilla(QsciScintillaBase.SCI_SETMULTIPLESELECTION, 0)
        self.SendScintilla(QsciScintillaBase.SCI_SETVIRTUALSPACEOPTIONS, 0)
        self.set_extra_actions()

    def _setup_lexer(self):
        self._lexer = PythonLexer(self)
        self.setLexer(self._lexer)

    def _setup_api(self):
        self._apis = QsciAPIs(self._lexer)
        for word in _COMPLETION_WORDS:
            self._apis.add(word)
        self._apis.prepare()

    def _setup_folding(self):
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)
        self.setMarginWidth(2, 16)
        self.setMarginType(2, QsciScintilla.SymbolMargin)
        self.setFoldMarginColors(QColor("#F8F8F8"), QColor("#F8F8F8"))
        self.setMarkerBackgroundColor(QColor("#0078D4"), QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerForegroundColor(QColor("#FFFFFF"), QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerBackgroundColor(QColor("#0078D4"), QsciScintilla.SC_MARKNUM_FOLDER)
        self.setMarkerForegroundColor(QColor("#FFFFFF"), QsciScintilla.SC_MARKNUM_FOLDER)

    def set_extra_actions(self):
        self._comment_action = None

    def _apply_theme(self):
        c = get_colors()
        self.setCaretForegroundColor(QColor(c["foreground"]))
        self.setCaretLineBackgroundColor(QColor(c["current_line"]))
        self.setSelectionBackgroundColor(QColor(c["selection_bg"]))
        self.setFoldMarginColors(QColor(c["line_number_bg"]), QColor(c["line_number_bg"]))
        self.setMarginBackgroundColor(0, QColor(c["line_number_bg"]))
        self.setMarginsForegroundColor(QColor(c["line_number_fg"]))
        is_dark = c.get("background") in ("#1E1E1E",)
        if not is_dark:
            self.setIndentationGuidesBackgroundColor(QColor("#E8E8E8"))
            self.setIndentationGuidesForegroundColor(QColor("#D0D0D0"))
        else:
            self.setIndentationGuidesBackgroundColor(QColor("#333333"))
            self.setIndentationGuidesForegroundColor(QColor("#444444"))
        self._lexer.refresh_theme()
        self.setMarkerBackgroundColor(
            QColor(c["line_number_fg_current"]), QsciScintilla.SC_MARKNUM_FOLDEROPEN
        )
        self.setMarkerBackgroundColor(
            QColor(c["line_number_fg_current"]), QsciScintilla.SC_MARKNUM_FOLDER
        )

    def apply_theme(self):
        self._apply_theme()

    def set_code(self, code: str, original: str = None):
        self.setText(code)
        self._original_code = original if original is not None else code
        self.setModified(False)

    def get_code(self) -> str:
        return self.text()

    def reset_to_original(self):
        self.setText(self._original_code)
        self.setModified(False)

    def get_cursor_line(self) -> int:
        return self.getCursorPosition()[0]

    def get_cursor_col(self) -> int:
        return self.getCursorPosition()[1]

    def set_cursor_pos(self, line: int, col: int = 0):
        self.setCursorPosition(line, col)
        self.ensureLineVisible(line)

    def get_selected_text(self) -> str:
        return self.selectedText()

    def has_selection(self) -> bool:
        return self.hasSelectedText()

    def is_modified(self) -> bool:
        return self.isModified()

    def _on_char_added(self, char):
        pass

    def toggle_comment(self):
        line_from, _, line_to, _ = self.getSelection()
        if line_from < 0:
            line_from = self.getCursorPosition()[0]
            line_to = line_from
        else:
            if line_to < line_from:
                line_from, line_to = line_to, line_from

        lines = []
        all_commented = True
        for i in range(line_from, line_to + 1):
            text = self.text(i).rstrip("\n").rstrip("\r")
            lines.append(text)
            if not text.lstrip().startswith("#"):
                all_commented = False

        self.beginUndoAction()
        for i, text in zip(range(line_from, line_to + 1), lines):
            if all_commented:
                stripped = text.lstrip()
                indent = text[: len(text) - len(stripped)]
                if stripped.startswith("# "):
                    new_text = indent + stripped[2:]
                elif stripped.startswith("#"):
                    new_text = indent + stripped[1:]
                else:
                    new_text = text
            else:
                stripped = text.lstrip()
                indent = text[: len(text) - len(stripped)]
                if stripped.startswith("#"):
                    new_text = text
                else:
                    new_text = indent + "# " + stripped
            self.setSelection(i, 0, i, self.lineLength(i))
            self.replaceSelectedText(new_text)
        self.endUndoAction()
        self.setCursorPosition(line_to, 0)

    def keyPressEvent(self, event):
        ctrl = event.modifiers() & Qt.ControlModifier
        shift = event.modifiers() & Qt.ShiftModifier
        key = event.key()

        if ctrl and key == Qt.Key_Slash:
            self.toggle_comment()
            return
        if ctrl and shift and key == Qt.Key_Slash:
            self.toggle_comment()
            return

        if key == Qt.Key_Return:
            super().keyPressEvent(event)
            self._smart_indent_after_enter()
            return

        if key == Qt.Key_Backspace and not self.hasSelectedText():
            line, col = self.getCursorPosition()
            if col > 0:
                text_before = self.text(line)[:col]
                if text_before and not text_before.strip():
                    spaces = len(text_before)
                    remove = spaces % 4
                    if remove == 0:
                        remove = 4
                    self.SendScintilla(
                        QsciScintillaBase.SCI_DELLINELEFT,
                    )
                    indent = " " * (spaces - remove)
                    self.insert(indent)
                    self.setCursorPosition(line, spaces - remove)
                    return

        super().keyPressEvent(event)

    def _smart_indent_after_enter(self):
        line, col = self.getCursorPosition()
        target_line = line - 1
        if target_line < 0:
            return
        prev_text = self.text(target_line).strip()
        if prev_text.endswith(":"):
            self.insert("    ")
            self.setCursorPosition(line, col + 4)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                path = url.toLocalFile()
                if path and path.endswith(".py"):
                    event.acceptProposedAction()
                    self.file_dropped.emit(path)
                    return
        super().dropEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and path.endswith(".py"):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and path.endswith(".py"):
                    event.acceptProposedAction()
                    return
        super().dragMoveEvent(event)
