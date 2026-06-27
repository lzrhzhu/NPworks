"""可拖拽停靠系统：固定的左/右/底三个栏位（DockZone），组件可在栏位间拖拽。

栏位本身的位置是结构固定的（由主窗口的 QSplitter 决定，不可拖动），
但挂在栏位中的"组件"（面板）可以通过拖拽标签在不同栏位之间移动，
也可以在同一栏位内重新排序。
"""
from PyQt5.QtCore import Qt, QObject, QMimeData, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QDrag
from PyQt5.QtWidgets import QTabWidget, QTabBar

_MIME_TYPE = "application/x-npworks-dock-panel"
_DRAG_THRESHOLD = 6


class DockTabBar(QTabBar):
    """支持跨栏位拖拽的标签栏。"""

    def __init__(self, zone):
        super().__init__()
        self._zone = zone
        self.setAcceptDrops(True)
        self._press_pos = None
        self._press_index = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            idx = self.tabAt(event.pos())
            if idx >= 0:
                self._press_pos = QPoint(event.pos())
                self._press_index = idx
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._press_pos is not None and self._press_index >= 0:
            moved = (event.pos() - self._press_pos).manhattanLength()
            if moved > _DRAG_THRESHOLD:
                idx = self._press_index
                self._press_pos = None
                self._press_index = -1
                self._start_drag(idx)
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._press_pos = None
        self._press_index = -1
        super().mouseReleaseEvent(event)

    def _start_drag(self, index):
        panel_id = self._zone.panel_id_at(index)
        if not panel_id:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(_MIME_TYPE, panel_id.encode("utf-8"))
        mime.setText(panel_id)
        drag.setMimeData(mime)
        pix = QPixmap(120, 22)
        pix.fill(Qt.transparent)
        drag.setPixmap(pix)
        drag.setHotSpot(QPoint(10, 11))
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat(_MIME_TYPE):
            panel_id = bytes(event.mimeData().data(_MIME_TYPE)).decode("utf-8")
            insert_index = self.tabAt(event.pos())
            self._zone.manager.move_panel(panel_id, self._zone.name, insert_index)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class DockZone(QTabWidget):
    """一个固定的停靠栏位，以标签页形式承载多个面板。"""

    def __init__(self, name, manager, parent=None):
        super().__init__(parent)
        self.name = name
        self.manager = manager
        self.setObjectName("dock_zone")
        self.setTabBar(DockTabBar(self))
        self.setTabsClosable(False)
        self.setMovable(False)
        self.setAcceptDrops(True)
        self.setMinimumWidth(0)
        self.setMinimumHeight(0)

    def add_panel(self, panel):
        index = self.addTab(panel["widget"], panel.get("title", ""))
        self._configure_tab(index, panel)
        return index

    def insert_panel(self, index, panel):
        if index < 0 or index > self.count():
            index = self.count()
        index = self.insertTab(index, panel["widget"], panel.get("title", ""))
        self._configure_tab(index, panel)
        return index

    def _configure_tab(self, index, panel):
        self.tabBar().setTabData(index, panel["id"])
        icon = panel.get("icon")
        if icon is not None and not icon.isNull():
            self.setTabIcon(index, icon)

    def remove_panel(self, panel_id):
        for i in range(self.count()):
            if self.tabBar().tabData(i) == panel_id:
                widget = self.widget(i)
                self.removeTab(i)
                return widget
        return None

    def panel_id_at(self, index):
        if index < 0 or index >= self.count():
            return None
        return self.tabBar().tabData(index)

    def index_of(self, panel_id):
        for i in range(self.count()):
            if self.tabBar().tabData(i) == panel_id:
                return i
        return -1

    def current_panel_id(self):
        return self.panel_id_at(self.currentIndex())

    def has_panel(self, panel_id):
        return self.index_of(panel_id) >= 0

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat(_MIME_TYPE):
            panel_id = bytes(event.mimeData().data(_MIME_TYPE)).decode("utf-8")
            self.manager.move_panel(panel_id, self.name, -1)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class DockManager(QObject):
    """管理所有栏位与面板，处理面板在栏位间的移动。"""

    panel_moved = pyqtSignal(str, str)   # panel_id, target_zone

    def __init__(self, parent=None):
        super().__init__(parent)
        self.zones = {}        # name -> DockZone
        self.panels = {}       # id -> {"widget","title","icon","zone"}

    def add_zone(self, name, zone):
        zone.name = name
        zone.manager = self
        self.zones[name] = zone

    def register_panel(self, panel_id, widget, title, zone, icon=None):
        if panel_id in self.panels:
            return
        if zone not in self.zones:
            zone = next(iter(self.zones))
        panel = {"id": panel_id, "widget": widget, "title": title,
                 "icon": icon, "zone": zone}
        self.panels[panel_id] = panel
        self.zones[zone].add_panel(panel)

    def detach_panel(self, panel_id):
        """从栏位移除面板（但保留组件），返回面板描述。"""
        panel = self.panels.pop(panel_id, None)
        if panel is None:
            return None
        self.zones[panel["zone"]].remove_panel(panel_id)
        return panel

    def move_panel(self, panel_id, target_zone, index=-1):
        panel = self.panels.get(panel_id)
        if panel is None or target_zone not in self.zones:
            return
        source = panel["zone"]
        if source == target_zone:
            target = self.zones[target_zone]
            cur = target.index_of(panel_id)
            if cur < 0 or (index == cur or (index < 0 and cur == target.count() - 1)):
                return
            self.zones[source].remove_panel(panel_id)
            if index < 0:
                target.add_panel(panel)
            else:
                target.insert_panel(index, panel)
        else:
            self.zones[source].remove_panel(panel_id)
            target = self.zones[target_zone]
            if index < 0:
                target.add_panel(panel)
            else:
                target.insert_panel(index, panel)
            panel["zone"] = target_zone
        self.zones[target_zone].setCurrentWidget(panel["widget"])
        self.panel_moved.emit(panel_id, target_zone)

    def zone_of(self, panel_id):
        panel = self.panels.get(panel_id)
        return panel["zone"] if panel else None

    def focus_panel(self, panel_id):
        panel = self.panels.get(panel_id)
        if panel is None:
            return False
        self.zones[panel["zone"]].setCurrentWidget(panel["widget"])
        return True

    def panel_ids(self):
        return list(self.panels.keys())

    def assignments(self):
        return {pid: p["zone"] for pid, p in self.panels.items()}
