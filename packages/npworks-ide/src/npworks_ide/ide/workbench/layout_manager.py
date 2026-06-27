"""布局管理器：负责停靠栏位可见性、面板显示/聚焦、栏位图标与外观开关。

从 main_window.py 抽取，与其它控制器风格一致。MainWindow 控件创建完成后
构造本类，所有「栏位 / 分割条 / 面板可见性 / 布局恢复」逻辑集中于此。
"""

_SIDEBAR_WIDTH = 260
_RIGHT_WIDTH = 320
_BOTTOM_HEIGHT = 240

# 固定栏位 -> (所在 splitter 属性名, 在 splitter 中的索引, 默认尺寸)
_ZONE_LAYOUT = {
    "left": ("_h_splitter", 1, _SIDEBAR_WIDTH),
    "right": ("_h_splitter", 3, _RIGHT_WIDTH),
    "bottom": ("_v_splitter", 1, _BOTTOM_HEIGHT),
}


class LayoutManager:
    def __init__(self, main_window):
        self._mw = main_window
        self.dock = main_window.dock
        # _zone_actions 与菜单构建共享同一个 dict 引用（不要复制）
        self._zone_actions = main_window._zone_actions
        self._activity_bar = main_window.activity_bar
        self._settings = main_window._settings

    # --- 控件创建完成后由 MainWindow 调用，集中注册面板 ---
    def register_panels(self, spec):
        """spec: [(panel_id, widget, title, zone, icon_key), ...]"""
        for panel_id, widget, title, zone, icon_key in spec:
            self.dock.register_panel(
                panel_id, widget, title, zone,
                icon=self.icon_for_key(icon_key))

    def _persist(self, key, on):
        self._settings.setValue(key, "1" if on else "0")

    # --- 栏位可见性 ---
    def zone_splitter_index(self, name):
        attr, idx, default = _ZONE_LAYOUT[name]
        return getattr(self._mw, attr), idx, default

    def is_zone_visible(self, name):
        splitter, idx, _ = self.zone_splitter_index(name)
        return splitter.sizes()[idx] > 50

    def set_zone_visible(self, name, on):
        splitter, idx, default = self.zone_splitter_index(name)
        sizes = splitter.sizes()
        if on:
            if sizes[idx] < 50:
                sizes[idx] = default
                splitter.setSizes(sizes)
        else:
            if sizes[idx] > 0:
                sizes[idx] = 0
                splitter.setSizes(sizes)

    def ensure_panel_zone_visible(self, panel_id):
        zone = self.dock.zone_of(panel_id)
        if zone and not self.is_zone_visible(zone):
            self.set_zone_visible(zone, True)
        return zone

    # --- 面板显示/聚焦 ---
    def show_panel(self, panel_id):
        """显示某面板所在的栏位并聚焦该面板。"""
        zone = self.dock.zone_of(panel_id)
        if not zone:
            return
        self.set_zone_visible(zone, True)
        self.dock.focus_panel(panel_id)
        self.sync_zone_actions()

    def show_output_panel(self):
        self.show_panel("output")

    def toggle_bottom_panel(self):
        self.set_zone_visible("bottom", not self.is_zone_visible("bottom"))
        self.sync_zone_actions()

    # --- DockManager 信号槽 ---
    def on_panel_moved(self, panel_id, zone):
        self._settings.setValue(f"dock/panel_{panel_id}", zone)
        self.auto_adjust_zones()

    def auto_adjust_zones(self):
        """空栏位自动收起，被拖入面板的栏位自动展开。"""
        for name, zone in self.dock.zones.items():
            if zone.count() == 0:
                self.set_zone_visible(name, False)
        for panel_id in self.dock.panel_ids():
            zone = self.dock.zone_of(panel_id)
            if zone and not self.is_zone_visible(zone):
                self.set_zone_visible(zone, True)
        self.sync_zone_actions()

    def sync_zone_actions(self):
        """同步视图菜单中三个栏位开关的勾选状态。"""
        for zone, act in self._zone_actions.items():
            act.setChecked(self.is_zone_visible(zone))

    # --- 图标 ---
    def icon_for_key(self, key):
        from npworks_ide.ide.platform import icons
        from npworks_ide.ide.themes.variables import LIGHT_VARS
        if key and key in icons._ICONS:
            return icons.icon(key, LIGHT_VARS["fg"], 16)
        return None

    def refresh_sidebar_icons(self):
        # 栏位标签图标随主题刷新
        from npworks_ide.ide.platform import icons
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        theme = self._mw.theme_ctrl.get_current_theme()
        v = DARK_VARS if theme == "dark" else LIGHT_VARS
        for panel_id, key in self._mw._panel_icon_keys.items():
            if not key:
                continue
            zone_name = self.dock.zone_of(panel_id)
            if not zone_name:
                continue
            zone = self.dock.zones[zone_name]
            idx = zone.index_of(panel_id)
            if idx >= 0:
                zone.setTabIcon(idx, icons.icon(key, v["fg"], 16))

    # --- 激活（面板 ↔ 活动栏） ---
    _ACTIVITY_PANEL = {0: "explorer", 1: "textbook"}

    def activate_panel(self, panel_id):
        """活动栏入口：切换/聚焦某面板所在的栏位。"""
        zone = self.dock.zone_of(panel_id)
        if zone is None:
            return
        same = (self.dock.zones[zone].current_panel_id() == panel_id
                and self.is_zone_visible(zone))
        if same:
            self.set_zone_visible(zone, False)
            self._activity_bar.set_checked(-1)
            self.sync_zone_actions()
            return
        self.set_zone_visible(zone, True)
        self.dock.focus_panel(panel_id)
        idx = next((k for k, v in self._ACTIVITY_PANEL.items()
                    if v == panel_id), None)
        if idx is not None:
            self._activity_bar.set_checked(idx)
        self.sync_zone_actions()

    # 兼容旧调用名
    def activate_view(self, view_id):
        self.activate_panel(view_id)

    def toggle_figures_dock(self):
        zone = self.dock.zone_of("figures")
        if zone is None:
            return
        visible = self.is_zone_visible(zone)
        self.set_zone_visible(zone, not visible)
        if not visible:
            self.dock.focus_panel("figures")
        self._activity_bar.set_checked(2 if not visible else -1)
        self.sync_zone_actions()

    def on_figure_ready(self, path):
        self._mw._figures_view.add_figure(path)
        zone = self.dock.zone_of("figures")
        if zone:
            self.set_zone_visible(zone, True)
            self.dock.focus_panel("figures")
        self._activity_bar.set_checked(3)

    # --- 外观访问器（供设置页 / 菜单使用） ---
    def is_primary_sidebar(self):
        return self.is_zone_visible("left")

    def set_primary_sidebar(self, on):
        self.set_zone_visible("left", on)
        self._persist("appearance/primary", on)
        self.sync_zone_actions()

    def is_figures_dock(self):
        zone = self.dock.zone_of("figures")
        return bool(zone) and self.is_zone_visible(zone)

    def set_figures_dock(self, on):
        zone = self.dock.zone_of("figures")
        if zone:
            self.set_zone_visible(zone, on)
        self._persist("appearance/figures", on)
        self.sync_zone_actions()

    def is_secondary_sidebar(self):
        return self.is_zone_visible("right")

    def set_secondary_sidebar(self, on):
        self.set_zone_visible("right", on)
        self._persist("appearance/secondary", on)
        self.sync_zone_actions()

    def is_panel(self):
        return self.is_zone_visible("bottom")

    def set_panel(self, on):
        self.set_zone_visible("bottom", on)
        self._persist("appearance/panel", on)
        self.sync_zone_actions()

    def is_view_visible(self, view_id):
        return self.dock.zone_of(view_id) is not None

    def set_view_visible(self, view_id, on):
        hidden = self._mw._hidden_panels
        if on:
            info = hidden.pop(view_id, None)
            if info is None:
                return
            self.dock.register_panel(
                view_id, info["widget"], info["title"], info["zone"],
                icon=info.get("icon"))
            self.set_zone_visible(info["zone"], True)
        else:
            zone = self.dock.zone_of(view_id)
            if zone is None:
                return
            info = self.dock.detach_panel(view_id)
            if info:
                hidden[view_id] = info
                if self.dock.zones[zone].count() == 0:
                    self.set_zone_visible(zone, False)
        self._persist(f"appearance/view_{view_id}", on)

    # --- 恢复 ---
    def restore_appearance(self):
        """仅恢复面板停靠栏位、组件显隐与栏位展开/收起。"""
        s = self._settings
        all_panels = self._mw._all_panels
        # 恢复面板停靠栏位
        for panel_id in all_panels:
            saved_zone = s.value(f"dock/panel_{panel_id}")
            if saved_zone in self.dock.zones:
                self.dock.move_panel(panel_id, saved_zone)
        # 恢复组件显隐
        for vid in all_panels:
            if s.value(f"appearance/view_{vid}", "1") != "1":
                self.set_view_visible(vid, False)
        # 恢复栏位展开/收起
        self.set_primary_sidebar(s.value("appearance/primary", "1") == "1")
        self.set_secondary_sidebar(
            s.value("appearance/secondary",
                    s.value("appearance/figures", "0")) == "1")
        self.set_panel(s.value("appearance/panel", "1") == "1")
        self.sync_zone_actions()

    def restore_splitter_sizes(self):
        """原 _restore_layout：恢复分割条尺寸。"""
        h_sizes = self._settings.value("dock/h_sizes")
        if h_sizes and len(h_sizes) == 4:
            self._mw._h_splitter.setSizes([int(x) for x in h_sizes])
        v_sizes = self._settings.value("dock/v_sizes")
        if v_sizes and len(v_sizes) == 2:
            self._mw._v_splitter.setSizes([int(x) for x in v_sizes])
