"""内置 EditorProvider 集合与注册。

仅保留代码编辑器(兜底)与图片查看器；PDF、Markdown、CSV 等作为可安装插件
（见 packages/npworks-plugin-*，通过入口点 npworks.plugins 注册）。
"""
import os

from npworks_ide.ide.plugin.editor_registry import registry, EditorProvider


class CodeProvider(EditorProvider):
    id = "npworks.code"
    extensions = ()            # 兜底：can_open 恒为真
    priority = EditorProvider.priority - 1   # 最低，作为默认文本编辑器
    title_prefix = "Py"
    readonly = False

    def can_open(self, path):
        return True            # VS Code 风格：未知类型一律按文本打开

    def create(self, path, parent=None):
        from npworks_ide.ide.widgets.editor import CodeEditor
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


class ImageProvider(EditorProvider):
    id = "npworks.image"
    extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg", ".webp")
    title_prefix = "\U0001F5BC"
    readonly = True

    def create(self, path, parent=None):
        from npworks_ide.ide.widgets.preview_image import ImagePreview
        return ImagePreview(path, parent)


_builtin_providers = [
    ImageProvider(),
    CodeProvider(),
]


def register_builtin_editors():
    for provider in _builtin_providers:
        registry.register(provider)
