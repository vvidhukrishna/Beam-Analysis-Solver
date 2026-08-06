import numpy as np
from beam import Beam, Reaction, PointLoad, AppliedMoment, Support, UniformDistributedLoad, TOLERANCE


def solve_reactions(beam: Beam) -> tuple[float, float, float, float]:
    """
    Solves reaction forces R_A and R_B for simply supported beam with 2 supports.
    Includes Point Loads, Applied Moments, and UDLs.
    Returns: (x_A, R_A, x_B, R_B)
    """
    beam.clear_reactions()
    
    supports = list(beam.supports())
    if len(supports) != 2:
        raise ValueError(f"Solver requires exactly 2 supports, found {len(supports)}.")

    (x_A, _), (x_B, _) = supports[0], supports[1]
    span = x_B - x_A

    if abs(span) < TOLERANCE:
        raise ValueError("Support separation distance cannot be zero.")

    # 1. Total applied vertical forces
    F_point_total = sum(load.force for _, load in beam.point_loads())
    F_udl_total = sum(udl.resultant_force for udl in beam.udls())
    F_applied_total = F_point_total + F_udl_total

    # 2. Sum of moments about Support A (\sum M_A = 0)
    # Applied point moments
    M_applied = sum(m.moment for _, m in beam.applied_moments())

    # Moments from point loads: F * (x - x_A)
    M_point_loads = sum(load.force * (x - x_A) for x, load in beam.point_loads())

    # Moments from UDLs: F_equiv * (x_centroid - x_A)
    M_udl_loads = sum(udl.resultant_force * (udl.centroid_x - x_A) for udl in beam.udls())

    M_total_about_A = M_applied + M_point_loads + M_udl_loads

    # Equilibrium equations:
    #   \sum M_A = 0 => R_B * (x_B - x_A) + M_total_about_A = 0
    #   \sum F_y = 0 => R_A + R_B + F_applied_total = 0
    R_B = -M_total_about_A / span
    R_A = -(F_applied_total + R_B)

    # Attach reaction events to beam model
    beam.add_event(x_A, Reaction(force=R_A))
    beam.add_event(x_B, Reaction(force=R_B))

    return x_A, R_A, x_B, R_B


def calculate_sfd_bmd(beam: Beam, num_samples: int = 1000) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculates Shear Force (V) and Bending Moment (M) along beam using dense integration.
    Handles step discontinuities from point forces/moments and quadratic curves from UDLs.
    Returns: (x_array, shear_force_array, bending_moment_array)
    """
    # Build evaluation x-grid including epsilons around discrete points to capture sharp jumps
    critical_x = {p.x for p in beam.points}
    for dev in beam.distributed_events:
        critical_x.add(dev.start_x)
        critical_x.add(dev.end_x)

    extra_pts = []
    for cx in critical_x:
        if cx > 0:
            extra_pts.append(cx - 1e-7)
        if cx < beam.length:
            extra_pts.append(cx + 1e-7)

    base_grid = np.linspace(0, beam.length, num_samples)
    x_all = np.unique(np.sort(np.concatenate([base_grid, list(critical_x), extra_pts])))

    shear_force = np.zeros_like(x_all)
    bending_moment = np.zeros_like(x_all)

    # Collect all point forces (Point loads + Support Reactions)
    point_forces: list[tuple[float, float]] = []
    for x, load in beam.point_loads():
        point_forces.append((x, load.force))
    for p in beam.points:
        for ev in p.events:
            if isinstance(ev, Reaction):
                point_forces.append((p.x, ev.force))

    applied_moments = [(x, m.moment) for x, m in beam.applied_moments()]
    udls = list(beam.udls())

    for idx, x in enumerate(x_all):
        # 1. Shear Force V(x) = Sum of all vertical forces to the left of section x
        V_pt = sum(f for px, f in point_forces if px <= x)

        V_udl = 0.0
        for udl in udls:
            if x <= udl.start_x:
                continue
            elif x >= udl.end_x:
                V_udl += udl.resultant_force
            else:
                # Partially active UDL region
                active_len = x - udl.start_x
                V_udl += udl.intensity * active_len

        shear_force[idx] = V_pt + V_udl

        # 2. Bending Moment M(x) = Sum of moments of forces & moments to the left of x
        M_pt_forces = sum(f * (x - px) for px, f in point_forces if px <= x)
        M_pt_moments = sum(m for px, m in applied_moments if px <= x)

        M_udl = 0.0
        for udl in udls:
            if x <= udl.start_x:
                continue
            elif x >= udl.end_x:
                M_udl += udl.resultant_force * (x - udl.centroid_x)
            else:
                active_len = x - udl.start_x
                active_force = udl.intensity * active_len
                active_centroid = udl.start_x + (active_len / 2.0)
                M_udl += active_force * (x - active_centroid)

        bending_moment[idx] = M_pt_forces + M_pt_moments + M_udl

    return x_all, shear_force, bending_moment