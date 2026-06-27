"""Python 运行环境控制器。

把虚拟环境管理（发现/创建/选择/安装包）从 MainWindow 中抽出，与
``RunController`` / ``FindController`` 等保持一致的控制器风格。负责：

- 持有 :class:`VEnvManager` 并在环境切换时同步 ``Executor`` 的解释器；
- 构建状态栏环境切换菜单；
- 提供添加/新建/安装/移除/切换等命令入口（供菜单、命令面板、设置页调用）。
"""
import os
import sys

from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

from npworks_ide.ide.controllers.env_manager import VEnvManager


class EnvController:
    def __init__(self, main_window, executor):
        self._mw = main_window
        self._executor = executor
        self.manager = VEnvManager(main_window)
        self._env_btn = None  # 由 MainWindow 通过 setup_status_button 注入

        self._executor.set_interpreter(self.manager.active_interpreter())
        self.manager.current_changed.connect(self._on_env_changed)
        self.manager.environments_changed.connect(self._refresh_env_status)

    # ---- 状态栏按钮 ----
    def setup_status_button(self, btn):
        """注入状态栏的 QToolButton 并刷新显示文本。"""
        self._env_btn = btn
        self._refresh_env_status()

    def _on_env_changed(self, _env_id):
        self._executor.set_interpreter(self.manager.active_interpreter())
        self._refresh_env_status()

    def _refresh_env_status(self):
        if self._env_btn is not None:
            self._env_btn.setText(f" {self.manager.current_display_label()} ")

    # ---- 菜单 ----
    def populate_menu(self, menu):
        """（重新）构建环境切换菜单内容。供 QMenu.aboutToShow 调用。"""
        menu.clear()
        cur = self.manager.current_id()
        for e in self.manager.all_environments():
            label = e.get("name", e.get("id", ""))
            ver = e.get("version") or ""
            text = f"{label} ({ver})" if ver else label
            if not e.get("valid", True):
                text += "  ⚠ 无效"
            act = QAction(text, self._mw, checkable=True)
            act.setChecked(e["id"] == cur)
            act.triggered.connect(
                lambda _checked, eid=e["id"]: self.manager.set_current(eid))
            menu.addAction(act)
        menu.addSeparator()
        menu.addAction("添加现有环境…", self.add_existing)
        menu.addAction("新建虚拟环境…", self.create_new)
        menu.addAction("安装 Python 包…", self.install_packages)
        menu.addAction("移除当前环境…", self.remove_current)
        menu.addSeparator()
        menu.addAction("在设置中管理…", self._mw._open_settings)

    # ---- 命令入口 ----
    def switch_palette(self):
        """命令面板：弹出环境切换菜单。"""
        if self._env_btn is not None:
            self._env_btn.showMenu()

    def add_existing(self):
        if sys.platform == "win32":
            flt = "Python 可执行文件 (*.exe);;所有文件 (*)"
        else:
            flt = "所有文件 (*)"
        path, _ = QFileDialog.getOpenFileName(
            self._mw, "选择 Python 解释器或虚拟环境目录",
            os.path.dirname(sys.executable), flt)
        if not path:
            return
        env = self.manager.add(path)
        if env is None:
            QMessageBox.warning(
                self._mw, "无法添加",
                "所选路径既不是有效的 Python 解释器，也不是有效的虚拟环境目录。")
            return
        self.manager.set_current(env["id"])

    def _suggest_dir(self):
        folders = self._mw.file_tree.get_open_folders()
        return folders[0] if folders else os.path.dirname(sys.executable)

    def create_new(self):
        from npworks_ide.ide.controllers.env_dialogs import CreateVEnvDialog
        dlg = CreateVEnvDialog(self.manager, suggest_dir=self._suggest_dir(),
                               parent=self._mw)
        dlg.exec_()

    def install_packages(self):
        from npworks_ide.ide.controllers.env_dialogs import PipInstallDialog
        dlg = PipInstallDialog(self.manager, parent=self._mw)
        dlg.exec_()

    def remove_current(self):
        cur = self.manager.current_id()
        if cur == VEnvManager.BASE_ID:
            QMessageBox.information(self._mw, "提示", "内置环境不可移除。")
            return
        env = self.manager.find(cur)
        name = env.get("name", cur) if env else cur
        btn = QMessageBox.question(
            self._mw, "移除环境",
            f"从环境列表中移除「{name}」？\n（不会删除磁盘上的文件）",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if btn == QMessageBox.Yes:
            self.manager.remove(cur)
