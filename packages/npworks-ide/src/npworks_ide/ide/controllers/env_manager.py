"""虚拟环境管理：发现、创建、选择 Python 解释器 / 虚拟环境。

跨平台支持：
- Windows：虚拟环境内可执行文件位于 ``<venv>/Scripts/python.exe``
- Linux / Ubuntu：位于 ``<venv>/bin/python``

当前活动环境用于执行用户代码（见 :mod:`npworks_ide.runner.executor`）。
环境列表以 JSON 持久化在 QSettings 中，活动环境以环境 id 记录。
"""
import os
import sys
import json
import subprocess

from PyQt5.QtCore import QObject, QSettings, pyqtSignal

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    _BIN_DIR = "Scripts"
    _PY_NAME = "python.exe"
else:
    _BIN_DIR = "bin"
    _PY_NAME = "python"

# 常见虚拟环境目录名（用于自动发现）
_COMMON_VENV_DIRS = (".venv", "venv", "env", ".env")


def venv_python(venv_dir):
    """返回某虚拟环境目录对应的 python 可执行文件绝对路径。"""
    return os.path.join(venv_dir, _BIN_DIR, _PY_NAME)


def is_valid_venv(venv_dir):
    """判断目录是否为有效的 Python 虚拟环境。"""
    if not venv_dir or not os.path.isdir(venv_dir):
        return False
    return (os.path.isfile(os.path.join(venv_dir, "pyvenv.cfg"))
            and os.path.isfile(venv_python(venv_dir)))


def is_python_executable(path):
    """判断路径是否为 python 可执行文件（按名称粗判 + 存在性）。"""
    if not path or not os.path.isfile(path):
        return False
    base = os.path.basename(path).lower()
    return base in ("python.exe", "python", "python3", "python3.exe") \
        or base.startswith("python")


def probe_version(executable):
    """调用 ``python --version`` 获取版本字符串，失败返回空串。"""
    if not executable or not os.path.isfile(executable):
        return ""
    try:
        proc = subprocess.run(
            [executable, "--version"],
            capture_output=True, text=True, timeout=15,
        )
        out = (proc.stdout or proc.stderr).strip()
        return out.replace("Python ", "").strip()
    except Exception:
        return ""


class VEnvManager(QObject):
    """虚拟环境管理器。

    环境条目结构::

        {
            "id":   唯一标识（venv 用目录路径，解释器用可执行文件路径），
            "name": 显示名称,
            "kind": "venv" | "interpreter",
            "path": venv 目录 或 可执行文件路径,
            "version": "3.10.8",   # 缓存的版本
        }

    内置 "base" 环境（id = :data:`BASE_ID`）始终存在，对应启动 IDE 的
    ``sys.executable``。
    """

    environments_changed = pyqtSignal()
    current_changed = pyqtSignal(str)

    BASE_ID = "__base__"
    BASE_NAME = "IDE 内置环境"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("npworks", "npworks")

    # ------------------------------------------------------------------ #
    #  持久化
    # ------------------------------------------------------------------ #
    def _load(self):
        raw = self._settings.value("venv/environments", None)
        if not raw:
            return []
        if isinstance(raw, (list, tuple)):
            return list(raw)
        try:
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save(self, envs):
        self._settings.setValue("venv/environments", json.dumps(envs, ensure_ascii=False))

    # ------------------------------------------------------------------ #
    #  列举
    # ------------------------------------------------------------------ #
    def base_env(self):
        return {
            "id": self.BASE_ID,
            "name": self.BASE_NAME,
            "kind": "base",
            "path": sys.executable,
            "version": sys.version.split()[0],
            "valid": True,
        }

    def _decorate(self, entry):
        """补齐运行时字段（valid / version）并规范化类型。"""
        e = dict(entry)
        e["valid"] = self._is_entry_valid(e)
        if not e.get("version"):
            e["version"] = probe_version(self._interpreter_for(e))
        return e

    def _is_entry_valid(self, e):
        kind = e.get("kind", "venv")
        path = e.get("path", "")
        if kind == "interpreter":
            return os.path.isfile(path)
        return is_valid_venv(path)

    def all_environments(self):
        """返回所有环境（base 在首位），每项含 valid/version 字段。"""
        result = [self.base_env()]
        for e in self._load():
            result.append(self._decorate(e))
        return result

    def find(self, env_id):
        """按 id 查找环境（含 base）。"""
        if env_id == self.BASE_ID:
            return self.base_env()
        for e in self._load():
            if e.get("id") == env_id:
                return self._decorate(e)
        return None

    # ------------------------------------------------------------------ #
    #  当前活动环境
    # ------------------------------------------------------------------ #
    def current_id(self):
        cid = self._settings.value("venv/current", self.BASE_ID, type=str)
        if cid == self.BASE_ID:
            return self.BASE_ID
        if any(e.get("id") == cid for e in self._load()):
            return cid
        return self.BASE_ID

    def set_current(self, env_id):
        ids = [self.BASE_ID] + [e.get("id") for e in self._load()]
        if env_id not in ids:
            return False
        self._settings.setValue("venv/current", env_id)
        self.current_changed.emit(env_id)
        self.environments_changed.emit()
        return True

    def _interpreter_for(self, entry):
        """解析某环境条目对应的 python 可执行文件路径；无效则回退 base。"""
        kind = entry.get("kind", "venv")
        path = entry.get("path", "")
        if kind == "base":
            return sys.executable
        if kind == "interpreter":
            return path if os.path.isfile(path) else sys.executable
        # venv
        return venv_python(path) if is_valid_venv(path) else sys.executable

    def active_interpreter(self):
        """当前活动环境的 python 可执行文件绝对路径。"""
        env = self.find(self.current_id())
        if env is None:
            return sys.executable
        return self._interpreter_for(env)

    def current_display_name(self):
        env = self.find(self.current_id())
        if env is None:
            return self.BASE_NAME
        return env.get("name", env.get("id", self.BASE_NAME))

    def current_display_label(self):
        """状态栏展示文本：``名称 (版本)``。"""
        env = self.find(self.current_id())
        if env is None:
            return self.BASE_NAME
        name = env.get("name", self.BASE_NAME)
        ver = env.get("version") or ""
        return f"{name} ({ver})" if ver else name

    # ------------------------------------------------------------------ #
    #  增删改
    # ------------------------------------------------------------------ #
    def add(self, path, name=None):
        """添加一个虚拟环境目录或 python 可执行文件，返回新增/更新条目或 None。"""
        if not path:
            return None
        path = os.path.normpath(path)
        if os.path.isfile(path) and is_python_executable(path):
            return self._upsert({
                "id": path, "name": name or os.path.basename(path),
                "kind": "interpreter", "path": path,
                "version": probe_version(path),
            })
        if is_valid_venv(path):
            return self._upsert({
                "id": path, "name": name or os.path.basename(path.rstrip(os.sep)) or "venv",
                "kind": "venv", "path": path,
                "version": probe_version(venv_python(path)),
            })
        return None

    def _upsert(self, env):
        envs = self._load()
        for i, e in enumerate(envs):
            if e.get("id") == env["id"]:
                envs[i] = env
                break
        else:
            envs.append(env)
        self._save(envs)
        self.environments_changed.emit()
        return env

    def remove(self, env_id):
        if not env_id or env_id == self.BASE_ID:
            return False
        envs = [e for e in self._load() if e.get("id") != env_id]
        self._save(envs)
        if self.current_id() == env_id:
            self.set_current(self.BASE_ID)
        else:
            self.environments_changed.emit()
        return True

    def rename(self, env_id, name):
        envs = self._load()
        changed = False
        for e in envs:
            if e.get("id") == env_id:
                e["name"] = name
                changed = True
                break
        if changed:
            self._save(envs)
            self.environments_changed.emit()
        return changed

    # ------------------------------------------------------------------ #
    #  创建 / pip
    # ------------------------------------------------------------------ #
    def create_venv(self, dest_dir, base_python=None, name=None,
                    system_site_packages=False):
        """同步创建虚拟环境（可能耗时数十秒）。

        返回 ``(ok, message_or_env)``。建议在后台线程调用，或使用
        :class:`npworks_ide.ide.controllers.env_dialogs.CreateVEnvDialog` 的异步实现。
        """
        base_python = base_python or sys.executable
        if not os.path.isfile(base_python):
            return False, f"找不到基础解释器: {base_python}"
        dest_dir = os.path.normpath(dest_dir)
        if os.path.exists(dest_dir) and os.listdir(dest_dir):
            return False, f"目标目录非空: {dest_dir}"
        cmd = [base_python, "-m", "venv"]
        if system_site_packages:
            cmd.append("--system-site-packages")
        cmd.append(dest_dir)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        except Exception as ex:
            return False, f"创建失败: {ex}"
        if proc.returncode != 0:
            return False, (proc.stderr or proc.stdout or "创建失败").strip()
        env = self.add(dest_dir, name=name)
        if env:
            self.set_current(env["id"])
        return True, env

    def pip_install(self, env_id, packages):
        """同步执行 ``pip install``。返回 ``(ok, output)``。"""
        env = self.find(env_id)
        if not env:
            return False, "环境不存在"
        py = self._interpreter_for(env)
        if not os.path.isfile(py):
            return False, "解释器无效或不存在"
        pkgs = [p for p in packages if p and p.strip()]
        if not pkgs:
            return False, "未指定包"
        cmd = [py, "-m", "pip", "install"] + pkgs
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        except Exception as ex:
            return False, f"pip 执行失败: {ex}"
        ok = proc.returncode == 0
        return ok, (proc.stdout or "") + (proc.stderr or "")

    def pip_freeze(self, env_id):
        env = self.find(env_id)
        if not env:
            return False, "环境不存在"
        py = self._interpreter_for(env)
        if not os.path.isfile(py):
            return False, "解释器无效或不存在"
        try:
            proc = subprocess.run([py, "-m", "pip", "freeze"],
                                  capture_output=True, text=True, timeout=60)
        except Exception as ex:
            return False, f"pip 执行失败: {ex}"
        return proc.returncode == 0, proc.stdout or proc.stderr

    # ------------------------------------------------------------------ #
    #  自动发现
    # ------------------------------------------------------------------ #
    def discover_in_folders(self, folders, max_depth=3):
        """在给定文件夹下扫描常见虚拟环境目录，返回发现的 venv 目录列表。"""
        found = []
        for folder in folders:
            if not folder or not os.path.isdir(folder):
                continue
            self._scan(folder, found, depth=0, max_depth=max_depth)
        # 去重并过滤已注册
        existing = {e.get("id") for e in self._load()}
        result = []
        seen = set()
        for v in found:
            n = os.path.normpath(v)
            if n in seen or n in existing:
                continue
            seen.add(n)
            result.append(n)
        return result

    def _scan(self, folder, found, depth, max_depth):
        try:
            entries = os.listdir(folder)
        except OSError:
            return
        for name in _COMMON_VENV_DIRS:
            cand = os.path.join(folder, name)
            if is_valid_venv(cand):
                found.append(cand)
        if depth >= max_depth:
            return
        for name in entries:
            if name.startswith(".") and name not in _COMMON_VENV_DIRS:
                continue
            sub = os.path.join(folder, name)
            if os.path.isdir(sub) and not is_valid_venv(sub):
                # 避免深入 node_modules / venv 内部
                if name in ("site-packages", "node_modules", "__pycache__"):
                    continue
                self._scan(sub, found, depth + 1, max_depth)
