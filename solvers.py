import numpy as np
from beam import Beam, Reaction, ReactionMoment, TOLERANCE, FIXED


def solve_reactions(beam: Beam) -> dict:
    beam.clear_reactions()

    supports = list(beam.supports())
    if len(supports) not in (1, 2):
        raise ValueError(
            f"Solver requires 1 support (Cantilever) or 2 supports (Simply Supported). Found {len(supports)}.")

    # Fetch ALL generic loads dynamically via equivalent forces
    equiv_loads = list(beam.equivalent_loads())
    F_applied_total = sum(force for _, force in equiv_loads)
    M_applied = sum(m.moment for _, m in beam.applied_moments())

    # ---------------- CANTILEVER (1 Support) ----------------
    if len(supports) == 1:
        (x_A, sup) = supports[0]
        if sup.support_type != FIXED:
            raise ValueError(f"A single support must be of type FIXED. Found '{sup.support_type}'.")

        # STRICT x=0 CHECK
        if x_A != 0.0:
            raise ValueError(f"Cantilever fixed support must be at x = 0.0m. Found x = {x_A}m.")
        
        # Sum of moments about Fixed Support A
        M_loads = sum(force * (x - x_A) for x, force in equiv_loads)
        M_total_about_A = M_applied + M_loads

        # Equilibrium equations
        R_A = -F_applied_total
        M_A = -M_total_about_A

        beam.add_event(x_A, Reaction(force=R_A))
        beam.add_event(x_A, ReactionMoment(moment=M_A))

        return {
            "type": "cantilever",
            "x_A": x_A,
            "R_A": R_A,
            "M_A": M_A
        }

    # ---------------- SIMPLY SUPPORTED (2 Supports) ----------------
    elif len(supports) == 2:
        (x_A, _), (x_B, _) = supports[0], supports[1]
        span = x_B - x_A

        if abs(span) < TOLERANCE:
            raise ValueError("Support separation distance cannot be zero.")

        # \sum M_A = 0
        M_loads = sum(force * (x - x_A) for x, force in equiv_loads)
        M_total_about_A = M_applied + M_loads

        R_B = -M_total_about_A / span
        R_A = -(F_applied_total + R_B)

        beam.add_event(x_A, Reaction(force=R_A))
        beam.add_event(x_B, Reaction(force=R_B))

        return {
            "type": "simply_supported",
            "x_A": x_A,
            "R_A": R_A,
            "x_B": x_B,
            "R_B": R_B
        }


def calculate_sfd_bmd(beam: Beam, num_samples: int = 1000) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    critical_x = {p.x for p in beam.points}
    for dev in beam.distributed_events:
        critical_x.add(dev.start_x)
        critical_x.add(dev.end_x)

    extra_pts = []
    for cx in critical_x:
        if cx > 0: extra_pts.append(cx - 1e-7)
        if cx < beam.length: extra_pts.append(cx + 1e-7)

    base_grid = np.linspace(0, beam.length, num_samples)
    x_all = np.unique(np.sort(np.concatenate([base_grid, list(critical_x), extra_pts])))

    shear_force = np.zeros_like(x_all)
    bending_moment = np.zeros_like(x_all)

    # Collect discrete point forces for SFD
    point_forces = []
    for x, load in beam.point_loads(): point_forces.append((x, load.force))
    for p in beam.points:
        for ev in p.events:
            if isinstance(ev, Reaction): point_forces.append((p.x, ev.force))

    # Collect ALL moments for BMD (Applied AND Reaction moments)
    all_discrete_moments = [(x, m.moment) for x, m in beam.applied_moments()]
    for p in beam.points:
        for ev in p.events:
            if isinstance(ev, ReactionMoment):
                all_discrete_moments.append((p.x, ev.moment))

    udls = list(beam.udls())
    uvls = list(beam.uvls())

    for idx, x in enumerate(x_all):
        # 1. Point events
        V_pt = sum(f for px, f in point_forces if px <= x)
        M_pt = sum(f * (x - px) for px, f in point_forces if px <= x) + sum(
            m for px, m in all_discrete_moments if px <= x)

        V_udl = M_udl = 0.0
        for udl in udls:
            if x >= udl.end_x:
                V_udl += udl.resultant_force
                M_udl += udl.resultant_force * (x - udl.centroid_x)
            elif x > udl.start_x:
                active_len = x - udl.start_x
                active_force = udl.intensity * active_len
                V_udl += active_force
                M_udl += active_force * (x - (udl.start_x + active_len / 2.0))

        # 2. UVL Integration
        V_uvl = M_uvl = 0.0
        for uvl in uvls:
            if x >= uvl.end_x:
                V_uvl += uvl.resultant_force
                M_uvl += uvl.resultant_force * (x - uvl.centroid_x)
            elif x > uvl.start_x:
                a = x - uvl.start_x
                w_x = uvl.w1 + (uvl.w2 - uvl.w1) * (a / uvl.span)

                active_force = ((uvl.w1 + w_x) / 2.0) * a
                V_uvl += active_force

                if abs(uvl.w1 + w_x) < TOLERANCE:
                    active_centroid = uvl.start_x + (a / 2.0)
                else:
                    active_centroid = uvl.start_x + (a / 3.0) * ((uvl.w1 + 2 * w_x) / (uvl.w1 + w_x))

                M_uvl += active_force * (x - active_centroid)

        shear_force[idx] = V_pt + V_udl + V_uvl
        bending_moment[idx] = M_pt + M_udl + M_uvl

    return x_all, shear_force, bending_moment