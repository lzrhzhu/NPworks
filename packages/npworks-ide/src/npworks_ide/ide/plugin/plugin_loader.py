"""插件发现与加载。

发现途径：
  1. Python 入口点 entry_points(group="npworks.plugins") —— pip 安装的插件
  2. 本地目录 ~/.npworks/extensions/*.py —— 免安装的脚本插件

启用/禁用状态持久化到 QSettings；加载过程逐个 try/except，单插件崩溃不影响整体。
"""
import importlib
import importlib.metadata
import importlib.util
import sys
from pathlib import Path

from PyQt5.QtCore import QSettings

GROUP = "npworks.plugins"


class Plugin:
    def __init__(self, name, source, kind, enabled=True):
        self.name = name
        self.source = source
        self.kind = kind          # "entrypoint" | "file"
        self.enabled = enabled
        self.error = None
        self.loaded = False


class PluginLoader:
    def __init__(self):
        self._settings = QSettings("npworks", "npworks")
        self._plugins = []

    def _entry_points(self):
        try:
            return list(importlib.metadata.entry_points(group=GROUP))
        except TypeError:
            return list(importlib.metadata.entry_points().get(GROUP, []))

    def discover(self):
        plugins = []
        seen = set()
        for ep in self._entry_points():
            if ep.name in seen:
                continue
            seen.add(ep.name)
            plugins.append(Plugin(ep.name, ep.value, "entrypoint"))

        local = Path.home() / ".npworks" / "extensions"
        if local.is_dir():
            for f in sorted(local.glob("*.py")):
                if f.stem in seen:
                    continue
                seen.add(f.stem)
                plugins.append(Plugin(f.stem, str(f), "file"))

        for p in plugins:
            p.enabled = self._is_enabled(p)
        self._plugins = plugins
        return plugins

    def _is_enabled(self, plugin):
        return self._settings.value(f"plugins/{plugin.name}", "1") != "0"

    def set_enabled(self, name, on):
        self._settings.setValue(f"plugins/{name}", "1" if on else "0")

    def load(self, api):
        for p in self._plugins:
            if not p.enabled:
                continue
            try:
                if p.kind == "entrypoint":
                    ep = next((e for e in self._entry_points() if e.name == p.name), None)
                    if ep is None:
                        p.error = "入口点丢失"
                        continue
                    obj = ep.load()
                    fn = obj if callable(obj) else getattr(obj, "register", None)
                    if not fn:
                        p.error = "缺少可调用的 register"
                        continue
                    fn(api)
                else:
                    spec = importlib.util.spec_from_file_location(p.name, p.source)
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[p.name] = mod
                    spec.loader.exec_module(mod)
                    fn = getattr(mod, "register", None)
                    if not fn:
                        p.error = "缺少 register(api)"
                        continue
                    fn(api)
                p.loaded = True
            except Exception as e:
                p.error = f"{type(e).__name__}: {e}"

    def plugins(self):
        return list(self._plugins)
