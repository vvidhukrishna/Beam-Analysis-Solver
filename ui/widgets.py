from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QToolButton, QTableWidget, QHeaderView, QAbstractItemView, QDoubleSpinBox, QSizePolicy)
from ui import icons
from ui.styles import PALETTE

ROW_HEIGHT = 30
HEADER_HEIGHT = 26


# Layout helpers
def card(title: str = None, hint: str = None):
    """A QFrame styled as a property-panel 'card' section. Returns (frame, content_layout)."""
    frame = QFrame()
    frame.setObjectName("card")
    outer = QVBoxLayout(frame)
    outer.setContentsMargins(12, 10, 12, 12)
    outer.setSpacing(8)

    if title:
        head = QHBoxLayout()
        head.setSpacing(6)
        title_lbl = QLabel(title.upper())
        title_lbl.setProperty("role", "section")
        head.addWidget(title_lbl)
        head.addStretch()
        outer.addLayout(head)

    if hint:
        hint_lbl = QLabel(hint)
        hint_lbl.setProperty("role", "hint")
        hint_lbl.setWordWrap(True)
        outer.addWidget(hint_lbl)

    content = QVBoxLayout()
    content.setSpacing(8)
    outer.addLayout(content)
    return frame, content


def field_row(label_text: str, widget: QWidget, label_width: int = 128) -> QWidget:
    """A horizontal [label][widget] row with consistent label alignment."""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    lbl = QLabel(label_text)
    lbl.setProperty("role", "fieldLabel")
    lbl.setFixedWidth(label_width)
    layout.addWidget(lbl)
    layout.addWidget(widget, 1)
    return row


def labeled_spinbox(label_text: str, unit: str, value: float, minimum: float = 0.0,
    maximum: float = 100000.0, decimals: int = 2, step: float = 0.5, label_width: int = 128) -> tuple:
    """Builds a [label][QDoubleSpinBox with unit suffix] row. Returns (row_widget, spinbox)."""
    spin = QDoubleSpinBox()
    spin.setDecimals(decimals)
    spin.setRange(minimum, maximum)
    spin.setSingleStep(step)
    spin.setSuffix(f" {unit}" if unit else "")
    spin.setValue(value)
    spin.setAlignment(Qt.AlignRight)
    return field_row(label_text, spin, label_width), spin


# Structured load table
class LoadTable(QWidget):
    """
    A compact, structured editor for a list of numeric load rows
    (point loads, moments, UDLs, UVLs), replacing the legacy
    comma-separated free-text pattern with real numeric, unit-aware
    controls.
    """
    rows_changed = pyqtSignal()

    def __init__(self, columns, add_label="+ Add Row", empty_text="No entries defined.", parent=None):
        super().__init__(parent)
        self.columns = columns
        self._empty_text = empty_text

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        self.table = QTableWidget(0, len(columns) + 1)
        headers = [f"{c['label']} ({c['unit']})" if c.get("unit") else c["label"] for c in columns]
        headers.append("")
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        header = self.table.horizontalHeader()
        for i in range(len(columns)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(len(columns), QHeaderView.Fixed)
        self.table.setColumnWidth(len(columns), 28)
        header.setFixedHeight(HEADER_HEIGHT)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.empty_label = QLabel(empty_text)
        self.empty_label.setProperty("role", "hint")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setFixedHeight(30)

        add_btn = QPushButton(add_label)
        add_btn.setObjectName("addRowButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(lambda: self.add_row())

        outer.addWidget(self.table)
        outer.addWidget(self.empty_label)
        outer.addWidget(add_btn)

        self._sync_height()

    def add_row(self, values=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, ROW_HEIGHT)

        for col, spec in enumerate(self.columns):
            spin = QDoubleSpinBox()
            spin.setDecimals(spec.get("decimals", 2))
            spin.setRange(spec.get("minimum", -1_000_000.0), spec.get("maximum", 1_000_000.0))
            spin.setSingleStep(spec.get("step", 0.5))
            if spec.get("unit"):
                spin.setSuffix(f" {spec['unit']}")
            spin.setAlignment(Qt.AlignRight)
            spin.setFrame(False)
            spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
            default = spec.get("default", 0.0)
            spin.setValue(values[col] if values is not None else default)
            self.table.setCellWidget(row, col, spin)

        remove_container = QWidget()
        h = QHBoxLayout(remove_container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setAlignment(Qt.AlignCenter)
        remove_btn = QToolButton()
        remove_btn.setObjectName("removeRowButton")
        remove_btn.setIcon(icons.icon("remove", color=PALETTE["text_tertiary"], size=12))
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setToolTip("Remove this row")
        remove_btn.clicked.connect(self._make_remove_handler(remove_container))
        h.addWidget(remove_btn)
        self.table.setCellWidget(row, len(self.columns), remove_container)
        self._sync_height()
        self.rows_changed.emit()

    def _make_remove_handler(self, container_widget):
        def handler():
            for row in range(self.table.rowCount()):
                if self.table.cellWidget(row, len(self.columns)) is container_widget:
                    self.table.removeRow(row)
                    break
            self._sync_height()
            self.rows_changed.emit()
        return handler

    def get_rows(self):
        """Return a list of tuples, one per row, of the raw float values (column order preserved)."""
        rows = []
        for row in range(self.table.rowCount()):
            values = tuple(self.table.cellWidget(row, col).value() for col in range(len(self.columns)))
            rows.append(values)
        return rows

    def row_count(self) -> int:
        return self.table.rowCount()

    def clear_rows(self):
        self.table.setRowCount(0)
        self._sync_height()
        self.rows_changed.emit()

    def _sync_height(self):
        n = self.table.rowCount()
        self.table.setVisible(n > 0)
        self.empty_label.setVisible(n == 0)
        if n > 0:
            self.table.setFixedHeight(HEADER_HEIGHT + n * ROW_HEIGHT + 4)