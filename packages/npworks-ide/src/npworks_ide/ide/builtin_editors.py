"""内置 EditorProvider 集合与注册。"""
import os

from npworks_ide.ide.editor_registry import registry, EditorProvider


class CodeProvider(EditorProvider):
    id = "npworks.code"
    extensions = ()            # 兜底：can_open 恒为真
    priority = EditorProvider.priority - 1   # 最低，作为默认文本编辑器
    title_prefix = "Py"
    readonly = False

    def can_open(self, path):
        return True            # VS Code 风格：未知类型一律按文本打开

    def create(self, path, parent=None):
        from npworks_ide.ide.editor import CodeEditor
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception:
            code = ""
        editor = CodeEditor(parent)
        editor.file_path = path
        editor.tab_title = os.path.basename(path)
        editor.set_code(code, code)
        return editor


class MarkdownProvider(EditorProvider):
    id = "npworks.markdown"
    extensions = (".md", ".markdown", ".mkd")
    title_prefix = "\U0001F4C4"
    readonly = False

    def create(self, path, parent=None):
        from npworks_ide.ide.preview_markdown import MarkdownSplitView
        return MarkdownSplitView(path, parent)


class ImageProvider(EditorProvider):
    id = "npworks.image"
    extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg", ".webp")
    title_prefix = "\U0001F5BC"
    readonly = True

    def create(self, path, parent=None):
        from npworks_ide.ide.preview_image import ImagePreview
        return ImagePreview(path, parent)


class PdfProvider(EditorProvider):
    id = "npworks.pdf"
    extensions = (".pdf",)
    title_prefix = "\U0001F4D1"
    readonly = True

    def create(self, path, parent=None):
        from npworks_ide.ide.preview_pdf import PdfPreview
        return PdfPreview(path, parent)


_builtin_providers = [
    PdfProvider(),
    ImageProvider(),
    MarkdownProvider(),
    CodeProvider(),
]


def register_builtin_editors():
    for provider in _builtin_providers:
        registry.register(provider)
