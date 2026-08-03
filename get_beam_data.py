from beam import Beam, PointLoad, AppliedMoment, Support, PINNED, ROLLER


def make_float_list(prompt_text: str) -> list[float]:
    """Helper to parse a comma-separated string of user input into floats."""
    raw_input = input(prompt_text).strip()
    if not raw_input:
        return []
    return [float(val.strip()) for val in raw_input.split(",")]


def validate_beam_inputs(
    number_of_supports: int,
    x_support_A: float,
    x_support_B: float,
    points: list[float],
    point_loads: list[float],
    moments: list[float],
) -> None:
    """Validates raw numerical user inputs before assembling the Beam structure."""
    if not points:
        raise ValueError("Points list cannot be empty.")

    if len(points) != len(point_loads) or len(points) != len(moments):
        raise ValueError("Mismatch in dimensions: 'points', 'point_loads', and 'moments' must have equal length.")

    beam_length = max(points)

    if number_of_supports != 2:
        raise ValueError(f"Version 1 only supports exactly 2 supports, got {number_of_supports}.")

    if beam_length <= 0:
        raise ValueError(f"Beam length must be greater than 0, got {beam_length}.")

    if not (0 <= x_support_A < beam_length):
        raise ValueError(f"Support A (x = {x_support_A}) must satisfy 0 <= x_support_A < beam_length ({beam_length}).")

    if not (0 <= x_support_B <= beam_length):
        raise ValueError(f"Support B (x = {x_support_B}) must satisfy 0 <= x_support_B <= beam_length ({beam_length}).")

    if x_support_A == x_support_B:
        raise ValueError(f"Support A and Support B cannot be at the same location (x = {x_support_A}).")

    for p in points:
        if not (0 <= p <= beam_length):
            raise ValueError(f"Load/moment location at x = {p} must lie between 0 and beam_length ({beam_length}).")


def get_beam_data(interactive: bool = True) -> Beam:
    """
    Prompts or uses default test data to instantiate and return a populated Beam object.
    """
    print("--- Beam Data Input ---")
    print("Sign Convention:")
    print("  • Positive x : right")
    print("  • Positive y : upward")
    print("  • Counter-clockwise moments : positive")
    print("  • Downward loads : negative\n")

    if interactive:
        try:
            number_of_supports = int(input("Enter number of supports (e.g., 2): "))

            print("\nEnter coordinates as comma-separated values (e.g., 0.0, 3.0, 4.5, 6.0):")
            points = make_float_list("  Point locations x (m): ")
            point_loads = make_float_list("  Point loads (kN): ")
            moments = make_float_list("  Applied moments (kNm): ")

            x_support_A = float(input("\nEnter Support A location x (m) [default = 0.0]: ") or points[0])
            x_support_B = float(input(f"Enter Support B location x (m) [default = {points[-1]}]: ") or points[-1])

        except ValueError as e:
            raise ValueError(f"Invalid numeric input provided: {e}") from e
    else:
        number_of_supports = 2
        points = [0.0, 2.5, 4.0, 5.0, 6.0]
        point_loads = [0.0, -20.0, -15.0, 0.0, -10.0]
        moments = [0.0, 10.0, -15.0, 0.0, 0.0]
        x_support_A = points[0]
        x_support_B = points[-2]

    # Validate raw inputs
    validate_beam_inputs(
        number_of_supports,
        x_support_A,
        x_support_B,
        points,
        point_loads,
        moments,
    )

    # Instantiate Beam object
    beam = Beam(length=max(points))

    # Populate loads and moments via beam.add_event()
    for x, load, moment in zip(points, point_loads, moments):
        if load != 0.0:
            beam.add_event(x, PointLoad(force=load))
        if moment != 0.0:
            beam.add_event(x, AppliedMoment(moment=moment))

    # Attach supports via beam.add_event()
    beam.add_event(x_support_A, Support(support_type=PINNED))
    beam.add_event(x_support_B, Support(support_type=ROLLER))

    return beam