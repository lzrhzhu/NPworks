from npworks_ide.ide.editor import CodeEditor
from npworks_ide.ide.preview_markdown import MarkdownSplitView
from npworks_ide.ide.themes import apply_theme


class ThemeController:
    def __init__(self, main_window, tab_widget, bottom_panel, settings):
        self._mw = main_window
        self._tab_widget = tab_widget
        self._bottom = bottom_panel
        self._settings = settings
        self._theme_actions = []

    def set_theme_actions(self, actions):
        self._theme_actions = actions

    def set_theme(self, name):
        from PyQt5.QtWidgets import QApplication
        apply_theme(QApplication.instance(), name)
        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            if isinstance(widget, MarkdownSplitView):
                widget.get_editor().apply_theme()
            elif isinstance(widget, CodeEditor):
                widget.apply_theme()
        run_ctrl = self._mw.run_ctrl
        if run_ctrl.terminal:
            run_ctrl.terminal.set_theme(name)
        if run_ctrl.shell_terminal:
            run_ctrl.shell_terminal.set_theme(name)
        for action in self._theme_actions:
            action.setChecked(False)
        if name == "dark":
            self._theme_actions[1].setChecked(True)
        else:
            self._theme_actions[0].setChecked(True)

    def get_current_theme(self):
        return self._settings.value("theme", "light")
