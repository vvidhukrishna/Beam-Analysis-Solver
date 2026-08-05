from beam import Beam, TOLERANCE


def validate_support_count(count_str: str) -> int:
    """Validates support count input."""
    count = int(count_str)
    if count != 2:
        raise ValueError(f"Version 1 only supports exactly 2 supports (got {count}).")
    return count


def validate_points(points_str: str) -> list[float]:
    """Parses and validates point locations."""
    if not points_str.strip():
        raise ValueError("Points list cannot be empty.")

    pts = [float(val.strip()) for val in points_str.split(",")]
    beam_length = max(pts)

    if beam_length <= 0:
        raise ValueError(f"Beam length must be greater than 0 (got {beam_length}m).")

    for x in pts:
        if x < 0:
            raise ValueError(f"Point location x = {x}m cannot be negative.")

    return pts


def validate_float_list(raw_input: str, expected_length: int, label: str) -> list[float]:
    """Parses float list and ensures it matches points array length."""
    raw_input = raw_input.strip()
    if not raw_input:
        return [0.0] * expected_length

    vals = [float(val.strip()) for val in raw_input.split(",")]
    if len(vals) != expected_length:
        raise ValueError(f"Length mismatch! Expected {expected_length} values for {label}, but got {len(vals)}.")

    return vals


def validate_support_location(
        loc_str: str, default: float, beam_length: float, support_name: str
) -> float:
    """Validates support position relative to beam span."""
    val = float(loc_str) if loc_str.strip() else default
    if not (0 <= val <= beam_length):
        raise ValueError(f"{support_name} (x = {val}m) must be between 0 and beam length ({beam_length}m).")
    return val


def validate_support_separation(x_A: float, x_B: float) -> None:
    """Checks that support A and support B are not at the exact same location."""
    if x_A == x_B:
        raise ValueError(f"Support B cannot be at the exact same location as Support A (x = {x_A}m).")


def validate_equilibrium(beam: Beam, R_A: float, R_B: float, x_A: float, x_B: float) -> None:
    """Sanity check to confirm sum of vertical forces and moments equal zero."""
    span = x_B - x_A
    total_loads = sum(load.force for _, load in beam.point_loads())
    force_balance = R_A + R_B + total_loads

    M_about_B = -R_A * span
    for x, load in beam.point_loads():
        M_about_B += (x - x_B) * load.force
    for _, moment in beam.applied_moments():
        M_about_B += moment.moment

    if abs(force_balance) > TOLERANCE or abs(M_about_B) > TOLERANCE:
        raise RuntimeError(
            f"Equilibrium check failed! Force error: {force_balance:.2e}, Moment error: {M_about_B:.2e}"
        )