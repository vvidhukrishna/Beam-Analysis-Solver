import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from beam import (Beam, Support, PointLoad, AppliedMoment, UniformDistributedLoad, UniformVaryingLoad)
import history

@pytest.fixture
def mock_history_file(tmp_path, monkeypatch):
    test_file = tmp_path / "test_history.json"
    monkeypatch.setattr(history, "history_file", str(test_file))
    return test_file


@pytest.fixture
def sample_beam():
    beam = Beam(10.0)
    beam.add_event(0, Support("pinned"))
    beam.add_event(10, Support("roller"))
    beam.add_event(5, PointLoad(-15))
    beam.add_event(8, AppliedMoment(20))
    beam.add_distributed_event(UniformDistributedLoad(0, 5, -5))
    beam.add_distributed_event(UniformVaryingLoad(5, 10, -5, 0))
    return beam


@pytest.fixture
def sample_analysis_data():
    x_grid = np.linspace(0, 10, 100)
    v_grid = np.sin(x_grid)
    m_grid = np.cos(x_grid)
    reactions = {"type": "simply_supported", "R_A": 10.0, "R_B": 15.0, "x_A": 0, "x_B": 10}
    stats = {
        "max_shear_force": 1.0,
        "min_shear_force": -1.0,
        "max_bending_moment": 1.0,
        "min_bending_moment": -1.0}
    return reactions, x_grid, v_grid, m_grid, stats


def test_save_and_load_history(mock_history_file, sample_beam, sample_analysis_data):
    reactions, x_grid, v_grid, m_grid, stats = sample_analysis_data

    # Save first execution
    history.save_analysis_history(sample_beam, "simply_supported", reactions, x_grid, v_grid, m_grid, stats)

    # Save second execution
    history.save_analysis_history(sample_beam, "simply_supported", reactions, x_grid, v_grid, m_grid, stats)

    loaded = history.load_history()

    assert len(loaded) == 2
    assert loaded[0]["execution"] == 1
    assert loaded[1]["execution"] == 2
    assert loaded[0]["beam"]["length"] == 10.0
    assert len(loaded[0]["beam"]["distributed_loads"]) == 2


def test_load_history_failures(mock_history_file):
    # Missing file
    assert history.load_history() == []

    # Invalid JSON
    mock_history_file.write_text("invalid json {")
    assert history.load_history() == []


def test_load_execution(mock_history_file, sample_beam, sample_analysis_data):
    reactions, x_grid, v_grid, m_grid, stats = sample_analysis_data
    history.save_analysis_history(sample_beam, "simply_supported", reactions, x_grid, v_grid, m_grid, stats)

    entry = history.load_execution(1)
    assert entry is not None
    assert entry["execution"] == 1

    entry_none = history.load_execution(99)
    assert entry_none is None


def test_reconstruct_beam(mock_history_file, sample_beam, sample_analysis_data):
    reactions, x_grid, v_grid, m_grid, stats = sample_analysis_data
    history.save_analysis_history(sample_beam, "simply_supported", reactions, x_grid, v_grid, m_grid, stats)

    entry = history.load_execution(1)
    reconstructed = history.reconstruct_beam(entry)

    assert reconstructed.length == sample_beam.length
    assert len(list(reconstructed.supports())) == 2
    assert len(list(reconstructed.point_loads())) == 1
    assert len(list(reconstructed.applied_moments())) == 1
    assert len(list(reconstructed.udls())) == 1
    assert len(list(reconstructed.uvls())) == 1


def test_load_analysis_data(mock_history_file, sample_beam, sample_analysis_data):
    reactions, x_grid, v_grid, m_grid, stats = sample_analysis_data
    history.save_analysis_history(sample_beam, "simply_supported", reactions, x_grid, v_grid, m_grid, stats)

    entry = history.load_execution(1)
    x_loaded, v_loaded, m_loaded = history.load_analysis_data(entry)

    assert isinstance(x_loaded, np.ndarray)
    np.testing.assert_array_almost_equal(x_grid, x_loaded)
    np.testing.assert_array_almost_equal(v_grid, v_loaded)
    np.testing.assert_array_almost_equal(m_grid, m_loaded)


@patch("history.plot_beam_results")
def test_plot_history_entry(mock_plot, mock_history_file, sample_beam, sample_analysis_data):
    reactions, x_grid, v_grid, m_grid, stats = sample_analysis_data
    history.save_analysis_history(sample_beam, "simply_supported", reactions, x_grid, v_grid, m_grid, stats)

    entry = history.load_execution(1)
    dummy_fig = MagicMock()

    beam, rxns = history.plot_history_entry(entry, dummy_fig)

    assert rxns == reactions
    mock_plot.assert_called_once()


def test_save_graph():
    mock_fig = MagicMock()
    history.save_graph(mock_fig, "test_output.png")
    mock_fig.savefig.assert_called_once_with("test_output.png", bbox_inches="tight")