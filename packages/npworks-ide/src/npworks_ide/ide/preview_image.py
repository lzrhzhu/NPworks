from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea

from npworks_ide.ide.editor_registry import EditorView


_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg", ".webp"}


def is_image_file(path: str) -> bool:
    from os.path import splitext
    return splitext(path)[1].lower() in _IMAGE_EXTS


class ImagePreview(QWidget, EditorView):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._path = file_path

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("background: #1E1E1E;")

        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self._label.setPixmap(pixmap)
        else:
            img = QImage(file_path)
            if not img.isNull():
                self._label.setPixmap(QPixmap.fromImage(img))
            else:
                self._label.setText(f"  无法加载图片: {file_path}")

        scroll.setWidget(self._label)
        layout.addWidget(scroll)

    @property
    def file_path(self):
        return self._path

    def apply_theme(self, theme_name):
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
        self._label.setStyleSheet(f"background: {v['bg_main']};")
