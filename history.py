import json
from datetime import datetime


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
    """
    Save one successful beam analysis to the history file.
    """

    # Load existing history if the file exists
    try:
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)

        if not isinstance(history, list):
            history = []

    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    # Determine execution number
    execution_number = len(history) + 1

    # Build the history record
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

    # Add UDLs
    for udl in beam.udls():
        history_entry["beam"]["distributed_loads"].append({
            "type": "udl",
            "start_x": udl.start_x,
            "end_x": udl.end_x,
            "intensity": udl.intensity,
            "centroid_x": udl.centroid_x,
            "resultant_force": udl.resultant_force
        })

    # Add UVLs
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

    # Add the new execution to history
    history.append(history_entry)

    # Write the updated history back to the file
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)
