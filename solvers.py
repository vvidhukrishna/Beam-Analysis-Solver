from beam import Beam, PointLoad, Reaction, AppliedMoment, Support, TOLERANCE
from Validation import validate_equilibrium


def solve_reactions(beam: Beam) -> None:
    """Computes support reactions using static equilibrium equations."""
    supports = beam.support_points()
    if len(supports) != 2:
        raise ValueError(f"Expected exactly 2 supports, found {len(supports)}")

    supports.sort(key=lambda p: p.x)
    pt_A, pt_B = supports[0], supports[1]
    x_A, x_B = pt_A.x, pt_B.x
    span = x_B - x_A

    if span <= TOLERANCE:
        raise ValueError(f"Support span too small or overlapping supports (span = {span:.2e} m).")

    # Sum moments about support A: ΣM_A = 0
    M_applied_about_A = sum((x - x_A) * load.force for x, load in beam.point_loads())
    M_applied_about_A += sum(moment.moment for _, moment in beam.applied_moments())

    # Calculate reaction forces
    R_B = -M_applied_about_A / span
    total_force = sum(load.force for _, load in beam.point_loads())
    R_A = -total_force - R_B

    # Validate equilibrium math
    validate_equilibrium(beam, R_A, R_B, x_A, x_B)

    # Attach reactions to beam
    beam.add_event(x_A, Reaction(force=R_A))
    beam.add_event(x_B, Reaction(force=R_B))


def calculate_sfd(beam: Beam) -> list[tuple[float, float]]:
    """Calculates Shear Force Diagram (SFD) coordinates."""
    sfd_data: list[tuple[float, float]] = []
    current_shear = 0.0

    for pt in beam.points:
        sfd_data.append((pt.x, current_shear))

        for event in pt.events:
            if isinstance(event, (PointLoad, Reaction)):
                current_shear += event.force

        sfd_data.append((pt.x, current_shear))

    return sfd_data


def calculate_bmd(beam: Beam) -> list[tuple[float, float]]:
    """Calculates Bending Moment Diagram (BMD) coordinates."""
    if not beam.points:
        return []

    bmd_data: list[tuple[float, float]] = []
    current_moment = 0.0
    current_shear = 0.0
    current_x = beam.points[0].x

    for pt in beam.points:
        dx = pt.x - current_x
        current_moment += current_shear * dx
        bmd_data.append((pt.x, current_moment))

        has_applied_moment = False
        for event in pt.events:
            if isinstance(event, AppliedMoment):
                current_moment -= event.moment
                has_applied_moment = True

        if has_applied_moment:
            bmd_data.append((pt.x, current_moment))

        for event in pt.events:
            if isinstance(event, (PointLoad, Reaction)):
                current_shear += event.force

        current_x = pt.x

    return bmd_data