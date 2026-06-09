from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction


class MenuBuilder:
    def __init__(self, main_window):
        self._mw = main_window

    def build_menu_bar(self):
        mb = self._mw.menuBar()

        file_menu = mb.addMenu("文件(&F)")
        self._add_action(file_menu, "新建(&N)", self._mw._new_file, QKeySequence.New)
        self._add_action(file_menu, "打开(&O)...", self._mw._open_file, QKeySequence.Open)
        self._add_action(file_menu, "打开文件夹(&F)...", self._mw._open_folder)
        recent_menu = file_menu.addMenu("最近文件(&R)")
        self._mw._actions.set_recent_menu(recent_menu)
        file_menu.addSeparator()
        self._add_action(file_menu, "关闭标签(&C)", self._mw._close_tab,
                         QKeySequence(Qt.ControlModifier | Qt.Key_W))
        self._add_action(file_menu, "关闭文件夹(&W)", self._mw._close_current_folder)
        file_menu.addSeparator()
        self._add_action(file_menu, "保存(&S)", self._mw._save_code, QKeySequence.Save)
        self._add_action(file_menu, "全部保存(&L)", self._mw._save_all,
                         QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_S))
        self._add_action(file_menu, "另存为(&A)...", self._mw._save_as, QKeySequence.SaveAs)
        file_menu.addSeparator()
        self._add_action(file_menu, "退出(&Q)", self._mw.close, QKeySequence.Quit)

        edit_menu = mb.addMenu("编辑(&E)")
        self._add_action(edit_menu, "撤销(&U)", self._mw.edit_ctrl.undo, QKeySequence.Undo)
        self._add_action(edit_menu, "重做(&R)", self._mw.edit_ctrl.redo, QKeySequence.Redo)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "剪切(&X)", self._mw.edit_ctrl.cut, QKeySequence.Cut)
        self._add_action(edit_menu, "复制(&C)", self._mw.edit_ctrl.copy, QKeySequence.Copy)
        self._add_action(edit_menu, "粘贴(&V)", self._mw.edit_ctrl.paste, QKeySequence.Paste)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "全选(&A)", self._mw.edit_ctrl.select_all, QKeySequence.SelectAll)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "注释/取消注释(&C)", self._mw.edit_ctrl.toggle_comment,
                         QKeySequence(Qt.ControlModifier | Qt.Key_Slash))
        edit_menu.addSeparator()
        self._add_action(edit_menu, "查找(&F)...", self._mw._show_find, QKeySequence.Find)
        self._add_action(edit_menu, "查找替换(&H)...", self._mw._show_replace, QKeySequence.Replace)
        self._add_action(edit_menu, "跳转到行(&G)...", self._mw._go_to_line,
                         QKeySequence(Qt.ControlModifier | Qt.Key_G))

        run_menu = mb.addMenu("运行(&R)")
        self._add_action(run_menu, "运行(&R)", self._mw.run_ctrl.run_code, QKeySequence(Qt.Key_F5))
        self._add_action(run_menu, "停止(&S)", self._mw.run_ctrl.stop_code,
                         QKeySequence(Qt.ShiftModifier | Qt.Key_F5))
        run_menu.addSeparator()
        self._add_action(run_menu, "重置代码(&E)", self._mw.run_ctrl.reset_code,
                         QKeySequence(Qt.ControlModifier | Qt.Key_R))
        run_menu.addSeparator()
        self._add_action(run_menu, "在终端中运行当前行", self._mw.run_ctrl.run_line_in_terminal)
        self._add_action(run_menu, "在终端中运行当前行 (Shell)", self._mw.run_ctrl.run_line_in_shell)
        run_menu.addSeparator()
        self._add_action(run_menu, "新建终端", self._mw.run_ctrl.new_terminal,
                         QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_QuoteLeft))
        self._add_action(run_menu, "关闭当前终端", self._mw.run_ctrl.close_terminal)

        view_menu = mb.addMenu("视图(&V)")
        self._add_action(view_menu, "文件浏览器(&E)", self._mw._toggle_explorer)
        self._add_action(view_menu, "大纲(&O)", self._mw._toggle_outline)
        self._add_action(view_menu, "底部面板(&B)", self._mw._toggle_bottom_panel,
                         QKeySequence(Qt.ControlModifier | Qt.Key_QuoteLeft))
        view_menu.addSeparator()
        self._add_action(view_menu, "IPython 终端(&I)", self._mw.run_ctrl.show_ipython_terminal)
        self._add_action(view_menu, "Shell 终端(&S)", self._mw.run_ctrl.show_shell_terminal)
        view_menu.addSeparator()

        light_action = QAction("亮色主题(&L)", self._mw, checkable=True, checked=True)
        light_action.triggered.connect(lambda: self._mw.theme_ctrl.set_theme("light"))
        dark_action = QAction("暗色主题(&D)", self._mw, checkable=True)
        dark_action.triggered.connect(lambda: self._mw.theme_ctrl.set_theme("dark"))
        theme_menu = view_menu.addMenu("主题(&T)")
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)

        saved_theme = QSettings("npworks", "npworks").value("theme", "light")
        if saved_theme == "dark":
            dark_action.setChecked(True)
            light_action.setChecked(False)

        help_menu = mb.addMenu("帮助(&H)")
        self._add_action(help_menu, "关于(&A)", self._mw._show_about)

        return [light_action, dark_action]

    def _add_action(self, menu, text, slot, shortcut=None):
        action = QAction(text, self._mw)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action
