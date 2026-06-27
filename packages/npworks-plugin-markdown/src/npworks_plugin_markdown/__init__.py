"""npworks 插件：Markdown 分栏编辑与实时预览。"""
from .md_view import MarkdownSplitView, MarkdownProvider

__version__ = "0.0.1"


def register(api):
    api.register_editor(MarkdownProvider())
