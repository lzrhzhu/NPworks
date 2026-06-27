"""非文件型标签页（文档/设置/欢迎页等）的可复用基类。

VS Code 风格：插件可以把任意 UI 作为"文档页面"打开在编辑区标签页里，
而不是弹模态对话框。继承 DocumentPanel 并通过 MainWindow.open_panel 打开。
"""
from PyQt5.QtWidgets import QWidget

from npworks_ide.ide.editor_registry import EditorView


class DocumentPanel(QWidget, EditorView):
    def __init__(self, title, panel_id=None, parent=None):
        super().__init__(parent)
        self._title = title
        self._panel_id = panel_id

    def editor_title(self):
        return self._title

    def is_readonly(self):
        return True

    @property
    def panel_id(self):
        return self._panel_id
