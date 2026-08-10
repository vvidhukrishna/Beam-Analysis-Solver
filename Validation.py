from beam import Beam, TOLERANCE


def validate_support_count(count_str: str) -> int:
    """Validates support count input."""
    count = int(count_str)
    if count != 2:
        raise ValueError(f"Version 2 only supports exactly 2 supports (got {count}).")
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
    """Parses float list and ensures length matches points array."""
    raw_input = raw_input.strip()
    if not raw_input:
        return [0.0] * expected_length

    vals = [float(val.strip()) for val in raw_input.split(",")]
    if len(vals) != expected_length:
        raise ValueError(
            f"Length mismatch! Expected {expected_length} values for {label}, but got {len(vals)}."
        )

    return vals


def validate_udl_count(raw_str: str) -> int:
    """Validates UDL count."""
    count = int(raw_str.strip() or "0")
    if count < 0:
        raise ValueError("UDL count cannot be negative.")
    return count


def validate_udl_spec(raw_str: str, beam_length: float) -> tuple[float, float, float]:
    """Parses single UDL string: 'start_x, end_x, intensity'."""
    parts = [float(p.strip()) for p in raw_str.split(",")]
    if len(parts) != 3:
        raise ValueError("UDL input requires exactly 3 values: start_x, end_x, intensity")

    start_x, end_x, intensity = parts

    if not (0 <= start_x < end_x <= beam_length):
        raise ValueError(
            f"Invalid UDL bounds ({start_x}m to {end_x}m). Must satisfy 0 <= start_x < end_x <= {beam_length}m."
        )

    return start_x, end_x, intensity


def validate_support_location(
    loc_str: str, default: float, beam_length: float, support_name: str
) -> float:
    """Validates support position relative to beam span."""
    val = float(loc_str) if loc_str.strip() else default
    if not (0 <= val <= beam_length):
        raise ValueError(f"{support_name} (x = {val}m) must be between 0 and beam length ({beam_length}m).")
    return val


def validate_support_separation(x_A: float, x_B: float) -> None:
    """Checks that supports A and B are distinct."""
    if abs(x_A - x_B) < TOLERANCE:
        raise ValueError(f"Support B cannot be at the exact same location as Support A (x = {x_A}m).")

def validate_uvl_count(raw_str: str) -> int:
    count = int(raw_str.strip() or "0")
    if count < 0:
        raise ValueError("UVL count cannot be negative.")
    return count

def validate_uvl_spec(raw_str: str, beam_length: float) -> tuple[float, float, float, float]:
    """Parses UVL string: 'start_x, end_x, w1, w2'."""
    parts = [float(p.strip()) for p in raw_str.split(",")]
    if len(parts) != 4:
        raise ValueError("UVL input requires exactly 4 values: start_x, end_x, w1, w2")

    start_x, end_x, w1, w2 = parts

    if not (0 <= start_x < end_x <= beam_length):
        raise ValueError(f"Invalid UVL bounds. Must satisfy 0 <= start_x < end_x <= {beam_length}m.")

    return start_x, end_x, w1, w2

def analyze_input_state(text, expected_type="float"):
    """
    Analyzes a string and returns its typing state:
    'empty', 'incomplete', 'valid', or 'invalid'
    """
    text = text.strip()
    if not text:
        return "empty"

    # Common incomplete typing states for numbers
    if text in ["-", ".", "-."]:
        return "incomplete"

    if text.endswith("e") or text.endswith("e-"):
        return "incomplete"  # user is typing scientific notation

    try:
        if expected_type == "float":
            val = float(text)
            if val <= 0:  # For beam length, we strictly want > 0
                return "invalid"
            return "valid"

        elif expected_type == "float_list":
            # e.g., "0, 2.5, 5.0, 6"
            parts = [p.strip() for p in text.split(",")]
            for part in parts:
                if part in ["", "-", ".", "-."]:
                    return "incomplete"  # Still typing after a comma
                float(part)  # Test conversion
            return "valid"

        elif expected_type == "udl_list":
            # e.g., "0, 2, -10; 2, 4, -15"
            return _check_complex_list(text, required_parts=3)

        elif expected_type == "uvl_list":
            # e.g., "0, 2, 0, -10"
            return _check_complex_list(text, required_parts=4)

    except ValueError:
        return "invalid"


def _check_complex_list(text, required_parts):
    # Split by semicolons for multiple loads
    groups = text.split(";")
    for group in groups:
        group = group.strip()
        if not group:
            continue  # trailing semicolon is okay, or user is about to type next

        parts = [p.strip() for p in group.split(",")]

        # If they haven't typed enough commas yet, it's incomplete
        if len(parts) < required_parts:
            # Check if what they HAVE typed so far is valid numbers/incomplete
            for part in parts:
                if part and part not in ["-", ".", "-."]:
                    try:
                        float(part)
                    except ValueError:
                        return "invalid"
            return "incomplete"

        # If they typed too many commas
        if len(parts) > required_parts:
            return "invalid"

        # Check all parts in the group
        for part in parts:
            if part in ["", "-", ".", "-."]:
                return "incomplete"
            try:
                float(part)
            except ValueError:
                return "invalid"

    return "valid"