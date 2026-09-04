import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolButton

from ui.widgets import LoadTable

POINT_LOAD_COLUMNS = [
    {"label": "Location", "unit": "m", "decimals": 2, "minimum": 0.0, "maximum": 100.0, "default": 0.0},
    {"label": "Magnitude", "unit": "kN", "decimals": 2, "minimum": -1000.0, "maximum": 1000.0, "default": -10.0},
]


@pytest.fixture
def table(qtbot):
    widget = LoadTable(
        POINT_LOAD_COLUMNS,
        add_label="+ Add Point Load",
        empty_text="No point loads defined."
    )
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    return widget


def test_load_table_starts_empty(table):
    """A fresh table has no rows and shows its empty state."""
    assert table.row_count() == 0
    assert table.get_rows() == []
    assert table.empty_label.isVisible() is True
    assert table.table.isVisible() is False


def test_load_table_add_row_uses_column_defaults(table):
    table.add_row()
    assert table.row_count() == 1
    assert table.get_rows() == [(0.0, -10.0)]
    assert table.empty_label.isVisible() is False
    assert table.table.isVisible() is True


def test_load_table_add_row_with_explicit_values(table):
    table.add_row((3.5, -25.0))
    assert table.get_rows() == [(3.5, -25.0)]


def test_load_table_multiple_rows_preserve_order(table):
    table.add_row((1.0, -5.0))
    table.add_row((2.0, 15.0))
    assert table.row_count() == 2
    assert table.get_rows() == [(1.0, -5.0), (2.0, 15.0)]


def test_load_table_clear_rows(table):
    table.add_row((1.0, -5.0))
    table.add_row((2.0, 15.0))
    table.clear_rows()
    assert table.row_count() == 0
    assert table.get_rows() == []
    assert table.empty_label.isVisible() is True


def test_load_table_remove_row_via_button(table, qtbot):
    """Clicking a row's remove (x) button deletes only that row."""
    table.add_row((1.0, -5.0))
    table.add_row((2.0, 15.0))

    remove_container = table.table.cellWidget(0, len(table.columns))
    remove_btn = remove_container.findChild(QToolButton)
    qtbot.mouseClick(remove_btn, Qt.LeftButton)

    assert table.row_count() == 1
    assert table.get_rows() == [(2.0, 15.0)]


def test_load_table_rows_changed_signal(table):
    """rows_changed fires on add, remove and clear so callers can react."""
    events = []
    table.rows_changed.connect(lambda: events.append(1))

    table.add_row()
    table.add_row()
    table.clear_rows()

    assert len(events) == 3
