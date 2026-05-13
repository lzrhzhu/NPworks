import sys
import os

sys.path.insert(0, r'G:\npworks\packages\npworks-ide\src')
sys.path.insert(0, r'G:\npworks\packages\npworks-content\src')

print("Step 1: imports")
from npworks_ide.ide.editor import CodeEditor, PythonLexer
from PyQt5.Qsci import QsciScintilla
print("Step 2: OK - all imports successful")
print(f"  CodeEditor bases: {CodeEditor.__bases__}")
print(f"  PythonLexer bases: {PythonLexer.__bases__}")

print("\nStep 3: verify QScintilla features exist")
assert hasattr(QsciScintilla, 'setFolding'), "setFolding missing"
assert hasattr(QsciScintilla, 'setIndentationGuides'), "setIndentationGuides missing"
assert hasattr(QsciScintilla, 'findFirst'), "findFirst missing"
assert hasattr(QsciScintilla, 'setAutoIndent'), "setAutoIndent missing"
print("  All QScintilla features available")

print("\nStep 4: check PythonLexer style IDs")
from PyQt5.Qsci import QsciLexerPython
assert hasattr(QsciLexerPython, 'Keyword')
assert hasattr(QsciLexerPython, 'ClassName')
assert hasattr(QsciLexerPython, 'FunctionMethodName')
assert hasattr(QsciLexerPython, 'HighlightedIdentifier')
assert hasattr(QsciLexerPython, 'Decorator')
assert hasattr(QsciLexerPython, 'Comment')
assert hasattr(QsciLexerPython, 'Number')
assert hasattr(QsciLexerPython, 'Operator')
assert hasattr(QsciLexerPython, 'DoubleQuotedString')
print("  All lexer style IDs available")

print("\nALL STATIC TESTS PASSED")
