import os
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QFileDialog, QMenu, QAction,
)

try:
    import yaml
except ImportError:
    yaml = None

_ROLE_PATH = 1000
_ROLE_IS_DIR = 1001
_ROLE_LOADED = 1002
_ROLE_IS_ROOT = 1003
_ROLE_IS_TEXTBOOK = 1004


def _sort_key(name: str):
    n = name.lower()
    is_dot = n.startswith(".")
    try:
        parts = name.rsplit(".", 1)
        num = int(parts[0]) if parts[0].isdigit() else float("inf")
    except (ValueError, IndexError):
        num = float("inf")
    return (is_dot, num, n)


class _RootItem(QTreeWidgetItem):
    def __init__(self, parent, path: str, label: str, is_textbook: bool = False):
        super().__init__(parent, [label])
        self.setData(0, _ROLE_PATH, path)
        self.setData(0, _ROLE_IS_DIR, True)
        self.setData(0, _ROLE_LOADED, False)
        self.setData(0, _ROLE_IS_ROOT, True)
        self.setData(0, _ROLE_IS_TEXTBOOK, is_textbook)
        font = self.font(0)
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(0, font)
        dummy = QTreeWidgetItem(self, [""])
        dummy.setData(0, _ROLE_LOADED, False)


class _DirItem(QTreeWidgetItem):
    def __init__(self, parent, path: str, label: str):
        super().__init__(parent, [label])
        self.setData(0, _ROLE_PATH, path)
        self.setData(0, _ROLE_IS_DIR, True)
        self.setData(0, _ROLE_LOADED, False)
        dummy = QTreeWidgetItem(self, [""])
        dummy.setData(0, _ROLE_LOADED, False)


class _FileItem(QTreeWidgetItem):
    def __init__(self, parent, path: str, label: str):
        super().__init__(parent, [label])
        self.setData(0, _ROLE_PATH, path)
        self.setData(0, _ROLE_IS_DIR, False)
        self.setData(0, _ROLE_LOADED, True)


class FileTree(QWidget):
    file_selected = pyqtSignal(str)
    open_folder_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._roots = []
        self._textbook_dir = None
        self._textbook_meta = {}
        self._watched_dirs = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tree = QTreeWidget(self)
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setAnimated(True)
        self._tree.setExpandsOnDoubleClick(True)
        self._tree.setRootIsDecorated(False)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.itemExpanded.connect(self._on_item_expanded)
        self._tree.itemCollapsed.connect(self._on_item_collapsed)
        self._tree.itemClicked.connect(self._on_item_clicked)

        header = self._tree.header()
        header.setMinimumSectionSize(200)

        layout.addWidget(self._tree)

        toolbar = QWidget()
        toolbar.setObjectName("file_tree_toolbar")
        toolbar.setFixedHeight(28)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(4, 0, 4, 0)
        tb_layout.setSpacing(2)

        self._btn_open = QPushButton("打开文件夹")
        self._btn_open.setObjectName("file_tree_btn")
        self._btn_open.setCursor(Qt.PointingHandCursor)
        self._btn_open.clicked.connect(self._on_open_folder_btn)
        tb_layout.addWidget(self._btn_open)

        self._btn_collapse = QPushButton("全部折叠")
        self._btn_collapse.setObjectName("file_tree_btn")
        self._btn_collapse.setCursor(Qt.PointingHandCursor)
        self._btn_collapse.clicked.connect(self._collapse_all)
        tb_layout.addWidget(self._btn_collapse)

        tb_layout.addStretch()
        layout.addWidget(toolbar)

    def init_textbook(self):
        try:
            import npworks_content
            content_dir = Path(npworks_content.__file__).parent / "content"
            if not content_dir.exists():
                return
            self._textbook_dir = str(content_dir)
            self._load_textbook_meta()
            self.add_root(self._textbook_dir, "NPWORKS 教材", is_textbook=True)
        except Exception:
            pass

    def _load_textbook_meta(self):
        if not self._textbook_dir or not yaml:
            return
        self._textbook_meta = {}
        content = Path(self._textbook_dir)
        for ch_dir in sorted(content.iterdir()):
            if ch_dir.is_dir() and ch_dir.name.startswith("ch"):
                meta_path = ch_dir / "meta.yaml"
                if meta_path.exists():
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta = yaml.safe_load(f)
                        sections = {}
                        for sec in meta.get("sections", []):
                            sections[sec["file"]] = sec["title"]
                        self._textbook_meta[ch_dir.name] = {
                            "title": meta.get("title", ch_dir.name),
                            "sections": sections,
                        }
                    except Exception:
                        pass

    def _textbook_section_title(self, path: str) -> str:
        if not self._textbook_dir:
            return None
        try:
            rel = os.path.relpath(path, self._textbook_dir)
            parts = rel.replace("\\", "/").split("/")
            if len(parts) == 2:
                ch_id, filename = parts
                ch_meta = self._textbook_meta.get(ch_id)
                if ch_meta:
                    return ch_meta["sections"].get(filename)
        except (ValueError, KeyError):
            pass
        return None

    def _textbook_chapter_title(self, dirname: str) -> str:
        ch_meta = self._textbook_meta.get(dirname)
        if ch_meta:
            return ch_meta["title"]
        return None

    def add_root(self, path: str, label: str = None, is_textbook: bool = False):
        path = os.path.normpath(path)
        for r in self._roots:
            if os.path.normpath(r) == path:
                return
        if label is None:
            label = os.path.basename(path)
        item = _RootItem(self._tree, path, label, is_textbook)
        self._roots.append(path)
        return item

    def close_root(self, path: str):
        path = os.path.normpath(path)
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if os.path.normpath(item.data(0, _ROLE_PATH) or "") == path:
                self._tree.takeTopLevelItem(i)
                self._roots.remove(path)
                return

    def close_selected_root(self):
        item = self._tree.currentItem()
        if not item:
            return
        root = self._find_root(item)
        if root:
            path = root.data(0, _ROLE_PATH)
            if path == self._textbook_dir:
                return
            self.close_root(path)

    def get_open_folders(self):
        return list(self._roots)

    def root_count(self):
        return len(self._roots)

    def expand_first_root(self):
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if item.data(0, _ROLE_IS_TEXTBOOK):
                item.setExpanded(True)
                break

    def clear_tree_selection(self):
        self._tree.clearSelection()

    def _find_root(self, item: QTreeWidgetItem) -> QTreeWidgetItem:
        while item.parent() is not None:
            item = item.parent()
        return item

    def _is_dir_item(self, item: QTreeWidgetItem) -> bool:
        return bool(item.data(0, _ROLE_IS_DIR))

    def _is_loaded(self, item: QTreeWidgetItem) -> bool:
        return bool(item.data(0, _ROLE_LOADED))

    def _get_path(self, item: QTreeWidgetItem) -> str:
        return item.data(0, _ROLE_PATH) or ""

    def _populate_dir(self, item: QTreeWidgetItem):
        if self._is_loaded(item):
            return
        path = self._get_path(item)
        if not path or not os.path.isdir(path):
            return

        if item.childCount() == 1:
            dummy = item.child(0)
            if not dummy.data(0, _ROLE_PATH):
                item.removeChild(dummy)

        is_textbook_root = bool(item.data(0, _ROLE_IS_TEXTBOOK))
        parent_is_textbook_root = False
        parent_is_textbook_ch = False
        if item.parent():
            root = self._find_root(item)
            if root and root.data(0, _ROLE_IS_TEXTBOOK):
                if item.parent() is root:
                    parent_is_textbook_root = True
                else:
                    parent_is_textbook_ch = True

        try:
            entries = sorted(os.listdir(path), key=_sort_key)
        except PermissionError:
            return

        for entry in entries:
            if entry.startswith(".") and entry not in (".", ".."):
                continue
            full = os.path.join(path, entry)
            is_dir = os.path.isdir(full)

            if is_dir:
                if is_textbook_root or parent_is_textbook_root:
                    title = self._textbook_chapter_title(entry)
                    name = title if title else entry
                else:
                    name = entry
                child = _DirItem(item, full, f"\u25B8 {name}")
            else:
                if parent_is_textbook_root or parent_is_textbook_ch:
                    sec_title = self._textbook_section_title(full)
                    name = sec_title if sec_title else entry
                else:
                    name = entry
                child = _FileItem(item, full, name)

        item.setData(0, _ROLE_LOADED, True)

    def _on_item_expanded(self, item: QTreeWidgetItem):
        if self._is_dir_item(item) and not self._is_loaded(item):
            self._populate_dir(item)
        text = item.text(0)
        if text.startswith("\u25B8"):
            item.setText(0, "\u25BE" + text[1:])

    def _on_item_collapsed(self, item: QTreeWidgetItem):
        text = item.text(0)
        if text.startswith("\u25BE"):
            item.setText(0, "\u25B8" + text[1:])

    def _on_item_clicked(self, item: QTreeWidgetItem, _col: int):
        path = self._get_path(item)
        if path and os.path.isfile(path):
            self.file_selected.emit(path)
        elif self._is_dir_item(item):
            item.setExpanded(not item.isExpanded())

    def _on_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        path = self._get_path(item)
        is_root = bool(item.data(0, _ROLE_IS_ROOT))
        is_textbook = bool(item.data(0, _ROLE_IS_TEXTBOOK))

        if path and os.path.isfile(path):
            action = menu.addAction("打开")
            action.triggered.connect(lambda: self.file_selected.emit(path))

        if is_root and not is_textbook:
            action = menu.addAction("关闭文件夹")
            action.triggered.connect(lambda: self.close_root(path))

        if is_root:
            action = menu.addAction("在资源管理器中打开")
            action.triggered.connect(lambda: os.startfile(path) if os.path.isdir(path) else None)

        if path and os.path.isdir(path) and not is_root:
            action = menu.addAction("新建 Python 文件")
            action.triggered.connect(lambda: self._new_file_in(path))

            action = menu.addAction("新建文件夹")
            action.triggered.connect(lambda: self._new_folder_in(path))

        if menu.actions():
            menu.exec_(self._tree.viewport().mapToGlobal(pos))

    def _new_file_in(self, dir_path: str):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建 Python 文件", "文件名:", text="new_file.py")
        if ok and name:
            full = os.path.join(dir_path, name)
            if not os.path.exists(full):
                with open(full, "w", encoding="utf-8") as f:
                    f.write("")
                self._refresh_dir(dir_path)

    def _new_folder_in(self, dir_path: str):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建文件夹", "文件夹名:")
        if ok and name:
            full = os.path.join(dir_path, name)
            os.makedirs(full, exist_ok=True)
            self._refresh_dir(dir_path)

    def _refresh_dir(self, dir_path: str):
        for i in range(self._tree.topLevelItemCount()):
            root = self._tree.topLevelItem(i)
            self._refresh_item(root, dir_path)

    def _refresh_item(self, item: QTreeWidgetItem, target_path: str):
        if self._get_path(item) == target_path and self._is_loaded(item):
            item.setData(0, _ROLE_LOADED, False)
            while item.childCount():
                item.removeChild(item.child(0))
            self._populate_dir(item)
            return
        for i in range(item.childCount()):
            self._refresh_item(item.child(i), target_path)

    def refresh_current(self):
        item = self._tree.currentItem()
        if not item:
            return
        target = item
        if not self._is_dir_item(item):
            target = item.parent()
        if target:
            path = self._get_path(target)
            if path:
                target.setData(0, _ROLE_LOADED, False)
                while target.childCount():
                    target.removeChild(target.child(0))
                self._populate_dir(target)

    def _on_open_folder_btn(self):
        self.open_folder_requested.emit()

    def _collapse_all(self):
        for i in range(self._tree.topLevelItemCount()):
            root = self._tree.topLevelItem(i)
            for j in range(root.childCount()):
                root.child(j).setExpanded(False)
            root.setExpanded(False)

    def select_file(self, file_path: str):
        file_path = os.path.normpath(file_path)
        self._tree.blockSignals(True)
        for i in range(self._tree.topLevelItemCount()):
            if self._select_in(self._tree.topLevelItem(i), file_path):
                break
        self._tree.blockSignals(False)

    def _select_in(self, item: QTreeWidgetItem, target: str) -> bool:
        path = self._get_path(item)
        if not path:
            return False
        norm = os.path.normpath(path)
        if norm == target and os.path.isfile(norm):
            self._tree.setCurrentItem(item)
            self._tree.scrollToItem(item)
            return True
        if os.path.isdir(norm) and self._is_dir_item(item):
            if not target.startswith(norm):
                return False
            if not self._is_loaded(item):
                self._populate_dir(item)
            item.setExpanded(True)
            for j in range(item.childCount()):
                if self._select_in(item.child(j), target):
                    return True
        return False

    def cleanup(self):
        pass
