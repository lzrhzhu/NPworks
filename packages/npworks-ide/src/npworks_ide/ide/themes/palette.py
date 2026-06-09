from PyQt5.QtGui import QPalette, QColor


def build_palette(theme_name):
    p = QPalette()
    if theme_name == "dark":
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
    else:
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
    return p
