from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QSettings

LIGHT = {
    "background": "#FFFFFF",
    "foreground": "#1E1E1E",
    "current_line": "#F3F3F3",
    "line_number_bg": "#F8F8F8",
    "line_number_fg": "#A0A0A0",
    "line_number_fg_current": "#333333",
    "selection_bg": "#ADD6FF",
    "bracket_match_bg": "#FFD700",
    "keyword": ("#0000FF", True, False),
    "function": ("#795E26", False, False),
    "class_": ("#267F99", True, False),
    "builtin": ("#267F99", False, False),
    "decorator": ("#267F99", False, False),
    "string": ("#A31515", False, False),
    "comment": ("#008000", False, True),
    "number": ("#098658", False, False),
    "operator": ("#000000", False, False),
}

DARK = {
    "background": "#1E1E1E",
    "foreground": "#D4D4D4",
    "current_line": "#2A2D2E",
    "line_number_bg": "#1E1E1E",
    "line_number_fg": "#5A5A5A",
    "line_number_fg_current": "#C6C6C6",
    "selection_bg": "#264F78",
    "bracket_match_bg": "#646400",
    "keyword": ("#569CD6", True, False),
    "function": ("#DCDCAA", False, False),
    "class_": ("#4EC9B0", True, False),
    "builtin": ("#4FC1FF", False, False),
    "decorator": ("#4FC1FF", False, False),
    "string": ("#CE9178", False, False),
    "comment": ("#6A9955", False, True),
    "number": ("#B5CEA8", False, False),
    "operator": ("#D4D4D4", False, False),
}

_LIGHT_VARS = {
    "bg_main": "#F3F3F3",
    "bg_menu": "#F0F0F0",
    "bg_input": "#FFFFFF",
    "fg": "#333333",
    "fg_dim": "#666666",
    "fg_title": "#555555",
    "border": "#D4D4D4",
    "border_input": "#C8C8C8",
    "accent": "#0078D4",
    "accent_bg": "#CCE8FF",
    "hover": "#D6D6D6",
    "hover_input": "#E9E9E9",
    "pressed": "#C4C4C4",
    "scrollbar": "#C1C1C1",
    "scrollbar_hover": "#A0A0A0",
    "output_fg": "#1E1E1E",
    "placeholder_fg": "#999999",
    "disabled": "#AAAAAA",
    "activity_bg": "#2C2C2C",
    "activity_border": "#3C3C3C",
    "activity_fg": "#888888",
    "activity_hover_bg": "#3C3C3C",
    "activity_hover_fg": "#CCCCCC",
    "activity_checked_fg": "#FFFFFF",
    "close_hover": "#C14545",
}

_DARK_VARS = {
    "bg_main": "#1E1E1E",
    "bg_menu": "#2D2D2D",
    "bg_input": "#3C3C3C",
    "fg": "#CCCCCC",
    "fg_dim": "#777777",
    "fg_title": "#AAAAAA",
    "border": "#3C3C3C",
    "border_input": "#555555",
    "accent": "#0078D4",
    "accent_bg": "#094771",
    "hover": "#3C3C3C",
    "hover_input": "#505050",
    "pressed": "#505050",
    "scrollbar": "#555555",
    "scrollbar_hover": "#777777",
    "output_fg": "#CCCCCC",
    "placeholder_fg": "#666666",
    "disabled": "#5A5A5A",
    "activity_bg": "#333333",
    "activity_border": "#3C3C3C",
    "activity_fg": "#666666",
    "activity_hover_bg": "#3C3C3C",
    "activity_hover_fg": "#CCCCCC",
    "activity_checked_fg": "#FFFFFF",
    "close_hover": "#C14545",
}

_QSS_TEMPLATE = """
QMainWindow {{
    background: {bg_main};
}}

QMenuBar {{
    background: {bg_menu};
    color: {fg};
    border-bottom: 1px solid {border};
    padding: 1px;
    font-size: 13px;
}}
QMenuBar::item {{
    padding: 4px 10px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {accent_bg};
}}

QMenu {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 4px 0px;
    font-size: 13px;
}}
QMenu::item {{
    padding: 6px 28px 6px 20px;
}}
QMenu::item:selected {{
    background: {accent};
    color: #FFFFFF;
}}
QMenu::separator {{
    height: 1px;
    background: {border};
    margin: 4px 8px;
}}

QToolBar {{
    background: {bg_menu};
    border: none;
    border-bottom: 1px solid {border};
    spacing: 2px;
    padding: 3px 6px;
}}
QToolBar QToolButton {{
    color: {fg};
    padding: 5px 10px;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    background: transparent;
}}
QToolBar QToolButton:hover {{
    background: {hover};
}}
QToolBar QToolButton:pressed {{
    background: {pressed};
}}
QToolBar QToolButton:disabled {{
    color: {disabled};
}}
QToolBar::separator {{
    width: 1px;
    height: 20px;
    background: {border};
    margin: 2px 4px;
}}

QTabWidget::pane {{
    border: none;
    background: {bg_main};
}}
QTabBar {{
    background: {bg_menu};
    border-bottom: 1px solid {border};
    font-size: 13px;
}}
QTabBar::tab {{
    background: transparent;
    color: {fg_dim};
    padding: 7px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 0px;
    min-width: 80px;
}}
QTabBar::tab:hover {{
    color: {fg};
    background: {hover};
}}
QTabBar::tab:selected {{
    color: {activity_checked_fg};
    border-bottom: 2px solid {accent};
    background: {bg_main};
}}
QTabBar::close-button {{
    subcontrol-position: right;
    image: none;
    width: 18px; height: 18px;
    border-radius: 3px;
    color: {fg_dim};
    font-size: 14px;
    font-weight: bold;
}}
QTabBar::close-button:hover {{
    background: {close_hover};
    color: #FFFFFF;
}}

QSplitter::handle {{
    background: {border};
}}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical   {{ height: 1px; }}
QSplitter::handle:hover {{ background: {accent}; }}

QStatusBar {{
    background: #007ACC;
    color: #FFFFFF;
    border: none;
    font-size: 12px;
    padding: 0px 4px;
}}
QStatusBar QLabel {{
    color: #FFFFFF;
    padding: 2px 8px;
    border-radius: 2px;
}}

QTreeWidget {{
    background: {bg_main};
    color: {fg};
    border: none;
    border-right: 1px solid {border};
    outline: none;
    font-size: 13px;
}}
QTreeWidget::item {{
    padding: 5px 4px;
    border-radius: 3px;
    margin: 1px 4px;
}}
QTreeWidget::item:hover {{
    background: {hover};
}}
QTreeWidget::item:selected {{
    background: {accent};
    color: #FFFFFF;
}}
QTreeWidget::branch {{
    background: {bg_main};
}}
QHeaderView::section {{
    background: {bg_menu};
    color: {fg_dim};
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {border};
    font-size: 12px;
    font-weight: bold;
}}

QLineEdit {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border_input};
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 13px;
    selection-background-color: {selection_bg};
}}
QLineEdit:focus {{
    border: 1px solid {accent};
}}

QPushButton {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border_input};
    padding: 4px 14px;
    border-radius: 4px;
    font-size: 13px;
}}
QPushButton:hover {{
    background: {hover_input};
    border: 1px solid {border_input};
}}
QPushButton:pressed {{
    background: {hover};
}}
QCheckBox {{
    color: {fg};
    spacing: 6px;
    font-size: 12px;
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border-radius: 3px;
    border: 1px solid {border_input};
    background: {bg_input};
}}
QCheckBox::indicator:checked {{
    background: {accent};
    border: 1px solid {accent};
}}

QTextEdit#output_text {{
    background: {bg_main};
    color: {output_fg};
    border: none;
    padding: 4px;
    font-size: 13px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {scrollbar};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {scrollbar_hover}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {scrollbar};
    border-radius: 5px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: {scrollbar_hover}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

QToolTip {{
    background: {bg_menu};
    color: {fg};
    border: 1px solid {border_input};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}

QCompleter QListView {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border_input};
    border-radius: 6px;
    padding: 4px;
    outline: none;
    font-size: 13px;
}}
QCompleter QListView::item {{
    padding: 4px 12px;
    border-radius: 3px;
}}
QCompleter QListView::item:selected {{
    background: {accent};
    color: #FFFFFF;
}}

QMessageBox {{
    background: {bg_input};
}}

#bottom_header {{
    background: {bg_menu};
    border-bottom: 1px solid {border};
    border-top: 1px solid {border};
}}
QPushButton#bottom_tab_btn {{
    background: transparent;
    color: {fg_dim};
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton#bottom_tab_btn:hover {{
    color: {fg};
    background: {hover};
}}
QPushButton#bottom_tab_btn:checked {{
    color: {activity_checked_fg};
    border-bottom: 2px solid {accent};
}}
QPushButton#bottom_ctrl_btn {{
    background: transparent;
    color: {fg_dim};
    border: none;
    border-radius: 3px;
    font-size: 12px;
}}
QPushButton#bottom_ctrl_btn:hover {{
    background: {hover};
    color: {fg};
}}

#terminal_display, #jupyter_terminal {{
    background: #1E1E1E;
    color: #CCCCCC;
    border: none;
    padding: 6px;
    font-family: Consolas, monospace;
    font-size: 13px;
}}
#terminal_input_row {{
    background: {bg_menu};
    border-top: 1px solid {border};
}}
#terminal_input_row QComboBox {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border};
    border-radius: 3px;
    padding: 3px 6px;
    font-size: 12px;
}}
#terminal_input_row QComboBox::drop-down {{
    border: none;
    width: 16px;
}}
#terminal_input_row QComboBox QAbstractItemView {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border_input};
    selection-background-color: {accent_bg};
}}
#terminal_input_row QLineEdit {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border};
    border-radius: 3px;
    padding: 4px 8px;
    font-family: Consolas, monospace;
    font-size: 13px;
}}
#terminal_input_row QLineEdit:focus {{
    border: 1px solid {accent};
}}
#terminal_input_row QPushButton {{
    background: {bg_input};
    color: {fg};
    border: 1px solid {border_input};
    border-radius: 3px;
    padding: 3px 6px;
    font-size: 12px;
}}
#terminal_input_row QPushButton:hover {{
    background: {hover_input};
}}
#terminal_prompt {{
    color: #6A9955;
    font-family: Consolas, monospace;
    font-size: 13px;
}}

QStackedWidget {{
    background: #1E1E1E;
}}

#file_tree_toolbar {{
    background: {bg_menu};
    border-top: 1px solid {border};
}}
#file_tree_btn {{
    background: transparent;
    color: {fg_title};
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 3px 8px;
    font-size: 11px;
}}
#file_tree_btn:hover {{
    background: {hover};
    border-color: {border_input};
}}

#activity_bar_container {{
    background: {activity_bg};
}}
#activity_bar {{
    background: {activity_bg};
    border-right: 1px solid {activity_border};
}}
#activity_btn {{
    background: transparent;
    color: {activity_fg};
    border: none;
    border-left: 2px solid transparent;
    font-size: 16px;
    border-radius: 0px;
}}
#activity_btn:hover {{
    color: {activity_hover_fg};
    background: {activity_hover_bg};
}}
#activity_btn:checked {{
    color: {activity_checked_fg};
    border-left: 2px solid {accent};
    background: {activity_hover_bg};
}}

#sidebar_panel {{
    background: {bg_main};
}}
#sidebar_title {{
    background: {bg_menu};
}}
#sidebar_separator {{
    background: {border};
    border: none;
}}

#dock_title_label {{
    color: {fg_title};
}}

#outline_placeholder {{
    color: {placeholder_fg};
    font-size: 13px;
    padding: 20px;
}}
"""

_SELECTION_BG = {
    "light": "#ADD6FF",
    "dark": "#264F78",
}


def get_colors(theme_name=None):
    if theme_name is None:
        s = QSettings("npworks", "npworks")
        theme_name = s.value("theme", "light")
    return DARK if theme_name == "dark" else LIGHT


def _build_qss(theme_name):
    v = _DARK_VARS if theme_name == "dark" else _LIGHT_VARS
    v = dict(v)
    v["selection_bg"] = _SELECTION_BG.get(theme_name, "#ADD6FF")
    return _QSS_TEMPLATE.format_map(v)


def apply_theme(app, theme_name):
    s = QSettings("npworks", "npworks")
    s.setValue("theme", theme_name)
    if theme_name == "dark":
        p = QPalette()
        p.setColor(QPalette.Window, QColor(30, 30, 30))
        p.setColor(QPalette.WindowText, QColor(204, 204, 204))
        p.setColor(QPalette.Base, QColor(30, 30, 30))
        p.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        p.setColor(QPalette.ToolTipBase, QColor(45, 45, 45))
        p.setColor(QPalette.ToolTipText, QColor(204, 204, 204))
        p.setColor(QPalette.Text, QColor(204, 204, 204))
        p.setColor(QPalette.Button, QColor(45, 45, 45))
        p.setColor(QPalette.ButtonText, QColor(204, 204, 204))
        p.setColor(QPalette.BrightText, QColor(255, 50, 50))
        p.setColor(QPalette.Link, QColor(0, 120, 212))
        p.setColor(QPalette.Highlight, QColor(0, 120, 212))
        p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        p.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        app.setPalette(p)
        app.setStyleSheet(_build_qss("dark"))
    else:
        p = QPalette()
        p.setColor(QPalette.Window, QColor(243, 243, 243))
        p.setColor(QPalette.WindowText, QColor(51, 51, 51))
        p.setColor(QPalette.Base, QColor(255, 255, 255))
        p.setColor(QPalette.AlternateBase, QColor(243, 243, 243))
        p.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        p.setColor(QPalette.ToolTipText, QColor(51, 51, 51))
        p.setColor(QPalette.Text, QColor(51, 51, 51))
        p.setColor(QPalette.Button, QColor(240, 240, 240))
        p.setColor(QPalette.ButtonText, QColor(51, 51, 51))
        p.setColor(QPalette.BrightText, QColor(255, 0, 0))
        p.setColor(QPalette.Link, QColor(0, 120, 212))
        p.setColor(QPalette.Highlight, QColor(0, 120, 212))
        p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        app.setPalette(p)
        app.setStyleSheet(_build_qss("light"))
