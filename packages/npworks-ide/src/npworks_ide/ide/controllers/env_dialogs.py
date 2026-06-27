"""虚拟环境相关对话框：异步创建环境、安装包（基于 QProcess，不阻塞 UI）。"""
import os
import sys

from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QCheckBox, QPushButton, QFileDialog, QTextEdit, QMessageBox,
    QWidget,
)

from npworks_ide.ide.controllers.env_manager import probe_version


def _hbox(*widgets, stretch=False):
    box = QHBoxLayout()
    box.setContentsMargins(0, 0, 0, 0)
    for w in widgets:
        box.addWidget(w)
    if stretch:
        box.addStretch()
    return box


class _ProcessDialog(QDialog):
    """运行单个子进程并实时显示输出的基类对话框。"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(620, 420)
        self._proc = None
        self._on_success = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        self._form_widget = QWidget()

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(self._mono_font())
        self._log.setMinimumHeight(160)

        # 先创建按钮，子类 _build_form 可配置其文本
        self._run_btn = QPushButton("开始")
        self._close_btn = QPushButton("关闭")
        self._close_btn.clicked.connect(self.accept)

        # 子类构建表单（期间可设置 _run_btn 文本）
        self._build_form(self._form_widget)
        self._run_btn.clicked.connect(self._run_handler)

        # 按视觉顺序装配布局
        root.addWidget(self._form_widget)
        root.addWidget(QLabel("输出"))
        root.addWidget(self._log)
        box = _hbox(self._run_btn, self._close_btn, stretch=True)
        root.addLayout(box)

    def _build_form(self, widget):  # 子类实现
        raise NotImplementedError

    def _run_handler(self):  # 子类实现：点击主按钮时的动作
        pass

    def _mono_font(self):
        from PyQt5.QtGui import QFont
        return QFont("Consolas", 10)

    # ---- 进程控制 ----
    def _start(self, program, args, cwd=None, on_success=None):
        if self._proc is not None and self._proc.state() != QProcess.NotRunning:
            return
        self._on_success = on_success
        self._log.clear()
        self._set_running(True)
        self._proc = QProcess(self)
        self._proc.setProcessChannelMode(QProcess.MergedChannels)
        self._proc.setProcessEnvironment(self._clean_env())
        self._proc.readyReadStandardOutput.connect(self._on_output)
        self._proc.finished.connect(self._on_finished)
        if cwd:
            self._proc.setWorkingDirectory(cwd)
        self._append(f"$ {program} {' '.join(args)}\n\n")
        self._proc.start(program, args)

    @staticmethod
    def _clean_env():
        env = QProcessEnvironment.systemEnvironment()
        env.remove("PYTHONHOME")
        env.remove("PYTHONPATH")
        return env

    def _on_output(self):
        data = self._proc.readAllStandardOutput()
        self._append(bytes(data).decode("utf-8", errors="replace"))

    def _on_finished(self, code, _status):
        self._append(f"\n[进程退出，返回码 {code}]\n")
        self._set_running(False)
        if code == 0 and self._on_success:
            try:
                self._on_success()
            except Exception as ex:
                self._append(f"\n[后续操作失败: {ex}]\n")

    def _append(self, text):
        self._log.moveCursor(self._log.textCursor().End)
        self._log.insertPlainText(text)
        self._log.ensureCursorVisible()

    def _set_running(self, running):
        self._run_btn.setEnabled(not running)
        self._close_btn.setEnabled(not running)

    def reject(self):
        if self._proc is not None and self._proc.state() != QProcess.NotRunning:
            self._proc.kill()
            self._proc.waitForFinished(3000)
        super().reject()


class CreateVEnvDialog(_ProcessDialog):
    """新建虚拟环境对话框。

    成功后自动把新环境注册到 :class:`VEnvManager` 并设为当前活动环境。
    """

    def __init__(self, venv_manager, suggest_dir=None, parent=None):
        self._mgr = venv_manager
        self._suggest_dir = suggest_dir
        super().__init__("新建虚拟环境", parent)

    def _build_form(self, widget):
        form = QFormLayout(widget)
        form.setContentsMargins(0, 0, 0, 8)
        form.setSpacing(8)

        self._dest_edit = QLineEdit()
        if self._suggest_dir:
            self._dest_edit.setText(os.path.join(self._suggest_dir, ".venv"))
        dest_btn = QPushButton("浏览…")
        dest_btn.clicked.connect(self._pick_dest)
        form.addRow("目标目录", _hbox(self._dest_edit, dest_btn))

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("留空则用目录名")
        form.addRow("显示名称", self._name_edit)

        self._base_combo = QComboBox()
        self._populate_base()
        base_btn = QPushButton("浏览…")
        base_btn.clicked.connect(self._pick_base)
        form.addRow("基础解释器", _hbox(self._base_combo, base_btn))

        self._syspkg = QCheckBox("继承系统站点包 (--system-site-packages)")
        form.addRow("", self._syspkg)

        self._run_btn.setText("创建环境")

    def _run_handler(self):
        self._do_create()

    def _populate_base(self):
        self._base_combo.clear()
        # 第一项：IDE 内置解释器
        base_exe = sys.executable
        self._base_combo.addItem(f"IDE 内置 ({probe_version(base_exe)})", base_exe)
        # 已注册的可执行文件
        seen = {base_exe}
        for e in self._mgr.all_environments():
            exe = self._mgr._interpreter_for(e)
            if exe and exe not in seen:
                self._base_combo.addItem(f"{e['name']} ({e.get('version','')})", exe)
                seen.add(exe)

    def _pick_dest(self):
        start = self._dest_edit.text() or self._suggest_dir or ""
        d = QFileDialog.getExistingDirectory(self, "选择虚拟环境目录", start)
        if d:
            self._dest_edit.setText(d)

    def _pick_base(self):
        start = os.path.dirname(sys.executable)
        flt = "Python 可执行文件 (*.exe);;所有文件 (*)" if sys.platform == "win32" \
            else "所有文件 (*)"
        p, _ = QFileDialog.getOpenFileName(self, "选择基础 Python 解释器", start, flt)
        if p:
            label = f"{os.path.basename(p)} ({probe_version(p)})"
            self._base_combo.addItem(label, p)
            self._base_combo.setCurrentIndex(self._base_combo.count() - 1)

    def _do_create(self):
        dest = self._dest_edit.text().strip()
        if not dest:
            QMessageBox.warning(self, "提示", "请填写目标目录。")
            return
        dest = os.path.normpath(dest)
        if os.path.exists(dest) and os.listdir(dest):
            QMessageBox.warning(self, "提示", f"目标目录非空：\n{dest}")
            return
        base = self._base_combo.currentData()
        if not base or not os.path.isfile(base):
            QMessageBox.warning(self, "提示", "请选择有效的基础解释器。")
            return
        name = self._name_edit.text().strip() or os.path.basename(dest.rstrip(os.sep))
        args = ["-m", "venv"]
        if self._syspkg.isChecked():
            args.append("--system-site-packages")
        args.append(dest)

        def on_success():
            env = self._mgr.add(dest, name=name)
            if env:
                self._mgr.set_current(env["id"])
            self._append(f"\n已创建并设为当前环境：{name}\n")

        self._start(base, args, on_success=on_success)


class PipInstallDialog(_ProcessDialog):
    """向指定环境安装第三方包。"""

    def __init__(self, venv_manager, parent=None):
        self._mgr = venv_manager
        super().__init__("安装 Python 包", parent)

    def _build_form(self, widget):
        form = QFormLayout(widget)
        form.setContentsMargins(0, 0, 0, 8)
        form.setSpacing(8)

        self._env_combo = QComboBox()
        self._populate_envs()
        form.addRow("目标环境", self._env_combo)

        self._pkgs_edit = QLineEdit()
        self._pkgs_edit.setPlaceholderText("例如 numpy scipy matplotlib（空格分隔）")
        form.addRow("包名", self._pkgs_edit)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self._install_btn = QPushButton("安装")
        self._freeze_btn = QPushButton("查看已装包")
        self._install_btn.clicked.connect(self._do_install)
        self._freeze_btn.clicked.connect(self._do_freeze)
        row.addWidget(self._install_btn)
        row.addWidget(self._freeze_btn)
        row.addStretch()
        form.addRow("", row)

        self._run_btn.setText("安装")

    def _run_handler(self):
        self._do_install()

    def _populate_envs(self):
        cur = self._mgr.current_id()
        idx = 0
        for i, e in enumerate(self._mgr.all_environments()):
            self._env_combo.addItem(
                f"{e['name']} ({e.get('version','')})", e["id"])
            if e["id"] == cur:
                idx = i
        self._env_combo.setCurrentIndex(idx)

    def _current_env(self):
        return self._env_combo.currentData()

    def _current_python(self):
        env = self._mgr.find(self._current_env())
        return self._mgr._interpreter_for(env) if env else None

    def _do_install(self):
        py = self._current_python()
        if not py or not os.path.isfile(py):
            QMessageBox.warning(self, "提示", "所选环境解释器无效。")
            return
        pkgs = [p.strip() for p in self._pkgs_edit.text().split() if p.strip()]
        if not pkgs:
            QMessageBox.warning(self, "提示", "请填写至少一个包名。")
            return
        self._start(py, ["-m", "pip", "install"] + pkgs)

    def _do_freeze(self):
        py = self._current_python()
        if not py or not os.path.isfile(py):
            QMessageBox.warning(self, "提示", "所选环境解释器无效。")
            return
        self._start(py, ["-m", "pip", "freeze"])
