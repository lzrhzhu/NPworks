import os
import shutil
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, Qt, QFileSystemWatcher
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QFileDialog, QMenu, QAction,
    QMessageBox, QInputDialog, QApplication,
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


class _DragTreeWidget(QTreeWidget):
    file_moved = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self._drag_path = None

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            path = item.data(0, _ROLE_PATH)
            is_root = item.data(0, _ROLE_IS_ROOT)
            if path and not is_root:
                self._drag_path = path
        super().startDrag(supportedActions)

    def dropEvent(self, event):
        if not self._drag_path:
            event.ignore()
            return

        pos = event.pos()
        target_item = self.itemAt(pos)
        if not target_item:
            self._drag_path = None
            event.ignore()
            return

        target_path = target_item.data(0, _ROLE_PATH) or ""
        if os.path.isfile(target_path):
            target_path = os.path.dirname(target_path)

        if not target_path or not os.path.isdir(target_path):
            self._drag_path = None
            event.ignore()
            return

        source_name = os.path.basename(self._drag_path)
        new_path = os.path.join(target_path, source_name)

        norm_source = os.path.normpath(self._drag_path)
        norm_new = os.path.normpath(new_path)

        if (norm_new == norm_source
                or os.path.exists(norm_new)
                or norm_new.startswith(norm_source + os.sep)):
            self._drag_path = None
            event.ignore()
            return

        try:
            shutil.move(self._drag_path, new_path)
            self.file_moved.emit(self._drag_path, new_path)
        except Exception:
            pass

        self._drag_path = None
        event.ignore()


class FileTree(QWidget):
    file_selected = pyqtSignal(str)
    open_folder_requested = pyqtSignal()
    file_renamed = pyqtSignal(str, str)
    file_deleted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._roots = []
        self._textbook_dir = None
        self._textbook_meta = {}
        self._watched_dirs = set()
        self._show_hidden = False
        self._clipboard_path = None
        self._clipboard_is_cut = False

        self._fs_watcher = QFileSystemWatcher(self)
        self._fs_watcher.directoryChanged.connect(self._on_fs_dir_changed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tree = _DragTreeWidget(self)
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
        self._tree.file_moved.connect(self._on_file_moved)

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

        self._btn_refresh = QPushButton("刷新")
        self._btn_refresh.setObjectName("file_tree_btn")
        self._btn_refresh.setCursor(Qt.PointingHandCursor)
        self._btn_refresh.clicked.connect(self.refresh_current)
        tb_layout.addWidget(self._btn_refresh)

        tb_layout.addStretch()

        self._btn_hidden = QPushButton(".*")
        self._btn_hidden.setObjectName("file_tree_btn")
        self._btn_hidden.setCursor(Qt.PointingHandCursor)
        self._btn_hidden.setFixedWidth(32)
        self._btn_hidden.setToolTip("显示/隐藏 dotfiles")
        self._btn_hidden.clicked.connect(self._toggle_hidden)
        tb_layout.addWidget(self._btn_hidden)

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
        self._watch_directory(path)
        return item

    def close_root(self, path: str):
        path = os.path.normpath(path)
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if os.path.normpath(item.data(0, _ROLE_PATH) or "") == path:
                self._tree.takeTopLevelItem(i)
                self._roots.remove(path)
                self._unwatch_directory(path)
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

    def _is_textbook_child(self, item: QTreeWidgetItem) -> bool:
        root = self._find_root(item)
        return bool(root and root.data(0, _ROLE_IS_TEXTBOOK))

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
            if not self._show_hidden and entry.startswith(".") and entry not in (".", ".."):
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
                self._watch_directory(full)
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

    def _watch_directory(self, path: str):
        path = os.path.normpath(path)
        if path not in self._watched_dirs and os.path.isdir(path):
            self._watched_dirs.add(path)
            self._fs_watcher.addPath(path)

    def _unwatch_directory(self, path: str):
        path = os.path.normpath(path)
        if path in self._watched_dirs:
            self._watched_dirs.discard(path)
            self._fs_watcher.removePath(path)

    def _on_fs_dir_changed(self, dir_path: str):
        dir_path = os.path.normpath(dir_path)
        self._refresh_dir(dir_path)

    def _on_item_clicked(self, item: QTreeWidgetItem, _col: int):
        path = self._get_path(item)
        if path and os.path.isfile(path):
            self.file_selected.emit(path)
        elif self._is_dir_item(item):
            item.setExpanded(not item.isExpanded())

    def _copy_path(self, path: str):
        self._clipboard_path = path
        self._clipboard_is_cut = False

    def _cut_path(self, path: str):
        self._clipboard_path = path
        self._clipboard_is_cut = True

    def _paste_into(self, dir_path: str):
        if not self._clipboard_path or not os.path.exists(self._clipboard_path):
            self._clipboard_path = None
            return
        src = self._clipboard_path
        name = os.path.basename(src)
        dst = os.path.join(dir_path, name)
        if os.path.normpath(dst) == os.path.normpath(src):
            return
        if os.path.exists(dst):
            QMessageBox.warning(self, "粘贴失败", f"'{name}' 已存在")
            return
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            if self._clipboard_is_cut:
                if os.path.isdir(src):
                    shutil.rmtree(src)
                else:
                    os.remove(src)
                self.file_deleted.emit(src)
                self._clipboard_path = None
                self._clipboard_is_cut = False
            self._refresh_dir(dir_path)
        except Exception as e:
            QMessageBox.warning(self, "粘贴失败", str(e))

    def _on_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        path = self._get_path(item)
        is_root = bool(item.data(0, _ROLE_IS_ROOT))
        is_textbook = bool(item.data(0, _ROLE_IS_TEXTBOOK))
        is_tb_child = self._is_textbook_child(item)

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

        if not is_root and not is_tb_child and path:
            menu.addSeparator()
            action = menu.addAction("重命名")
            action.triggered.connect(lambda checked, it=item: self._rename_item(it))
            action = menu.addAction("删除")
            action.triggered.connect(lambda checked, it=item: self._delete_item(it))
            menu.addSeparator()
            action = menu.addAction("复制")
            action.triggered.connect(lambda checked, p=path: self._copy_path(p))
            action = menu.addAction("剪切")
            action.triggered.connect(lambda checked, p=path: self._cut_path(p))

        if not is_root and os.path.isdir(path) and not is_tb_child:
            if self._clipboard_path is not None:
                action = menu.addAction("粘贴")
                action.triggered.connect(lambda checked, d=path: self._paste_into(d))

        if menu.actions():
            menu.exec_(self._tree.viewport().mapToGlobal(pos))

    def _new_file_in(self, dir_path: str):
        name, ok = QInputDialog.getText(self, "新建 Python 文件", "文件名:", text="new_file.py")
        if ok and name:
            full = os.path.join(dir_path, name)
            if not os.path.exists(full):
                with open(full, "w", encoding="utf-8") as f:
                    f.write("")
                self._refresh_dir(dir_path)

    def _new_folder_in(self, dir_path: str):
        name, ok = QInputDialog.getText(self, "新建文件夹", "文件夹名:")
        if ok and name:
            full = os.path.join(dir_path, name)
            os.makedirs(full, exist_ok=True)
            self._refresh_dir(dir_path)

    def _rename_item(self, item: QTreeWidgetItem):
        path = self._get_path(item)
        if not path:
            return
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "重命名", "新名称:", text=old_name)
        if not ok or not new_name or new_name == old_name:
            return
        new_path = os.path.join(os.path.dirname(path), new_name)
        if os.path.exists(new_path):
            QMessageBox.warning(self, "重命名失败", f"'{new_name}' 已存在")
            return
        try:
            os.rename(path, new_path)
            self.file_renamed.emit(path, new_path)
            self._refresh_dir(os.path.dirname(path))
        except Exception as e:
            QMessageBox.warning(self, "重命名失败", str(e))

    def _delete_item(self, item: QTreeWidgetItem):
        path = self._get_path(item)
        if not path:
            return
        name = os.path.basename(path)
        if self._is_dir_item(item):
            msg = f"确定要删除文件夹 '{name}' 及其所有内容吗？"
        else:
            msg = f"确定要删除文件 '{name}' 吗？"
        reply = QMessageBox.question(
            self, "确认删除", msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            if self._is_dir_item(item):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.file_deleted.emit(path)
            self._refresh_dir(os.path.dirname(path))
        except Exception as e:
            QMessageBox.warning(self, "删除失败", str(e))

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

    def _toggle_hidden(self):
        self._show_hidden = not self._show_hidden
        self._btn_hidden.setText("●.*" if self._show_hidden else ".*")
        self._refresh_all()

    def _refresh_all(self):
        for i in range(self._tree.topLevelItemCount()):
            self._reload_subtree(self._tree.topLevelItem(i))

    def _reload_subtree(self, item: QTreeWidgetItem):
        if self._is_loaded(item) and self._is_dir_item(item):
            was_expanded = item.isExpanded()
            item.setData(0, _ROLE_LOADED, False)
            children = [item.child(c) for c in range(item.childCount())]
            for ch in children:
                item.removeChild(ch)
            self._populate_dir(item)
            item.setExpanded(was_expanded)
            if was_expanded:
                for c in range(item.childCount()):
                    self._reload_subtree(item.child(c))

    def _on_file_moved(self, old_path: str, new_path: str):
        parent_old = os.path.dirname(old_path)
        parent_new = os.path.dirname(new_path)
        self._refresh_dir(parent_old)
        if parent_new != parent_old:
            self._refresh_dir(parent_new)
        self.file_renamed.emit(old_path, new_path)

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
        for d in list(self._watched_dirs):
            self._fs_watcher.removePath(d)
        self._watched_dirs.clear()
