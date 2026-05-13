import sys
import traceback

try:
    from PyQt5.QtCore import QTimer
    from npworks_ide.app import main

    import npworks_ide.ide.main_window as mw

    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    from PyQt5.QtGui import QFont
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    from npworks_ide.ide.theme import apply_theme
    apply_theme(app, "light")

    window = mw.MainWindow()
    print("MainWindow created", flush=True)
    window.show()
    print("MainWindow shown", flush=True)

    def quit_app():
        print("Quitting...", flush=True)
        app.quit()

    QTimer.singleShot(2000, quit_app)
    app.exec_()
    print("APP EXITED NORMALLY", flush=True)
except Exception:
    traceback.print_exc()
