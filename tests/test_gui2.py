import sys
import traceback

from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from PyQt5.QtGui import QFont, QColor

try:
    print("a. Creating QsciScintilla", flush=True)
    sci = QsciScintilla()
    print("b. Created", flush=True)

    sci.setFont(QFont("Consolas", 11))
    sci.setTabWidth(4)
    sci.setIndentationsUseTabs(False)
    sci.setMarginLineNumbers(0, True)
    sci.setMarginWidth(0, "0000")
    print("c. Basic settings done", flush=True)

    lexer = QsciLexerPython(sci)
    sci.setLexer(lexer)
    print("d. Lexer set", flush=True)

    apis = QsciAPIs(lexer)
    apis.add("print")
    apis.prepare()
    print("e. APIs prepared", flush=True)

    sci.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)
    print("f. Folding set", flush=True)

    sci.setIndentationGuides(True)
    print("g. Indent guides set", flush=True)

    sci.setAutoIndent(True)
    sci.setBackspaceUnindents(True)
    sci.setBraceMatching(QsciScintilla.SloppyBraceMatch)
    sci.setCaretLineVisible(True)
    sci.setCaretLineBackgroundColor(QColor("#F3F3F3"))
    sci.setText("def hello():\n    pass\n")
    print("h. Text set", flush=True)

    print("ALL OK - text:", repr(sci.text()[:20]), flush=True)
except Exception:
    traceback.print_exc()
