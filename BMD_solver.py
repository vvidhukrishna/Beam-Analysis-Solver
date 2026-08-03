from beam import Beam, PointLoad, Reaction, AppliedMoment

def calculate_bmd(beam: Beam) -> list[tuple[float, float]]:
    """
    Calculates the Bending Moment Diagram (BMD) values along the beam.

    Returns:
        A list of (x_coordinate, bending_moment) tuples.
        Points with applied moments will appear twice to capture vertical steps.
    """
    bmd_data: list[tuple[float, float]] = []
    current_moment = 0.0
    current_shear = 0.0

    if not beam.points:
        return []
    current_x = beam.points[0].x

    for pt in beam.points:
        dx = pt.x - current_x
        current_moment += current_shear * dx
        bmd_data.append((pt.x, current_moment))

        has_applied_moment = False
        for event in pt.events:
            if isinstance(event, AppliedMoment):
                # Applied moments produce an instantaneous jump in the BMD.
                # Positive counter-clockwise applied moments reduce the internal bending
                # moment according to this project's sign convention.
                current_moment -= event.moment
                has_applied_moment = True

        if has_applied_moment:
            bmd_data.append((pt.x, current_moment))

        for event in pt.events:
            if isinstance(event, (PointLoad, Reaction)):
                current_shear += event.force
        current_x = pt.x
    return bmd_data