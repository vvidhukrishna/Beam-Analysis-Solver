import json
from datetime import datetime
import numpy as np
from plotting import plot_beam_results
from beam import (
    Beam, Support, PointLoad, AppliedMoment,
    UniformDistributedLoad, UniformVaryingLoad
)

HISTORY_FILE = "history.json"


def save_analysis_history(
    beam,
    system_type,
    reactions,
    x_grid,
    shear_force,
    bending_moment,
    summary_statistics,
):
    """Save a completed beam analysis to the history file."""
    try:
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)

        if not isinstance(history, list):
            history = []

    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    execution_number = len(history) + 1

    history_entry = {
        "execution": execution_number,
        "timestamp": datetime.now().isoformat(timespec="seconds"),

        "beam": {
            "length": beam.length,

            "supports": [
                {
                    "x": x,
                    "type": support.support_type
                }
                for x, support in beam.supports()
            ],

            "point_loads": [
                {
                    "x": x,
                    "force": load.force
                }
                for x, load in beam.point_loads()
            ],

            "applied_moments": [
                {
                    "x": x,
                    "moment": moment.moment
                }
                for x, moment in beam.applied_moments()
            ],

            "distributed_loads": []
        },

        "analysis": {
            "system_type": system_type,

            "reactions": reactions,

            "summary_statistics": summary_statistics,

            "analysis_data": {
                "x_coords": x_grid.tolist(),
                "shear_force": shear_force.tolist(),
                "bending_moment": bending_moment.tolist()
            }
        }
    }

    for udl in beam.udls():
        history_entry["beam"]["distributed_loads"].append({
            "type": "udl",
            "start_x": udl.start_x,
            "end_x": udl.end_x,
            "intensity": udl.intensity,
            "centroid_x": udl.centroid_x,
            "resultant_force": udl.resultant_force
        })

    for uvl in beam.uvls():
        history_entry["beam"]["distributed_loads"].append({
            "type": "uvl",
            "start_x": uvl.start_x,
            "end_x": uvl.end_x,
            "w1": uvl.w1,
            "w2": uvl.w2,
            "centroid_x": uvl.centroid_x,
            "resultant_force": uvl.resultant_force
        })

    history.append(history_entry)

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def load_history():
    """Load all saved beam analyses from the history file."""
    try:
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)
            return history if isinstance(history, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_execution(execution_number: int):
    """Return a saved analysis by execution number."""
    history = load_history()
    for entry in history:
        if entry.get("execution") == execution_number:
            return entry
    return None

def reconstruct_beam(entry):
    """Reconstruct a Beam object from a saved history entry."""
    beam_data = entry["beam"]

    beam = Beam(beam_data["length"])

    for supp in beam_data.get("supports", []):
        beam.add_event(supp["x"], Support(supp["type"]))

    for pt in beam_data.get("point_loads", []):
        beam.add_event(pt["x"], PointLoad(pt["force"]))

    for mom in beam_data.get("applied_moments", []):
        beam.add_event(mom["x"], AppliedMoment(mom["moment"]))

    for dist in beam_data.get("distributed_loads", []):
        if dist["type"] == "udl":
            udl = UniformDistributedLoad(
                dist["start_x"],
                dist["end_x"],
                dist["intensity"]
            )
            beam.add_distributed_event(udl)

        elif dist["type"] == "uvl":
            uvl = UniformVaryingLoad(
                dist["start_x"],
                dist["end_x"],
                dist["w1"],
                dist["w2"]
            )
            beam.add_distributed_event(uvl)

    return beam

def load_analysis_data(entry):
    """Load stored SFD/BMD analysis data from a history entry."""
    data = entry["analysis"]["analysis_data"]

    x_grid = np.array(data["x_coords"])
    V_grid = np.array(data["shear_force"])
    M_grid = np.array(data["bending_moment"])

    return x_grid, V_grid, M_grid

def plot_history_entry(entry, figure):
    """Plot a previously saved beam analysis without rerunning the solver."""
    beam = reconstruct_beam(entry)
    x_grid, V_grid, M_grid = load_analysis_data(entry)
    reactions = entry["analysis"]["reactions"]

    plot_beam_results(beam, x_grid, V_grid, M_grid, figure, reactions)

    return beam, reactions

def save_graph(figure, filename):
    """Save a Matplotlib figure to the specified file."""
    figure.savefig(filename, bbox_inches="tight")