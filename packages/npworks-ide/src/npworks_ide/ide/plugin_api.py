"""插件 API：插件通过 register(api) 拿到此对象，贡献各种能力。

对应 VS Code 的贡献点：
  register_editor        -> customEditors
  register_view          -> views / viewsContainers
  register_activity      -> viewsContainers（活动栏入口）
  register_command       -> commands
  register_settings      -> configuration（设置页分区）
"""


class PluginAPI:
    def __init__(self, main_window):
        self._mw = main_window

    def main_window(self):
        return self._mw

    def register_editor(self, provider):
        """注册自定义编辑器提供者（EditorProvider）。"""
        from npworks_ide.ide.editor_registry import registry
        registry.register(provider)

    def register_view(self, view, side="primary"):
        """把一个 SideView 挂载到主/次侧边栏。"""
        panel = self._mw._primary if side == "primary" else self._mw._secondary
        panel.add_view(view)

    def register_activity(self, icon_key, tooltip, view_id=None,
                          on_activate=None, bottom=False):
        """在活动栏添加按钮。view_id 给定则点击切换该视图；on_activate 为额外回调。"""
        idx = self._mw.activity_bar.add_button(icon_key, tooltip, bottom=bottom)

        def handler():
            if view_id:
                self._mw._activate_view(view_id)
            if on_activate:
                on_activate()

        self._mw._activity_handlers[idx] = handler
        self._mw.activity_bar.apply_theme_icons(self._mw.theme_ctrl.get_current_theme())
        return idx

    def register_command(self, command_id, callback, title=None):
        self._mw.command_registry.register(command_id, callback, title)

    def register_settings_factory(self, title, factory):
        """注册设置页的一个分区（factory: (QVBoxLayout, theme) -> None）。"""
        self._mw.setting_sections.append((title, factory))
