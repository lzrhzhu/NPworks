import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextBrowser

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
