from beam import Beam, PointLoad, AppliedMoment, Support, Reaction, TOLERANCE


def solve_reactions(beam: Beam) -> None:
    """
    Computes support reaction forces using static equilibrium equations
    and directly attaches Reaction events to the corresponding support points in the Beam.
    """
    # 1. Extract support points from the beam object
    support_points = []
    for pt in beam.points:
        for event in pt.events:
            if isinstance(event, Support):
                support_points.append(pt)

    if len(support_points) != 2:
        raise ValueError(f"Expected 2 supports, found {len(support_points)}")

    # Sort supports by position
    support_points.sort(key=lambda p: p.x)
    pt_A, pt_B = support_points[0], support_points[1]

    x_A = pt_A.x
    x_B = pt_B.x
    span = x_B - x_A

    # Defensive check: ensure supports are separated
    if span <= TOLERANCE:
        raise ValueError(f"Support span too small or overlapping supports (span = {span:.2e} m).")

    # 2. Compute moments about support A
    M_applied_about_A = 0.0
    total_applied_force = 0.0

    for pt in beam.points:
        arm = pt.x - x_A
        for event in pt.events:
            if isinstance(event, PointLoad):
                M_applied_about_A += arm * event.force
                total_applied_force += event.force
            elif isinstance(event, AppliedMoment):
                M_applied_about_A += event.moment

    # 3. Apply equilibrium equations
    # ΣM_A = 0 => M_applied_about_A + R_B * span = 0
    R_B = -M_applied_about_A / span

    # ΣFy = 0 => R_A + R_B + total_applied_force = 0
    R_A = -total_applied_force - R_B

    # 4. Equilibrium Check about support B
    M_about_B = -R_A * span
    for pt in beam.points:
        arm_B = pt.x - x_B
        for event in pt.events:
            if isinstance(event, PointLoad):
                M_about_B += arm_B * event.force
            elif isinstance(event, AppliedMoment):
                M_about_B += event.moment

    force_balance = R_A + R_B + total_applied_force

    if abs(force_balance) > TOLERANCE or abs(M_about_B) > TOLERANCE:
        raise RuntimeError(
            f"Equilibrium check failed! Force error: {force_balance:.2e}, Moment error: {M_about_B:.2e}"
        )

    # 5. Attach Reaction events directly via beam.add_event()
    beam.add_event(x_A, Reaction(force=R_A))
    beam.add_event(x_B, Reaction(force=R_B))