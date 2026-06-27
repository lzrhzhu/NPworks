"""PDF 查看视图与 provider。"""
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton,
)

from npworks_ide.ide.editor_registry import EditorView, EditorProvider


class PdfPreview(QWidget, EditorView):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self._path = file_path
        self._doc = None
        self._current_page = 0
        self._total_pages = 0
        self._zoom = 1.0
        self._page_labels = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QWidget()
        toolbar.setFixedHeight(36)
        toolbar.setStyleSheet("background:#2D2D2D; border-bottom:1px solid #3C3C3C;")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(8, 2, 8, 2)
        tb.setSpacing(6)

        self._btn_prev = QPushButton("< 上一页")
        self._btn_next = QPushButton("下一页 >")
        self._btn_zoom_out = QPushButton("-")
        self._btn_zoom_in = QPushButton("+")
        self._btn_fit = QPushButton("适合宽度")
        self._page_info = QLabel("0 / 0")
        self._page_info.setStyleSheet("color:#CCCCCC;")
        self._zoom_label = QLabel("100%")
        self._zoom_label.setStyleSheet("color:#CCCCCC;")

        btn_style = (
            "QPushButton{background:#3C3C3C;color:#CCCCCC;border:none;padding:4px 10px;border-radius:3px;}"
            "QPushButton:hover{background:#505050;}"
            "QPushButton:pressed{background:#0078D4;}"
            "QPushButton:disabled{background:#2D2D2D;color:#666;}"
        )
        for b in (self._btn_prev, self._btn_next, self._btn_zoom_out, self._btn_zoom_in, self._btn_fit):
            b.setStyleSheet(btn_style)
            b.setFont(QFont("Segoe UI", 9))

        self._btn_prev.clicked.connect(self._prev_page)
        self._btn_next.clicked.connect(self._next_page)
        self._btn_zoom_out.clicked.connect(lambda: self._zoom_by(-0.25))
        self._btn_zoom_in.clicked.connect(lambda: self._zoom_by(0.25))
        self._btn_fit.clicked.connect(self._fit_width)

        tb.addWidget(self._btn_prev)
        tb.addWidget(self._page_info)
        tb.addWidget(self._btn_next)
        tb.addStretch()
        tb.addWidget(self._btn_zoom_out)
        tb.addWidget(self._zoom_label)
        tb.addWidget(self._btn_zoom_in)
        tb.addWidget(self._btn_fit)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea{background:#1E1E1E;border:none;}")
        self._scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self._container = QWidget()
        self._container.setStyleSheet("background:#1E1E1E;")
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

    def _load_pdf(self, file_path):
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

    def _show_fallback(self, text):
        lbl = QLabel(f"  {text}")
        lbl.setStyleSheet("color:#CC6666;font-size:14px;padding:20px;")
        self._container_layout.addWidget(lbl)
        self._total_pages = 0
        self._current_page = 0
        self._update_nav()

    def _render_pages(self):
        import fitz
        for lbl in self._page_labels:
            self._container_layout.removeWidget(lbl)
            lbl.deleteLater()
        self._page_labels.clear()
        for idx in range(self._total_pages):
            page = self._doc[idx]
            pix = page.get_pixmap(matrix=fitz.Matrix(self._zoom * 2, self._zoom * 2))
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            lbl = QLabel()
            lbl.setPixmap(QPixmap.fromImage(img))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background:white;margin:4px 8px;border:1px solid #3C3C3C;border-radius:2px;")
            self._page_labels.append(lbl)
            self._container_layout.addWidget(lbl)
        self._update_nav()

    def _update_nav(self):
        self._page_info.setText(f"{self._current_page + 1} / {self._total_pages}")
        self._zoom_label.setText(f"{int(self._zoom * 100)}%")
        self._btn_prev.setEnabled(self._current_page > 0)
        self._btn_next.setEnabled(self._current_page < self._total_pages - 1)

    def _prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._scroll_to(self._current_page)
            self._update_nav()

    def _next_page(self):
        if self._current_page < self._total_pages - 1:
            self._current_page += 1
            self._scroll_to(self._current_page)
            self._update_nav()

    def _scroll_to(self, idx):
        if 0 <= idx < len(self._page_labels):
            self._scroll.ensureWidgetVisible(self._page_labels[idx], 0, 0)

    def _zoom_by(self, delta):
        self._zoom = max(0.25, min(self._zoom + delta, 3.0))
        if self._doc and self._total_pages > 0:
            self._render_pages()

    def _fit_width(self):
        vw = self._scroll.viewport().width() - 40
        if vw <= 0 or not self._doc or self._total_pages == 0:
            return
        pw = self._doc[0].rect.width
        if pw > 0:
            self._zoom = max(0.25, min(vw / (pw * 2), 3.0))
            self._render_pages()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            d = event.angleDelta().y()
            if d > 0:
                self._zoom_by(0.25)
            elif d < 0:
                self._zoom_by(-0.25)
            event.accept()
            return
        super().wheelEvent(event)

    def cleanup(self):
        if self._doc:
            self._doc.close()
            self._doc = None


class PdfProvider(EditorProvider):
    id = "npworks.pdf"
    extensions = (".pdf",)
    title_prefix = "\U0001F4D1"
    readonly = True

    def create(self, path, parent=None):
        return PdfPreview(path, parent)
