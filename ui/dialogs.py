"""
Dialog windows for the Beam Analysis Solver.

HistoryDialog is a presentation layer only: it reads already-loaded
history entries (the same data returned by history.load_history()) and,
on selection, hands the chosen execution number back to the caller via a
callback. It never talks to history.json directly, so the existing
history storage/loading mechanism in history.py is untouched.
"""

from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton
)

from ui.styles import PALETTE


class HistoryDialog(QDialog):
    """Browsable card list over saved analyses."""

    def __init__(self, history_entries, on_load, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis History")
        self.resize(440, 500)
        self._on_load = on_load
        self._selected_execution = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("SAVED EXECUTIONS")
        title.setProperty("role", "section")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(False)
        layout.addWidget(self.list_widget, 1)

        if not history_entries:
            placeholder = QListWidgetItem("No saved executions yet. Run an analysis to populate history.")
            placeholder.setFlags(Qt.NoItemFlags)
            self.list_widget.addItem(placeholder)
        else:
            for entry in reversed(history_entries):  # most recent first
                self._add_entry(entry)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghostButton")
        close_btn.clicked.connect(self.reject)
        self.load_btn = QPushButton("Load Analysis")
        self.load_btn.setObjectName("primaryButton")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self._load_clicked)
        btn_row.addWidget(close_btn)
        btn_row.addWidget(self.load_btn)
        layout.addLayout(btn_row)

        self.list_widget.currentItemChanged.connect(self._selection_changed)
        self.list_widget.itemDoubleClicked.connect(lambda _item: self._load_clicked())

    def _add_entry(self, entry):
        execution = entry.get("execution")
        timestamp = entry.get("timestamp", "")
        beam = entry.get("beam", {}) or {}
        analysis = entry.get("analysis", {}) or {}
        length = beam.get("length")
        system_type = analysis.get("system_type", "")
        stats = analysis.get("summary_statistics", {}) or {}

        system_label = "Cantilever" if system_type == "cantilever" else "Simply Supported"
        try:
            ts_label = datetime.fromisoformat(timestamp).strftime("%d %b %Y, %H:%M")
        except (ValueError, TypeError):
            ts_label = timestamp or "--"

        length_label = f"L = {length:.2f} m" if isinstance(length, (int, float)) else ""
        max_m = stats.get("max_bending_moment")
        result_label = f"Max M = {max_m:.2f} kNm" if isinstance(max_m, (int, float)) else ""

        exec_label = f"#{execution:03d}" if isinstance(execution, int) else "#---"
        text = f"{exec_label}    {ts_label}\n{system_label}   \u2022   {length_label}   \u2022   {result_label}"

        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, execution)
        self.list_widget.addItem(item)

    def _selection_changed(self, current, _previous):
        has_selection = current is not None and current.data(Qt.UserRole) is not None
        self.load_btn.setEnabled(has_selection)
        self._selected_execution = current.data(Qt.UserRole) if has_selection else None

    def _load_clicked(self):
        if self._selected_execution is not None:
            self._on_load(self._selected_execution)
            self.accept()


class AboutDialog(QDialog):
    """Small, restrained About dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Beam Analysis Solver")
        self.setFixedSize(380, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(4)

        name = QLabel("Beam Analysis Solver")
        name.setStyleSheet(f"font-size: 14pt; font-weight: 600; color: {PALETTE['text_primary']};")
        layout.addWidget(name)

        version = QLabel("Version 3.0")
        version.setProperty("role", "hint")
        layout.addWidget(version)
        layout.addSpacing(12)

        desc = QLabel("Static Beam Analysis\nShear Force & Bending Moment Diagram Solver")
        desc.setProperty("role", "fieldLabel")
        layout.addWidget(desc)
        layout.addSpacing(12)

        stack = QLabel("Built with Python \u00b7 PyQt5 \u00b7 Matplotlib \u00b7 NumPy")
        stack.setProperty("role", "hint")
        layout.addWidget(stack)

        layout.addStretch()

        convention = QLabel(
            "Sign convention:  \u2193 loads negative   \u2022   \u2191 loads positive   \u2022   CCW moments positive"
        )
        convention.setProperty("role", "hint")
        convention.setWordWrap(True)
        layout.addWidget(convention)
        layout.addSpacing(14)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("primaryButton")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
