TOLERANCE = 1e-6

def calculate_reactions(beam_data: dict) -> dict:

    points = beam_data["points"]
    point_loads = beam_data["point_loads"]
    moments = beam_data["moments"]
    x_support_A = beam_data["x_support_A"]
    x_support_B = beam_data["x_support_B"]

    length = x_support_B - x_support_A

    # Compute total applied moment about support A (x = x_support_A)
    M_applied_about_A = 0.0
    for i in range(len(points)):
        # Moment arm relative to support A
        arm = points[i] - x_support_A
        M_applied_about_A += (arm * point_loads[i]) + moments[i]

    # Use ΣM_A = 0 to calculate reaction R_B at support B
    # ΣM_A = M_applied_about_A + (R_B * length) = 0
    R_B = -M_applied_about_A / length

    # Use ΣFy = 0 to calculate reaction R_A at support A
    # ΣFy = R_A + R_B + sum(point_loads) = 0
    total_applied_force = sum(point_loads)
    R_A = -total_applied_force - R_B

    # Validate solution using equilibrium check
    # Moment balance about support B
    M_about_B = (sum((p - x_support_B) * load for p, load in zip(points, point_loads)) + sum(moments) - (R_A * length))

    force_balance = R_A + R_B + total_applied_force

    # Force balance across the bridge
    if abs(force_balance) <= TOLERANCE and abs(M_about_B) <= TOLERANCE:
        pass
    else:
        raise RuntimeError(f"Equilibrium check failed! Force error: {force_balance:.2e}, Moment error: {M_about_B:.2e}")

    # Return reaction results
    return {
        "R_A": R_A,
        "R_B": R_B,
        "x_support_A": x_support_A,
        "x_support_B": x_support_B,
    }