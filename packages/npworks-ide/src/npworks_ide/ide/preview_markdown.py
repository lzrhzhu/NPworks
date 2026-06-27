import os

from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextBrowser, QSplitter, QWidget, QVBoxLayout

from npworks_ide.ide.editor_registry import EditorView

_MD_EXTS = {".md", ".markdown", ".mkd"}


def is_markdown_file(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in _MD_EXTS


def _md_to_html(text: str) -> str:
    try:
        import markdown
        return markdown.markdown(text, extensions=["extra", "codehilite", "toc"])
    except ImportError:
        pass

    html_lines = ["<html><body><pre style='white-space:pre-wrap;font-family:Consolas,monospace;'>"]
    for line in text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").splitlines():
        html_lines.append(line)
    html_lines.append("</pre></body></html>")
    return "\n".join(html_lines)


_CSS = """
body {
    font-family: 'Segoe UI', -apple-system, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    padding: 16px 24px;
    color: #D4D4D4;
    background: #1E1E1E;
}
h1, h2, h3, h4, h5, h6 { color: #569CD6; margin-top: 1.2em; }
h1 { border-bottom: 1px solid #3C3C3C; padding-bottom: 8px; }
h2 { border-bottom: 1px solid #3C3C3C; padding-bottom: 6px; }
a { color: #4EC9B0; }
code { background: #2D2D2D; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; font-size: 13px; }
pre { background: #2D2D2D; padding: 12px; border-radius: 4px; overflow-x: auto; }
pre code { background: transparent; padding: 0; }
blockquote { border-left: 3px solid #0078D4; margin-left: 0; padding-left: 12px; color: #999999; }
table { border-collapse: collapse; margin: 8px 0; }
th, td { border: 1px solid #3C3C3C; padding: 6px 12px; }
th { background: #2D2D2D; }
img { max-width: 100%; }
"""


class MarkdownPreview(QTextBrowser):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._path = file_path
        self.setOpenExternalLinks(True)
        self.setFont(QFont("Segoe UI", 10))

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            text = f"无法读取文件: {file_path}"

        html = _md_to_html(text)
        full = f"<html><head><style>{_CSS}</style></head><body>{html}</body></html>"
        self.setHtml(full)

    @property
    def file_path(self):
        return self._path

    def set_markdown_text(self, text: str):
        html = _md_to_html(text)
        full = f"<html><head><style>{_CSS}</style></head><body>{html}</body></html>"
        self.setHtml(full)


class MarkdownSplitView(QWidget, EditorView):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._path = file_path
        self.file_path_prop = file_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = QSplitter(Qt.Horizontal, self)
        self._splitter.setHandleWidth(2)

        from npworks_ide.ide.editor import CodeEditor
        self._editor = CodeEditor(self._splitter)
        self._editor.file_path = file_path
        self._editor._setup_folding()
        try:
            from PyQt5.Qsci import QsciLexerMarkdown
            self._md_lexer = QsciLexerMarkdown(self._editor)
            self._md_lexer.setFont(QFont("Consolas", 11))
            self._editor.setLexer(self._md_lexer)
        except ImportError:
            self._editor.setLexer(None)

        self._preview = QTextBrowser(self._splitter)
        self._preview.setOpenExternalLinks(True)
        self._preview.setFont(QFont("Segoe UI", 10))

        self._splitter.addWidget(self._editor)
        self._splitter.addWidget(self._preview)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([500, 500])

        layout.addWidget(self._splitter)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            text = f"无法读取文件: {file_path}"

        self._editor.set_code(text)
        self._original_text = text
        self._update_preview(text)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self._on_timer)

        self._editor.textChanged.connect(self._schedule_update)

    @property
    def file_path(self):
        return self._path

    def _schedule_update(self):
        self._timer.start()

    def _on_timer(self):
        text = self._editor.text()
        self._update_preview(text)

    def _update_preview(self, text: str):
        html = _md_to_html(text)
        full = f"<html><head><style>{_CSS}</style></head><body>{html}</body></html>"
        self._preview.setHtml(full)

    def get_editor(self):
        return self._editor

    def is_modified(self):
        return self._editor.isModified()

    def get_code(self):
        return self._editor.text()

    def save_content(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                f.write(self._editor.text())
            self._original_text = self._editor.text()
            self._editor.setModified(False)
            return True
        except Exception:
            return False

    # --- EditorView 接口 ---
    def editor_title(self):
        return os.path.basename(self._path)

    def is_modified(self):
        return self._editor.isModified()

    def is_readonly(self):
        return False

    def save(self):
        return self.save_content()

    def apply_theme(self, theme_name):
        self._editor.apply_theme()

    def apply_editor_prefs(self):
        self._editor.apply_editor_prefs()
