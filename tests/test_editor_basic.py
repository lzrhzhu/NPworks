import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'npworks-ide', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'npworks-content', 'src'))

print("Step 1: imports")
from npworks_ide.ide.editor import CodeEditor
from PyQt5.QtWidgets import QApplication

print("Step 2: QApplication")
app = QApplication(sys.argv)

print("Step 3: create CodeEditor")
e = CodeEditor()

print("Step 4: set_code")
e.set_code("def hello():\n    pass\n")

print("Step 5: get_code")
code = e.get_code()
print(f"  code: {repr(code[:30])}")

print("Step 6: toggle_comment")
e.toggle_comment()
print(f"  after comment: {repr(e.get_code()[:40])}")

print("Step 7: toggle_comment again")
e.toggle_comment()
print(f"  after uncomment: {repr(e.get_code()[:30])}")

print("Step 8: cursor position")
line, col = e.getCursorPosition()
print(f"  cursor: line={line}, col={col}")

print("Step 9: folding check")
print(f"  folding enabled: {e.folding()}")

print("Step 10: indentation guides")
print(f"  indent guides: {e.indentationGuides()}")

print("\nALL TESTS PASSED")
