from datetime import datetime


class RunController:
    def __init__(self, main_window, executor, output_panel):
        self._mw = main_window
        self._executor = executor
        self._output = output_panel
        self._start_time = None
        self.terminal = None           # IPython TerminalWidget（懒创建）
        self.shell_terminal = None     # Shell TerminalPanel（懒创建）
        self._ipython_panel = None     # _LazyPanel
        self._shell_panel = None       # _LazyPanel

    def set_terminal_panels(self, ipython_panel, shell_panel):
        self._ipython_panel = ipython_panel
        self._shell_panel = shell_panel

    def _current_editor(self):
        return self._mw._current_editor()

    def _show_panel(self, panel_id):
        self._mw.layout.show_panel(panel_id)

    def _ensure_ipython(self):
        if self.terminal is None and self._ipython_panel is not None:
            self.terminal = self._ipython_panel.ensure()
        return self.terminal

    def _ensure_shell(self):
        if self.shell_terminal is None and self._shell_panel is not None:
            self.shell_terminal = self._shell_panel.ensure()
        return self.shell_terminal

    def run_code(self):
        editor = self._current_editor()
        if not editor:
            return
        code = editor.get_code()
        if not code.strip():
            return
        self._output.clear_output()
        self._start_time = datetime.now()
        self._output.append_system(">>> 运行中...")
        self._show_panel("output")
        if not self._executor.execute(code):
            self._start_time = None

    def stop_code(self):
        self._executor.stop()
        self._output.append_system("已手动终止")

    def reset_code(self):
        editor = self._current_editor()
        if editor:
            editor.reset_to_original()
            self._output.append_system("已重置为原始代码")

    def run_line_in_terminal(self):
        editor = self._current_editor()
        if not editor:
            return
        line, _ = editor.getCursorPosition()
        text = editor.text(line).strip()
        if text:
            self._show_panel("ipython")
            terminal = self._ensure_ipython()
            if terminal:
                terminal.execute_command(text)

    def run_line_in_shell(self):
        editor = self._current_editor()
        if not editor:
            return
        line, _ = editor.getCursorPosition()
        text = editor.text(line).strip()
        if text:
            self._show_panel("shell")
            shell = self._ensure_shell()
            if shell:
                shell.execute_command(text)

    def new_terminal(self):
        self._show_panel("shell")
        shell = self._ensure_shell()
        if shell:
            shell.add_terminal()

    def close_terminal(self):
        if self.shell_terminal:
            self.shell_terminal.close_terminal()

    def show_ipython_terminal(self):
        self._show_panel("ipython")
        self._ensure_ipython()

    def show_shell_terminal(self):
        self._show_panel("shell")
        self._ensure_shell()

    def send_input(self, text):
        self._executor.send_input(text)

    def on_execution_started(self):
        self._mw._run_label.setText(" ● 运行中 ")
        self._output.show_input()

    def on_execution_finished(self, exit_code, exit_status):
        self._output.hide_input()
        self._output.flush_output()
        if self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            self._mw._run_label.setText("")
            self._output.append_system(
                f"[运行完毕] 退出码={exit_code} 耗时={elapsed:.2f}s"
            )
            self._start_time = None
        else:
            self._mw._run_label.setText("")

    def create_terminal(self):
        from npworks_ide.ide.widgets.terminal import TerminalWidget
        self.terminal = TerminalWidget(self._mw)
        theme = self._mw._settings.value("theme", "light")
        self.terminal.set_theme(theme)
        return self.terminal

    def create_shell(self):
        from npworks_ide.ide.widgets.shell_terminal import TerminalPanel
        self.shell_terminal = TerminalPanel(self._mw)
        theme = self._mw._settings.value("theme", "light")
        self.shell_terminal.set_theme(theme)
        return self.shell_terminal

    def cleanup(self):
        if self.terminal:
            self.terminal.cleanup()
        if self.shell_terminal:
            self.shell_terminal.cleanup()
