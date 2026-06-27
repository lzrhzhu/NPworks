"""VS Code 风格侧边栏容器。

视图（文件浏览器、大纲、搜索等）作为 SideView 挂载到 SideBarPanel，
可在主侧边栏与次侧边栏之间移动、切换，而非固定位置。
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame,
    QToolButton,
)


class SideView:
    """挂载到侧边栏的一个视图描述。"""

    def __init__(self, view_id, title, icon_key, widget, actions=None):
        self.view_id = view_id
        self.title = title
        self.icon_key = icon_key
        self.widget = widget
        self.actions = list(actions or [])   # 标题栏右侧的动作按钮


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)


class SideBarPanel(QWidget):
    """侧边栏宿主：标题栏 + 堆叠的视图。side 为 'primary' 或 'secondary'。"""

    view_switched = pyqtSignal(str)

    def __init__(self, side="primary", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar_panel")
        self._side = side
        self._views = {}        # view_id -> SideView
        self._order = []
        self._current = None
        self._on_move = None
        self._move_icon = QIcon()
        self.setMinimumWidth(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("sidebar_title")
        header.setFixedHeight(30)
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 0, 4, 0)
        h.setSpacing(4)

        self._title = QLabel("")
        self._title.setObjectName("dock_title_label")
        f = self._title.font()
        f.setBold(True)
        f.setPointSize(10)
        self._title.setFont(f)
        h.addWidget(self._title)
        h.addStretch()

        self._actions_box = QWidget()
        self._actions_layout = QHBoxLayout(self._actions_box)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(2)
        h.addWidget(self._actions_box)

        self._move_btn = QToolButton()
        self._move_btn.setObjectName("file_tree_btn")
        self._move_btn.setCursor(Qt.PointingHandCursor)
        self._move_btn.setToolTip("移动到另一侧侧边栏")
        self._move_btn.clicked.connect(self._emit_move)
        h.addWidget(self._move_btn)

        layout.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setObjectName("sidebar_separator")
        layout.addWidget(sep)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

    @property
    def side(self):
        return self._side

    def set_move_callback(self, cb):
        self._on_move = cb

    def set_move_icon(self, icon):
        self._move_icon = icon
        self._move_btn.setIcon(icon)

    def set_move_visible(self, visible):
        self._move_btn.setVisible(visible)

    def _emit_move(self):
        if self._current and self._on_move:
            self._on_move(self._current)

    def add_view(self, view: SideView):
        if view.view_id in self._views:
            return
        self._views[view.view_id] = view
        self._order.append(view.view_id)
        self._stack.addWidget(view.widget)
        if self._current is None:
            self.show_view(view.view_id)

    def remove_view(self, view_id):
        view = self._views.pop(view_id, None)
        if view is None:
            return None
        if view_id in self._order:
            self._order.remove(view_id)
        self._stack.removeWidget(view.widget)
        if self._current == view_id:
            self._current = None
            if self._order:
                self.show_view(self._order[0])
        return view

    def has_view(self, view_id):
        return view_id in self._views

    def view_ids(self):
        return list(self._order)

    def current_view_id(self):
        return self._current

    def show_view(self, view_id):
        view = self._views.get(view_id)
        if view is None:
            return
        self._stack.setCurrentWidget(view.widget)
        self._current = view_id
        self._title.setText(view.title)
        self._refresh_actions(view)
        self.view_switched.emit(view_id)

    def _refresh_actions(self, view):
        _clear_layout(self._actions_layout)
        for act in view.actions:
            self._actions_layout.addWidget(act)
        self._actions_box.setVisible(bool(view.actions))

    def apply_theme(self, theme_name, vars_):
        for vid in self._order:
            v = self._views[vid]
            if hasattr(v.widget, "apply_theme"):
                try:
                    v.widget.apply_theme(theme_name)
                except TypeError:
                    pass
