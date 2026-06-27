"""CSV 表格查看视图与 provider。"""
import csv

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
)

from npworks_ide.ide.editor_registry import EditorView, EditorProvider


def _read_csv(path):
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                sample = list(csv.reader(f))
            if sample:
                return sample[0], sample[1:]
            return [], []
        except UnicodeDecodeError:
            continue
    return [], []


class CsvView(QWidget, EditorView):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self._path = file_path
        self._all_rows = []
        self._header = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        bar = QWidget()
        bar.setObjectName("csv_toolbar")
        bar.setFixedHeight(32)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(8, 0, 8, 0)
        bl.setSpacing(8)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("过滤行（子串，不区分大小写）...")
        self._filter.setClearButtonEnabled(True)
        self._filter.textChanged.connect(self._apply_filter)
        bl.addWidget(self._filter)

        self._info = QLabel("")
        self._info.setStyleSheet("color: gray;")
        bl.addWidget(self._info)
        bl.addStretch()

        layout.addWidget(bar)

        self._table = QTableWidget()
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._table.verticalHeader().setDefaultSectionSize(22)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table)

        self._load()

    @property
    def file_path(self):
        return self._path

    def _load(self):
        header, rows = _read_csv(self._path)
        self._header = header
        self._all_rows = rows
        ncols = max(len(header), max((len(r) for r in rows), default=0), 1)
        self._table.setColumnCount(ncols)
        if header:
            self._table.setHorizontalHeaderLabels(
                header + [f"Col {i+1}" for i in range(len(header), ncols)]
            )
        else:
            self._table.setHorizontalHeaderLabels([f"Col {i+1}" for i in range(ncols)])
        self._populate(self._all_rows)
        self._info.setText(f"{len(rows)} 行 × {ncols} 列")

    def _populate(self, rows):
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c in range(self._table.columnCount()):
                val = row[c] if c < len(row) else ""
                self._table.setItem(r, c, QTableWidgetItem(val))

    def _apply_filter(self, text):
        text = (text or "").lower()
        if not text:
            self._populate(self._all_rows)
            return
        filtered = [r for r in self._all_rows
                    if any(text in (cell or "").lower() for cell in r)]
        self._populate(filtered)
        self._info.setText(f"{len(filtered)} / {len(self._all_rows)} 行 × {self._table.columnCount()} 列")

    def apply_theme(self, theme_name):
        from npworks_ide.ide.themes.variables import LIGHT_VARS, DARK_VARS
        v = DARK_VARS if theme_name == "dark" else LIGHT_VARS
        self.setStyleSheet(
            f"QWidget#csv_toolbar {{ background: {v['bg_menu']}; border-bottom: 1px solid {v['border']}; }}")
        self._table.setStyleSheet(
            f"QTableWidget {{ background: {v['bg_input']}; color: {v['fg']}; "
            f"gridline-color: {v['border']}; alternate-background-color: {v['hover']}; }}"
            f"QHeaderView::section {{ background: {v['bg_menu']}; color: {v['fg_dim']}; "
            f"padding: 4px; border: none; border-right: 1px solid {v['border']}; }}"
        )
        self._info.setStyleSheet(f"color: {v['fg_dim']};")


class CsvProvider(EditorProvider):
    id = "npworks.csv"
    extensions = (".csv", ".tsv")
    title_prefix = "\U0001F5C2"
    readonly = True

    def create(self, path, parent=None):
        return CsvView(path, parent)
