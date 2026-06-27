"""通过 DWM API 让 Windows 原生标题栏/边框跟随应用主题（消除顶部白边）。

保留原生窗口的全部行为（系统缩放、Aero Snap、最小化/最大化/关闭），
仅把标题栏与边框颜色改为深色或浅色以匹配主题。
非 Windows 平台为空操作。
"""
import sys


def _hex_to_colorref(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b << 16) | (g << 8) | r   # COLORREF = 0x00BBGGRR


def apply_titlebar_theme(window, theme, caption_color=None, border_color=None):
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = int(window.winId())
        dwm = ctypes.windll.dwmapi

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        dark = theme == "dark"
        value = ctypes.c_int(1 if dark else 0)
        if dwm.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value), ctypes.sizeof(value),
        ) != 0:
            dwm.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value))

        if caption_color is not None:
            cap = ctypes.c_int(_hex_to_colorref(caption_color))
            dwm.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(cap), ctypes.sizeof(cap))
        if border_color is not None:
            bord = ctypes.c_int(_hex_to_colorref(border_color))
            dwm.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(bord), ctypes.sizeof(bord))
    except Exception:
        pass
