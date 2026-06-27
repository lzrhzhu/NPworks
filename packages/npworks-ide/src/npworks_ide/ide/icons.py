import os

from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QApplication

try:
    from PyQt5.QtSvg import QSvgRenderer
    _HAS_SVG = True
except ImportError:
    _HAS_SVG = False

# 单色线性图标 (24x24 viewBox)。所有颜色用 {color} 占位，按主题着色。
# 图标来源风格：Material Design / VS Code Codex 线性图标。

_ICONS = {
    "explorer": (
        '<path fill="{color}" d="M10 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>'
    ),
    "outline": (
        '<path fill="{color}" d="M5 5h2v2H5V5zm0 4h2v2H5V9zm0 4h2v2H5v-2zm0 4h2v2H5v-2zM9 5h12v2H9V5zm0 4h12v2H9V9zm0 4h12v2H9v-2zm0 4h12v2H9v-2z"/>'
    ),
    "search": (
        '<path fill="{color}" d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14z"/>'
    ),
    "settings": (
        '<path fill="{color}" d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94 0 .31.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>'
    ),
    "run": (
        '<path fill="{color}" d="M8 5v14l11-7z"/>'
    ),
    "stop": (
        '<path fill="{color}" d="M6 6h12v12H6z"/>'
    ),
    "new": (
        '<path fill="{color}" d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8V4h5v5h5v9zm-4-1h-2v-3H7v-2h3V8h2v3h3v2h-3z"/>'
    ),
    "open": (
        '<path fill="{color}" d="M20 6h-8l-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>'
    ),
    "save": (
        '<path fill="{color}" d="M17 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7l-4-4zm-5 16a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm3-10H5V5h10v4z"/>'
    ),
    "reset": (
        '<path fill="{color}" d="M17.65 6.35A7.95 7.95 0 0 0 12 4a8 8 0 1 0 7.74 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>'
    ),
    "book": (
        '<path fill="{color}" d="M18 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM6 4h5v8L8.5 10.5 6 12V4z"/>'
    ),
    "winmin": (
        '<rect x="5" y="14" width="14" height="1.8" fill="{color}"/>'
    ),
    "winmax": (
        '<rect x="6" y="6" width="12" height="12" fill="none" stroke="{color}" stroke-width="1.8"/>'
    ),
    "winrestore": (
        '<rect x="5" y="8" width="10" height="10" fill="none" stroke="{color}" stroke-width="1.8"/>'
        '<path d="M8.5 8 V5 H18 V14.5 H15" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/>'
    ),
    "winclose": (
        '<path d="M6 6 L18 18 M18 6 L6 18" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
    ),
}

# 应用 Logo：原子轨道（计算物理主题）
_LOGO = (
    '<g fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round">'
    '<ellipse cx="12" cy="12" rx="10" ry="4"/>'
    '<ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/>'
    '<ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/>'
    '</g>'
    '<circle cx="12" cy="12" r="2.4" fill="{color}"/>'
)

_ICON_KEYS = ("explorer", "outline", "search", "settings", "run", "stop",
              "new", "open", "save", "reset", "book",
              "winmin", "winmax", "winrestore", "winclose")


def _device_pixel_ratio():
    app = QApplication.instance()
    if app is None:
        return 1.0
    screen = app.primaryScreen()
    return screen.devicePixelRatio() if screen else 1.0


def _render_svg(inner_template, color, size):
    inner = inner_template.replace("{color}", color)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
        f' width="{size}" height="{size}">{inner}</svg>'
    )
    ratio = _device_pixel_ratio()
    phys = max(1, int(round(size * ratio)))
    pm = QPixmap(phys, phys)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing, True)
    if _HAS_SVG:
        renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
        renderer.render(painter)
    else:
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.gray)
        painter.drawEllipse(2, 2, size - 4, size - 4)
    painter.end()
    if ratio != 1.0:
        pm.setDevicePixelRatio(ratio)
    return pm


def icon(name, color, size=22):
    """按名称和颜色生成单色 QIcon。"""
    template = _ICONS.get(name)
    if template is None:
        return QIcon()
    return QIcon(_render_svg(template, color, size))


def logo_icon(color, size=22):
    return QIcon(_render_svg(_LOGO, color, size))


def logo_pixmap(color, size=256):
    return _render_svg(_LOGO, color, size)
