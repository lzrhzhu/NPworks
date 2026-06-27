"""npworks 插件：PDF 查看器。"""
from .pdf_view import PdfPreview, PdfProvider

__version__ = "0.0.1"


def register(api):
    api.register_editor(PdfProvider())
