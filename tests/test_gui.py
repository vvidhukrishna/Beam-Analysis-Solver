import pytest
import numpy as np
from unittest.mock import patch
from PyQt5.QtCore import Qt
from gui import BeamAnalysisApp

@pytest.fixture
def app(qtbot):
    """Fixture to set up the GUI for testing."""
    test_app = BeamAnalysisApp()
    qtbot.addWidget(test_app)
    test_app.show()
    qtbot.waitExposed(test_app)
    return test_app

def test_initial_state(app):
    """Test the default state of the GUI."""
    assert app.windowTitle() == "Beam Analysis Tool"
    assert app.radio_simply.isChecked() is True
    assert app.supp_a_input.isVisible() is True
    assert app.supp_b_input.isVisible() is True
    assert app.beam_length_input.value() == 10.0


def test_toggle_beam_type(app, qtbot):
    """Test switching between Simply Supported and Cantilever."""
    # Switch to cantilever
    qtbot.mouseClick(app.radio_cantilever, Qt.LeftButton)
    assert app.radio_cantilever.isChecked() is True
    assert app.supp_a_input.isVisible() is False
    assert app.supp_b_input.isVisible() is False

    # Switch back to simply supported
    qtbot.mouseClick(app.radio_simply, Qt.LeftButton)
    assert app.supp_a_input.isVisible() is True
    assert app.supp_b_input.isVisible() is True


def test_calculate_invalid_input(app, qtbot):
    app.supp_a_input.setValue(9.0)
    app.supp_b_input.setValue(5.0)
    qtbot.mouseClick(app.calc_btn, Qt.LeftButton)

    assert "Error" in app.result_box.toPlainText()


@patch("gui.save_analysis_history")
@patch("gui.plot_beam_results")
@patch("gui.solve_reactions")
@patch("gui.calculate_sfd_bmd")
def test_calculate_saves_history(mock_calc, mock_solve, mock_plot, mock_save_history, app, qtbot):
    """Test that a successful calculation triggers saving to history and plotting."""
    mock_solve.return_value = {"type": "simply_supported", "R_A": 10, "R_B": 10, "x_A": 0, "x_B": 10}
    mock_calc.return_value = (np.array([0, 10]), np.array([5, -5]), np.array([0, 25]))

    qtbot.mouseClick(app.calc_btn, Qt.LeftButton)

    mock_solve.assert_called_once()
    mock_calc.assert_called_once()
    mock_save_history.assert_called_once()
    mock_plot.assert_called_once()

    output_text = app.result_box.toPlainText()
    assert "Analysis Successful" in output_text
    assert "Saved to history.json" in output_text


@patch("gui.load_history")
def test_refresh_history(mock_load_history, app):
    """Test that the history dropdown populates correctly."""
    mock_load_history.return_value = [
        {"execution": 1, "timestamp": "2026-09-03T10:00:00"},
        {"execution": 2, "timestamp": "2026-09-03T10:05:00"}
    ]

    app.refresh_history()

    assert app.history_combo.count() == 2
    assert app.history_combo.itemData(0) == 1
    assert app.history_combo.itemData(1) == 2


@patch("gui.load_execution")
@patch("gui.plot_history_entry")
def test_load_selected_history_valid(mock_plot, mock_load_execution, app):
    """Test loading a valid history entry."""
    app.history_combo.addItem("Test Exec", 1)
    app.history_combo.setCurrentIndex(0)

    mock_entry = {
        "analysis": {
            "summary_statistics": {
                "max_shear_force": 15.0,
                "min_shear_force": -10.0,
                "max_bending_moment": 25.0,
                "min_bending_moment": 0.0
            }
        }
    }
    mock_load_execution.return_value = mock_entry

    app.load_selected_history()

    mock_load_execution.assert_called_once_with(1)
    mock_plot.assert_called_once_with(mock_entry, app.figure)

    output_text = app.result_box.toPlainText()
    assert "Loaded Execution: 1" in output_text
    assert "Max Shear Force: 15.00 kN" in output_text
    assert "Max Bending Moment: 25.00 kNm" in output_text


@patch("gui.QMessageBox.warning")
def test_load_selected_history_none(mock_warning, app):
    """Test behavior when user tries to load history with no selection."""
    app.history_combo.clear()

    app.load_selected_history()

    mock_warning.assert_called_once()


@patch("gui.QFileDialog.getSaveFileName")
@patch("gui.save_graph")
@patch("gui.QMessageBox.information")
def test_save_current_graph(mock_info, mock_save, mock_file_dialog, app):
    """Test the graph saving functionality."""
    # Simulate user choosing a file name
    mock_file_dialog.return_value = ("test_graph.png", "")

    app.save_current_graph()

    mock_save.assert_called_once_with(app.figure, "test_graph.png")
    mock_info.assert_called_once()


@patch("gui.QFileDialog.getSaveFileName")
@patch("gui.save_graph")
def test_save_current_graph_cancel(mock_save, mock_file_dialog, app):
    """Test that cancelling the save graph dialog does not throw errors or save."""
    mock_file_dialog.return_value = ("", "")

    app.save_current_graph()

    mock_save.assert_not_called()