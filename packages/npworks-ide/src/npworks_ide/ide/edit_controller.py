class EditController:
    def __init__(self, main_window):
        self._mw = main_window

    def _current_editor(self):
        return self._mw._current_editor()

    def undo(self):
        editor = self._current_editor()
        if editor:
            editor.undo()

    def redo(self):
        editor = self._current_editor()
        if editor:
            editor.redo()

    def cut(self):
        editor = self._current_editor()
        if editor:
            editor.cut()

    def copy(self):
        editor = self._current_editor()
        if editor:
            editor.copy()

    def paste(self):
        editor = self._current_editor()
        if editor:
            editor.paste()

    def select_all(self):
        editor = self._current_editor()
        if editor:
            editor.selectAll()

    def toggle_comment(self):
        editor = self._current_editor()
        if editor:
            editor.toggle_comment()
