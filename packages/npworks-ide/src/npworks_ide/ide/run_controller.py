from datetime import datetime


class RunController:
    def __init__(self, main_window, executor, output_panel, bottom_panel):
        self._mw = main_window
        self._executor = executor
        self._output = output_panel
        self._bottom = bottom_panel
        self._start_time = None
        self.terminal = None
        self.shell_terminal = None

    def _current_editor(self):
        return self._mw._current_editor()

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
        self._bottom.show()
        self._bottom.show_output_tab()
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
            self._bottom.show()
            self._bottom.show_terminal_tab()
            self._bottom.ensure_terminal()
            if self.terminal:
                self.terminal.execute_command(text)

    def run_line_in_shell(self):
        editor = self._current_editor()
        if not editor:
            return
        line, _ = editor.getCursorPosition()
        text = editor.text(line).strip()
        if text:
            self._bottom.show()
            self._bottom.show_shell_tab()
            self._bottom.ensure_shell()
            if self.shell_terminal:
                self.shell_terminal.execute_command(text)

    def new_terminal(self):
        self._bottom.show()
        self._bottom.show_shell_tab()
        if self.shell_terminal:
            self.shell_terminal.add_terminal()

    def close_terminal(self):
        if self.shell_terminal:
            self.shell_terminal.close_terminal()

    def show_ipython_terminal(self):
        self._bottom.show()
        self._bottom.show_terminal_tab()

    def show_shell_terminal(self):
        self._bottom.show()
        self._bottom.show_shell_tab()

    def send_input(self, text):
        self._executor.send_input(text)

    def on_execution_started(self):
        self._mw._run_label.setText(" ● 运行中 ")
        self._output.show_input()

    def on_execution_finished(self, exit_code, exit_status):
        self._output.hide_input()
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
        from npworks_ide.ide.terminal import TerminalWidget
        self.terminal = TerminalWidget(self._mw)
        theme = self._mw._settings.value("theme", "light")
        self.terminal.set_theme(theme)
        return self.terminal

    def create_shell(self):
        from npworks_ide.ide.shell_terminal import TerminalPanel
        self.shell_terminal = TerminalPanel(self._mw)
        theme = self._mw._settings.value("theme", "light")
        self.shell_terminal.set_theme(theme)
        return self.shell_terminal

    def cleanup(self):
        if self.terminal:
            self.terminal.cleanup()
        if self.shell_terminal:
            self.shell_terminal.cleanup()
