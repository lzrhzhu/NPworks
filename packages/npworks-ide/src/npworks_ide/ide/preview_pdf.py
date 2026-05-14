import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QSizePolicy,
)

_PDF_EXTS = {".pdf"}


def is_pdf_file(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in _PDF_EXTS


class PdfPreview(QWidget):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._path = file_path
        self._doc = None
        self._current_page = 0
        self._total_pages = 0
        self._zoom = 1.0
        self._page_labels = []
        self._page_pixmaps = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QWidget()
        toolbar.setFixedHeight(36)
        toolbar.setStyleSheet(
            "background: #2D2D2D; border-bottom: 1px solid #3C3C3C;"
        )
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 2, 8, 2)
        tb_layout.setSpacing(6)

        self._btn_prev = QPushButton("< 上一页")
        self._btn_next = QPushButton("下一页 >")
        self._btn_zoom_out = QPushButton("-")
        self._btn_zoom_in = QPushButton("+")
        self._btn_fit_width = QPushButton("适合宽度")

        self._page_info = QLabel("0 / 0")
        self._page_info.setStyleSheet("color: #CCCCCC;")
        self._zoom_label = QLabel("100%")
        self._zoom_label.setStyleSheet("color: #CCCCCC;")

        btn_style = (
            "QPushButton { background: #3C3C3C; color: #CCCCCC; border: none; "
            "padding: 4px 10px; border-radius: 3px; }"
            "QPushButton:hover { background: #505050; }"
            "QPushButton:pressed { background: #0078D4; }"
            "QPushButton:disabled { background: #2D2D2D; color: #666666; }"
        )
        for btn in (self._btn_prev, self._btn_next, self._btn_zoom_out,
                     self._btn_zoom_in, self._btn_fit_width):
            btn.setStyleSheet(btn_style)
            btn.setFont(QFont("Segoe UI", 9))

        self._btn_prev.clicked.connect(self._prev_page)
        self._btn_next.clicked.connect(self._next_page)
        self._btn_zoom_out.clicked.connect(self._zoom_out)
        self._btn_zoom_in.clicked.connect(self._zoom_in)
        self._btn_fit_width.clicked.connect(self._fit_width)

        tb_layout.addWidget(self._btn_prev)
        tb_layout.addWidget(self._page_info)
        tb_layout.addWidget(self._btn_next)
        tb_layout.addStretch()
        tb_layout.addWidget(self._btn_zoom_out)
        tb_layout.addWidget(self._zoom_label)
        tb_layout.addWidget(self._btn_zoom_in)
        tb_layout.addWidget(self._btn_fit_width)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { background: #1E1E1E; border: none; }")
        self._scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self._container = QWidget()
        self._container.setStyleSheet("background: #1E1E1E;")
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._container_layout.setSpacing(8)
        self._container_layout.setContentsMargins(0, 8, 0, 8)

        self._scroll.setWidget(self._container)

        layout.addWidget(toolbar)
        layout.addWidget(self._scroll)

        self._load_pdf(file_path)

    @property
    def file_path(self):
        return self._path

    def _load_pdf(self, file_path: str):
        try:
            import fitz
            self._doc = fitz.open(file_path)
            self._total_pages = len(self._doc)
            self._current_page = 0
            self._render_pages()
        except ImportError:
            self._show_fallback("PyMuPDF 未安装，无法渲染 PDF。请运行: pip install PyMuPDF")
        except Exception as e:
            self._show_fallback(f"无法打开 PDF: {e}")

    def _show_fallback(self, text: str):
        label = QLabel(f"  {text}")
        label.setStyleSheet("color: #CC6666; font-size: 14px; padding: 20px;")
        self._container_layout.addWidget(label)
        self._total_pages = 0
        self._current_page = 0
        self._update_nav()

    def _render_pages(self):
        for lbl in self._page_labels:
            self._container_layout.removeWidget(lbl)
            lbl.deleteLater()
        self._page_labels.clear()
        self._page_pixmaps.clear()

        import fitz
        for page_idx in range(self._total_pages):
            page = self._doc[page_idx]
            mat = fitz.Matrix(self._zoom * 2, self._zoom * 2)
            pix = page.get_pixmap(matrix=mat)
            img = QImage(pix.samples, pix.width, pix.height,
                         pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self._page_pixmaps.append(pixmap)

            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                "background: white; margin: 4px 8px; "
                "border: 1px solid #3C3C3C; border-radius: 2px;"
            )
            self._page_labels.append(label)
            self._container_layout.addWidget(label)

        self._update_nav()

    def _update_nav(self):
        self._page_info.setText(f"{self._current_page + 1} / {self._total_pages}")
        self._zoom_label.setText(f"{int(self._zoom * 100)}%")
        self._btn_prev.setEnabled(self._current_page > 0)
        self._btn_next.setEnabled(self._current_page < self._total_pages - 1)

    def _prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._scroll_to_page(self._current_page)
            self._update_nav()

    def _next_page(self):
        if self._current_page < self._total_pages - 1:
            self._current_page += 1
            self._scroll_to_page(self._current_page)
            self._update_nav()

    def _scroll_to_page(self, idx):
        if 0 <= idx < len(self._page_labels):
            self._scroll.ensureWidgetVisible(self._page_labels[idx], 0, 0)

    def _zoom_in(self):
        if self._zoom < 3.0:
            self._zoom = min(self._zoom + 0.25, 3.0)
            self._rerender()

    def _zoom_out(self):
        if self._zoom > 0.25:
            self._zoom = max(self._zoom - 0.25, 0.25)
            self._rerender()

    def _fit_width(self):
        viewport_width = self._scroll.viewport().width() - 40
        if viewport_width <= 0 or not self._doc or self._total_pages == 0:
            return
        import fitz
        page = self._doc[0]
        page_width = page.rect.width
        if page_width > 0:
            self._zoom = viewport_width / (page_width * 2)
            self._zoom = max(0.25, min(self._zoom, 3.0))
            self._rerender()

    def _rerender(self):
        if self._doc and self._total_pages > 0:
            self._render_pages()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._zoom_in()
            elif delta < 0:
                self._zoom_out()
            event.accept()
            return
        super().wheelEvent(event)

    def cleanup(self):
        if self._doc:
            self._doc.close()
            self._doc = None
