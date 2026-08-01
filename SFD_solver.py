from beam import Beam, PointLoad, Reaction


def calculate_sfd(beam: Beam) -> list[tuple[float, float]]:
    """
    Calculates the Shear Force Diagram (SFD) values along the beam.
    Positive shear follows the beam sign convention.

    Returns:
        A list of (x_coordinate, shear_force) tuples.
        Points with concentrated forces will appear twice to capture vertical steps.
    """
    sfd_data: list[tuple[float, float]] = []
    current_shear_force = 0.0

    for pt in beam.points:
        sfd_data.append((pt.x, current_shear_force))

        for event in pt.events:
            if isinstance(event, (PointLoad, Reaction)):
                current_shear_force += event.force

        sfd_data.append((pt.x, current_shear_force))

    return sfd_data