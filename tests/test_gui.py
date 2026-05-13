import sys
import traceback

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

try:
    print("1. Creating QApplication", flush=True)
    app = QApplication(sys.argv)
    print("2. QApplication created", flush=True)

    from npworks_ide.ide.editor import CodeEditor
    print("3. CodeEditor imported", flush=True)

    w = CodeEditor()
    print("4. CodeEditor created", flush=True)

    w.set_code("def hello():\n    pass\n")
    print("5. Code set", flush=True)

    w.show()
    print("6. Widget shown", flush=True)

    QTimer.singleShot(1000, app.quit)
    print("7. Timer set", flush=True)

    app.exec_()
    print("8. App exited normally", flush=True)
except Exception:
    traceback.print_exc()
    print("ERROR", flush=True)
