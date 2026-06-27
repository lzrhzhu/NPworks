"""命令注册表：插件可贡献命令（id + 回调 + 标题），供命令面板/快捷键调用。"""


class CommandRegistry:
    def __init__(self):
        self._cmds = {}   # id -> (callback, title)

    def register(self, command_id, callback, title=None):
        self._cmds[command_id] = (callback, title)

    def unregister(self, command_id):
        self._cmds.pop(command_id, None)

    def get(self, command_id):
        entry = self._cmds.get(command_id)
        return entry[0] if entry else None

    def run(self, command_id, *args, **kwargs):
        cb = self.get(command_id)
        if cb:
            return cb(*args, **kwargs)
        return None

    def items(self):
        return [(cid, title) for cid, (_cb, title) in self._cmds.items() if title]
