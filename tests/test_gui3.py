import sys, traceback
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

import npworks_ide.ide.editor as mod
from PyQt5.QtGui import QFont, QColor
from PyQt5.Qsci import QsciScintillaBase

try:
    e = mod.CodeEditor.__new__(mod.CodeEditor)
    print("a. new", flush=True)

    super(mod.CodeEditor, e).__init__(None)
    print("b. super init", flush=True)

    e._original_code = ""
    e._file_path = None
    e._chapter_id = None
    e._section_filename = None
    e._tab_title = "未命名"
    e._on_file_dropped = None
    print("c. attrs", flush=True)

    e._setup_editor()
    print("d. setup_editor", flush=True)

    e._setup_lexer()
    print("e. setup_lexer", flush=True)

    e._setup_api()
    print("f. setup_api", flush=True)

    e._setup_folding()
    print("g. setup_folding", flush=True)

    e._apply_theme()
    print("h. apply_theme", flush=True)

    e.setAcceptDrops(True)
    e.SCN_CHARADDED.connect(e._on_char_added)
    print("i. signals", flush=True)

    print("ALL OK", flush=True)
except Exception:
    traceback.print_exc()
