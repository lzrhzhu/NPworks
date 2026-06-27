class FindController:
    def __init__(self, main_window, find_replace_panel):
        self._mw = main_window
        self._panel = find_replace_panel

    def _current_editor(self):
        return self._mw._current_editor()

    def find_next(self):
        editor = self._current_editor()
        if not editor:
            return
        text = self._panel.get_find_text()
        if not text:
            return
        cs = self._panel.is_case_sensitive()
        ww = self._panel.is_whole_word()
        line, col = editor.getCursorPosition()
        col += 1
        found = editor.findFirst(text, False, cs, ww, True, line, col)
        if found:
            self._panel.set_match_count(1, 1)
        else:
            found = editor.findFirst(text, False, cs, ww, True, 0, 0)
            if found:
                self._panel.set_match_count(1, 1)
            else:
                self._panel.set_match_count(0, 0)

    def find_prev(self):
        editor = self._current_editor()
        if not editor:
            return
        text = self._panel.get_find_text()
        if not text:
            return
        cs = self._panel.is_case_sensitive()
        ww = self._panel.is_whole_word()
        line, col = editor.getCursorPosition()
        found = editor.findFirst(text, False, cs, ww, False, line, col)
        if not found:
            last_line = editor.lines() - 1
            line_len = len(editor.text(last_line))
            editor.findFirst(text, False, cs, ww, False, last_line, line_len)

    def replace_one(self):
        editor = self._current_editor()
        if not editor:
            return
        find_text = self._panel.get_find_text()
        replace_text = self._panel.get_replace_text()
        if not find_text:
            return
        if editor.hasSelectedText() and editor.selectedText() == find_text:
            editor.replaceSelectedText(replace_text)
        self.find_next()

    def replace_all(self):
        editor = self._current_editor()
        if not editor:
            return
        find_text = self._panel.get_find_text()
        replace_text = self._panel.get_replace_text()
        if not find_text:
            return
        cs = self._panel.is_case_sensitive()
        ww = self._panel.is_whole_word()
        editor.beginUndoAction()
        editor.setCursorPosition(0, 0)
        count = 0
        found = editor.findFirst(find_text, False, cs, ww, True, 0, 0)
        while found:
            editor.replaceSelectedText(replace_text)
            count += 1
            found = editor.findNext()
        editor.endUndoAction()
        self._panel.set_match_count(count, count)

    def clear_find_highlight(self):
        pass
