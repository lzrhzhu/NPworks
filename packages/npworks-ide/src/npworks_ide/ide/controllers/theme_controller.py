from npworks_ide.ide.themes import apply_theme
from npworks_ide.ide.plugin.editor_registry import EditorView


class ThemeController:
    def __init__(self, main_window, tab_widget, settings):
        self._mw = main_window
        self._tab_widget = tab_widget
        self._settings = settings
        self._theme_actions = []

    def set_theme_actions(self, actions):
        self._theme_actions = actions

    def set_theme(self, name):
        from PyQt5.QtWidgets import QApplication
        apply_theme(QApplication.instance(), name)
        self._mw.activity_bar.apply_theme_icons(name)
        self._mw._refresh_toolbar_icons()
        self._mw.layout.refresh_sidebar_icons()
        self._apply_window_icon(name)
        self._mw._apply_titlebar(name)
        if self._mw._win_controls is not None:
            self._mw._win_controls.refresh_icons(name)
        for i in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(i)
            if isinstance(widget, EditorView):
                widget.apply_theme(name)
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

    def _apply_window_icon(self, theme_name):
        from npworks_ide.ide.platform import icons
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
        self._mw.setWindowIcon(icons.logo_icon(v["activity_checked_fg"], 64))

    def apply_window_icon(self):
        self._apply_window_icon(self.get_current_theme())
