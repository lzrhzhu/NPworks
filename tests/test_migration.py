import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'npworks-ide', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'npworks-content', 'src'))

print("Test 1: editor module import")
from npworks_ide.ide.editor import CodeEditor, PythonLexer
print("  OK")

print("Test 2: theme module")
from npworks_ide.ide.theme import get_colors, LIGHT, DARK
c = LIGHT
print(f"  LIGHT keyword: {c['keyword']}")
print(f"  DARK keyword: {DARK['keyword']}")

print("Test 3: verify theme tuple format for lexer")
for key in ['keyword', 'function', 'class_', 'builtin', 'decorator', 'string', 'comment', 'number', 'operator']:
    val = LIGHT[key]
    assert isinstance(val, tuple) and len(val) == 3, f"LIGHT[{key}] is not a 3-tuple: {val}"
    color, bold, italic = val
    assert isinstance(color, str) and color.startswith('#'), f"bad color: {color}"
print("  All theme values are valid 3-tuples")

print("Test 4: main_window imports (module level only)")
from npworks_ide.ide.output_panel import OutputPanel
from npworks_ide.ide.find_replace import FindReplacePanel
from npworks_ide.ide.file_tree import FileTree
from npworks_ide.runner.executor import Executor
print("  OK")

print("Test 5: verify no QPlainTextEdit refs in main_window")
main_window_path = os.path.join(os.path.dirname(__file__), '..', 'packages', 'npworks-ide', 'src', 'npworks_ide', 'ide', 'main_window.py')
with open(main_window_path, 'r', encoding='utf-8') as f:
    content = f.read()
assert 'QTextCursor' not in content, "QTextCursor still referenced"
assert 'QTextDocument' not in content, "QTextDocument still referenced"
assert 'textCursor()' not in content, "textCursor() still referenced"
assert 'blockNumber()' not in content, "blockNumber() still referenced"
print("  No stale QPlainTextEdit API references")

print("\nALL IMPORT & COMPATIBILITY TESTS PASSED")
