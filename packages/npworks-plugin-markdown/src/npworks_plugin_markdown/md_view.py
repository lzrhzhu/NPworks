"""Markdown 分栏视图（左编辑 + 右预览）与 provider。

预览优先使用 QWebEngineView（Chromium）：支持 LaTeX(MathJax)、相对图片、
pygments 代码高亮；若未安装 WebEngine 则回退到 QTextBrowser。
"""
import os
import re

from PyQt5.QtCore import Qt, QTimer, QSettings, QUrl
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QTextBrowser, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QButtonGroup,
)

from npworks_ide.ide.editor_registry import EditorView, EditorProvider


MODE_SOURCE = "source"
MODE_SPLIT = "split"
MODE_PREVIEW = "preview"


def _webengine_classes():
    """惰性导入 WebEngine；offscreen/未安装时返回 None。"""
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
        return QWebEngineView, QWebEngineSettings
    except Exception:
        return None


def _strip_bt_prefix(line):
    s = line.lstrip()
    if s.startswith(">"):
        s = s[1:]
        if s.startswith(" "):
            s = s[1:]
        return s
    return line


def _unwrap_blockquote_fences(text):
    """把"引用块内的围栏代码"解包为顶层围栏代码块。

    python-markdown 不支持 blockquote 里的 ``` 围栏（会把围栏当行内代码）。
    教材常用 `>` 引用块包裹整段代码示例，这里剥掉 `>` 前缀使其成为正常围栏代码。
    """
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith(">"):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith(">"):
                j += 1
            run = lines[i:j]
            depref = [_strip_bt_prefix(l) for l in run]
            first = next((l for l in depref if l.strip()), "")
            if first.startswith("```") or first.startswith("~~~"):
                out.extend(depref)
            else:
                out.extend(run)
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def _preprocess_for_markdown(text):
    """保护代码块（markdown 仍渲染），并把 $...$/$$...$$ 替换为占位符，
    使其穿过 markdown 处理而不被转义（避免反斜杠被吞）。返回 (text, math_stash)。"""
    text = _unwrap_blockquote_fences(text)
    code_stash = []
    math_stash = []   # list of ("inline"|"display", latex)

    def keep_code(m):
        code_stash.append(m.group(0))
        return f"\x00C{len(code_stash) - 1}\x00"

    def keep_math(kind):
        def _f(m):
            math_stash.append((kind, m.group(1)))
            return f"\x00M{len(math_stash) - 1}\x00"
        return _f

    text = re.sub(r"```.*?```", keep_code, text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", keep_code, text, flags=re.S)
    text = re.sub(r"`[^`]*`", keep_code, text)
    text = re.sub(r"\$\$(.+?)\$\$", keep_math("display"), text, flags=re.S)
    text = re.sub(r"(?<!\$)\$([^\$\n]+?)\$(?!\$)", keep_math("inline"), text)
    # 代码占位符还原（让 markdown 正常渲染代码块）
    text = re.sub(r"\x00C(\d+)\x00", lambda m: code_stash[int(m.group(1))], text)
    return text, math_stash


def _restore_math(html_str, math_stash):
    """markdown 之后把数学占位符还原为带 MathJax 分隔符的 HTML。"""
    import html as _html

    def repl(m):
        kind, latex = math_stash[int(m.group(1))]
        latex = _html.escape(latex)   # 转义 < > &，但保留反斜杠
        if kind == "display":
            return f'<div class="math-display">\\[{latex}\\]</div>'
        return f'<span class="math-inline">\\({latex}\\)</span>'

    return re.sub(r"\x00M(\d+)\x00", repl, html_str)


def _md_body(text):
    import html as _html
    text, math_stash = _preprocess_for_markdown(text)
    try:
        import markdown
        html = markdown.markdown(
            text,
            extensions=["extra", "codehilite", "toc", "sane_lists", "tables"],
            extension_configs={"codehilite": {"guess_lang": False}},
        )
    except Exception:
        html = "<pre>" + _html.escape(text) + "</pre>"
    return _restore_math(html, math_stash)


def _pygments_css():
    try:
        from pygments.formatters import HtmlFormatter
        return HtmlFormatter(style="default").get_style_defs(".codehilite")
    except Exception:
        return ""


_CSS = """
body { font-family:'Segoe UI',-apple-system,sans-serif; font-size:16px; line-height:1.75;
       padding:24px 40px; color:#1a1a1a; background:#ffffff; max-width:980px; margin:0 auto; }
p,li { color:#1a1a1a; }
a { color:#0066cc; }
h1,h2,h3,h4,h5,h6 { color:#000000; margin-top:1.4em; margin-bottom:0.4em; line-height:1.3; }
h1 { font-size:1.9em; font-weight:700; border-bottom:2px solid #e0e0e0; padding-bottom:8px; }
h2 { font-size:1.5em; font-weight:700; border-bottom:1px solid #e8e8e8; padding-bottom:6px; }
h3 { font-size:1.25em; font-weight:700; }
h4 { font-size:1.1em; font-weight:700; }
h5 { font-size:1.0em; font-weight:700; }
h6 { font-size:0.95em; font-weight:700; color:#444; }
code { background:#f4f4f4; padding:2px 6px; border-radius:3px; font-family:Consolas,'Cascadia Code',monospace; font-size:13px; color:#b00020; }
pre { background:#f7f7f9; padding:14px 16px; border-radius:6px; overflow-x:auto; border:1px solid #e2e2e2; }
pre code { background:transparent; padding:0; color:#222; }
.codehilite { background:#f7f7f9; border-radius:6px; }
blockquote { border-left:4px solid #c0c0c0; margin-left:0; padding:4px 16px; color:#555; background:#fafafa; }
table { border-collapse:collapse; margin:12px 0; display:block; overflow-x:auto; }
th,td { border:1px solid #d0d0d0; padding:6px 14px; }
th { background:#f0f0f0; color:#000; }
img { max-width:100%; }
.math-display { margin:1.2em 0; text-align:center; }
"""

_MATHJAX = """
<script>
window.MathJax = {
  tex: { inlineMath: [['\\\\(','\\\\)']], displayMath: [['\\\\[','\\\\]']] },
  options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
"""


def build_html(text, base_url=""):
    body = _md_body(text)
    return (
        "<html><head><meta charset='utf-8'>"
        f"<base href='{base_url}'>"
        f"<style>{_pygments_css()}{_CSS}</style>"
        f"{_MATHJAX}"
        f"</head><body>{body}</body></html>"
    )


class MarkdownSplitView(QWidget, EditorView):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self._path = file_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 模式工具栏：源码 / 分栏 / 预览
        self._mode_bar = QWidget()
        self._mode_bar.setObjectName("md_mode_bar")
        self._mode_bar.setFixedHeight(30)
        mbl = QHBoxLayout(self._mode_bar)
        mbl.setContentsMargins(8, 0, 8, 0)
        mbl.setSpacing(4)
        self._mode_group = QButtonGroup(self)
        self._mode_group.setExclusive(True)
        self._mode_buttons = {}
        for key, text in ((MODE_SOURCE, "源码"), (MODE_SPLIT, "分栏"), (MODE_PREVIEW, "预览")):
            b = QPushButton(text)
            b.setObjectName("md_mode_btn")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=key: self._set_mode(k))
            self._mode_group.addButton(b)
            self._mode_buttons[key] = b
            mbl.addWidget(b)
        mbl.addStretch()
        layout.addWidget(self._mode_bar)

        self._splitter = QSplitter(Qt.Horizontal, self)
        self._splitter.setHandleWidth(2)

        from npworks_ide.ide.editor import CodeEditor
        self._editor = CodeEditor(self._splitter)
        self._editor.file_path = file_path
        self._editor._setup_folding()
        try:
            from PyQt5.Qsci import QsciLexerMarkdown
            self._md_lexer = QsciLexerMarkdown(self._editor)
            self._style_md_lexer()
            self._editor.setLexer(self._md_lexer)
        except ImportError:
            self._md_lexer = None
            self._editor.setLexer(None)

        we = _webengine_classes()
        if we is not None:
            QWebEngineView, QWebEngineSettings = we
            self._preview = QWebEngineView(self._splitter)
            self._preview.settings().setAttribute(
                QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            try:
                self._preview.page().setBackgroundColor(QColor("#ffffff"))
            except Exception:
                pass
        else:
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
        self._preview_ready = False   # 源码模式下不预渲染，点"分栏/预览"才构建

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self._on_timer)
        self._editor.textChanged.connect(lambda: self._timer.start())

        saved = QSettings("npworks", "npworks").value("markdown/view_mode", MODE_SOURCE)
        self._set_mode(saved if saved in (MODE_SOURCE, MODE_SPLIT, MODE_PREVIEW) else MODE_SOURCE)
        self.apply_theme(QSettings("npworks", "npworks").value("theme", "light"))

    def _set_mode(self, mode):
        QSettings("npworks", "npworks").setValue("markdown/view_mode", mode)
        self._mode = mode
        for k, b in self._mode_buttons.items():
            b.setChecked(k == mode)
        self._editor.setVisible(mode in (MODE_SOURCE, MODE_SPLIT))
        self._preview.setVisible(mode in (MODE_SPLIT, MODE_PREVIEW))
        # 切到分栏/预览时按需构建预览（源码模式不渲染）
        if mode in (MODE_SPLIT, MODE_PREVIEW) and not self._preview_ready:
            self._update_preview(self._editor.text())
            self._preview_ready = True
        # 强制重排 splitter
        self._splitter.setSizes([500, 500] if mode == MODE_SPLIT else [1, 1])

    @property
    def file_path(self):
        return self._path

    def _on_timer(self):
        # 仅在预览可见时刷新，避免源码模式下空跑渲染
        if self._mode in (MODE_SPLIT, MODE_PREVIEW):
            self._update_preview(self._editor.text())

    def _update_preview(self, text):
        base_dir = os.path.dirname(self._path)
        base_qurl = QUrl.fromLocalFile(base_dir + os.sep)
        html = build_html(text, base_qurl.toString())
        if isinstance(self._preview, QTextBrowser):
            self._preview.setHtml(html)
        else:
            self._preview.setHtml(html, base_qurl)

    def get_editor(self):
        return self._editor

    def _style_md_lexer(self):
        """用主题前景色统一样式（去掉难读的蓝色）：标题加粗、强调斜体。"""
        if getattr(self, "_md_lexer", None) is None:
            return
        from PyQt5.QtGui import QColor
        from npworks_ide.ide.theme import get_colors
        c = get_colors()
        fg, bg = c["foreground"], c["background"]
        lexer = self._md_lexer
        for sty in range(128):
            desc = (lexer.description(sty) or "").lower()
            if not desc:
                continue
            font = QFont("Consolas", 11)
            if any(k in desc for k in ("header", "heading", "strong", "title", "h1", "h2")):
                font.setBold(True)
            if any(k in desc for k in ("emphasis", "italic")):
                font.setItalic(True)
            lexer.setColor(QColor(fg), sty)
            lexer.setPaper(QColor(bg), sty)
            lexer.setFont(font, sty)
        lexer.setDefaultColor(QColor(fg))
        lexer.setDefaultPaper(QColor(bg))
        lexer.setFont(QFont("Consolas", 11))

    # --- EditorView 接口 ---
    def editor_title(self):
        return os.path.basename(self._path)

    def is_modified(self):
        return self._editor.isModified()

    def is_readonly(self):
        return False

    def save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                f.write(self._editor.text())
            self._original_text = self._editor.text()
            self._editor.setModified(False)
            return True
        except Exception:
            return False

    def apply_theme(self, theme_name):
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
        self._mode_bar.setStyleSheet(
            f"QWidget#md_mode_bar {{ background: {v['bg_menu']}; border-bottom: 1px solid {v['border']}; }}")
        self.setStyleSheet(
            f"QPushButton#md_mode_btn {{ background: transparent; color: {v['fg_dim']}; "
            f"border: 1px solid transparent; border-radius: 3px; padding: 3px 12px; font-size: 12px; }}"
            f"QPushButton#md_mode_btn:hover {{ background: {v['hover']}; color: {v['fg']}; }}"
            f"QPushButton#md_mode_btn:checked {{ background: {v['accent_bg']}; "
            f"color: {v['fg']}; border-color: {v['border_input']}; }}"
        )
        self._editor.apply_theme()
        self._style_md_lexer()

    def apply_editor_prefs(self):
        self._editor.apply_editor_prefs()


class MarkdownProvider(EditorProvider):
    id = "npworks.markdown"
    extensions = (".md", ".markdown", ".mkd")
    title_prefix = "\U0001F4C4"
    readonly = False

    def create(self, path, parent=None):
        return MarkdownSplitView(path, parent)
