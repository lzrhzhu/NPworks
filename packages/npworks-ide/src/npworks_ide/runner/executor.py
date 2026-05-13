import sys
import tempfile
import os
import glob

from PyQt5.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal

_MATPLOTLIB_RC = (
    "import matplotlib\n"
    "matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']\n"
    "matplotlib.rcParams['axes.unicode_minus'] = False\n"
)

_RC_LINE_COUNT = _MATPLOTLIB_RC.count("\n")


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
        self._temp_file.write(_MATPLOTLIB_RC)
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
