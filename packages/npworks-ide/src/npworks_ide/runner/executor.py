import sys
import tempfile
import os
import glob

from PyQt5.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal

# 注入到用户代码前的预处理：用 Agg 后端，拦截 plt.show 把 figure 存成 PNG
# 并打印 "__NPWORKS_FIG__:<path>" 标记，输出面板据此内联显示图片。
_PROLOGUE = (
    "import matplotlib\n"
    "matplotlib.use('Agg')\n"
    "matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']\n"
    "matplotlib.rcParams['axes.unicode_minus'] = False\n"
    "import matplotlib.pyplot as _npw_plt\n"
    "import atexit as _npw_atexit, os as _npw_os, tempfile as _npw_tmp\n"
    "def _npw_emit_fig(p):\n"
    "    print('__NPWORKS_FIG__:' + p, flush=True)\n"
    "def _npw_dump_figs():\n"
    "    for _n in list(_npw_plt.get_fignums()):\n"
    "        _f = _npw_plt.figure(_n)\n"
    "        _p = _npw_os.path.join(_npw_tmp.gettempdir(), 'npworks_fig_%d.png' % _n)\n"
    "        try:\n"
    "            _f.savefig(_p, dpi=110, bbox_inches='tight')\n"
    "            _npw_emit_fig(_p)\n"
    "        except Exception as _e:\n"
    "            print('figure save failed:', _e)\n"
    "        _npw_plt.close(_n)\n"
    "_npw_plt.show = _npw_dump_figs\n"
    "_npw_atexit.register(_npw_dump_figs)\n"
)

_RC_LINE_COUNT = _PROLOGUE.count("\n")

# 关闭捕获时使用的最小预处理（仅字体），不强制 Agg、不拦截 show
_PROLOGUE_PLAIN = (
    "import matplotlib\n"
    "matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']\n"
    "matplotlib.rcParams['axes.unicode_minus'] = False\n"
)
# 用注释行补齐到与 _PROLOGUE 相同行数，保证 traceback 行号偏移一致
_pad = _RC_LINE_COUNT - _PROLOGUE_PLAIN.count("\n")
if _pad > 0:
    _PROLOGUE_PLAIN += ("# \n" * _pad)


def _capture_enabled():
    try:
        from PyQt5.QtCore import QSettings
        return QSettings("npworks", "npworks").value("run/capture_figures", "1") != "0"
    except Exception:
        return True


def _cleanup_stale_temp_files():
    tmp_dir = tempfile.gettempdir()
    pattern = os.path.join(tmp_dir, "npworks_*.py")
    for f in glob.glob(pattern):
        try:
            os.unlink(f)
        except OSError:
            pass


class Executor(QObject):
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal(int, QProcess.ExitStatus)
    stdout_ready = pyqtSignal(str)
    stderr_ready = pyqtSignal(str)
    input_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._temp_file = None
        _cleanup_stale_temp_files()

    def execute(self, code: str):
        if self.is_running():
            return False

        self._temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix="npworks_", delete=False, encoding="utf-8"
        )
        prologue = _PROLOGUE if _capture_enabled() else _PROLOGUE_PLAIN
        self._temp_file.write(prologue)
        self._temp_file.write(code)
        self._temp_file.close()

        self._process = QProcess(self)
        self._process.setProcessEnvironment(self._build_env())
        self._process.setProcessChannelMode(QProcess.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        self._process.start(sys.executable, [self._temp_file.name])
        self.execution_started.emit()
        return True

    def stop(self):
        if self.is_running():
            self._process.kill()
            self._process.waitForFinished(3000)

    def send_input(self, text: str):
        if self.is_running():
            self._process.write((text + "\n").encode("utf-8"))

    def is_running(self) -> bool:
        return self._process is not None and self._process.state() != QProcess.NotRunning

    def _on_stdout(self):
        data = self._process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="replace")
        self.stdout_ready.emit(text)

    def _on_stderr(self):
        data = self._process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="replace")
        self.stderr_ready.emit(text)

    def _on_finished(self, exit_code, exit_status):
        self.execution_finished.emit(exit_code, exit_status)
        if self._temp_file:
            try:
                os.unlink(self._temp_file.name)
            except OSError:
                pass
            self._temp_file = None

    def _build_env(self):
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        return env
