from typing import Callable, TypeVar
from beam import Beam, PointLoad, AppliedMoment, Support, UniformDistributedLoad, PINNED, ROLLER
from Validation import (
    validate_support_count,
    validate_points,
    validate_float_list,
    validate_udl_count,
    validate_udl_spec,
    validate_support_location,
    validate_support_separation,
)

T = TypeVar("T")


def prompt_until_valid(prompt_text: str, validator_fn: Callable[[str], T]) -> T:
    """Generic wrapper that reprompts until validation succeeds."""
    while True:
        try:
            raw_val = input(prompt_text)
            return validator_fn(raw_val)
        except (ValueError, TypeError) as e:
            print(f"  [Input Error] {e} Please try again.\n")


def get_beam_data(interactive: bool = True) -> Beam:
    """Prompts interactively for beam, point loads, UDLs, and supports."""
    print("--- Beam Data Input ---")
    print("Sign Convention:")
    print("  • Positive x : right")
    print("  • Positive y : upward (forces/reactions)")
    print("  • Downward loads : negative")
    print("  • Counter-clockwise moments : positive\n")

    if interactive:
        # 1. Supports count
        number_of_supports = prompt_until_valid(
            "Enter number of supports (e.g., 2): ",
            validate_support_count
        )

        # 2. Coordinates
        print("\nEnter point locations as comma-separated values (e.g., 0.0, 3.0, 4.5, 6.0):")
        points = prompt_until_valid(
            "  Point locations x (m): ",
            validate_points
        )

        num_pts = len(points)
        beam_length = max(points)

        # 3. Point Loads & Moments
        point_loads = prompt_until_valid(
            f"  Point loads ({num_pts} values in kN, e.g., 0, -20, 0, 0): ",
            lambda raw: validate_float_list(raw, num_pts, "Point loads"),
        )

        moments = prompt_until_valid(
            f"  Applied moments ({num_pts} values in kNm, e.g., 0, 10, -15, 0): ",
            lambda raw: validate_float_list(raw, num_pts, "Applied moments"),
        )

        # 4. UDL Inputs
        udl_count = prompt_until_valid(
            "\nEnter number of Uniform Distributed Loads (UDLs) [default = 0]: ",
            validate_udl_count
        )

        udls: list[tuple[float, float, float]] = []
        for i in range(udl_count):
            udl_spec = prompt_until_valid(
                f"  UDL #{i+1} (start_x, end_x, intensity in kN/m, e.g. '1.0, 4.0, -10.0'): ",
                lambda raw: validate_udl_spec(raw, beam_length)
            )
            udls.append(udl_spec)

        # 5. Support Locations
        x_support_A = prompt_until_valid(
            f"\nEnter Support A location x (m) [default = {points[0]}]: ",
            lambda raw: validate_support_location(raw, points[0], beam_length, "Support A"),
        )

        def validate_b_wrapper(raw_input: str) -> float:
            xB = validate_support_location(raw_input, points[-1], beam_length, "Support B")
            validate_support_separation(x_support_A, xB)
            return xB

        x_support_B = prompt_until_valid(
            f"Enter Support B location x (m) [default = {points[-1]}]: ",
            validate_b_wrapper,
        )

    else:
        points = [0.0, 2.5, 4.0, 5.0, 6.0]
        point_loads = [0.0, -20.0, -15.0, 0.0, -10.0]
        moments = [0.0, 10.0, -15.0, 0.0, 0.0]
        udls = [(1.0, 4.0, -10.0)]
        x_support_A = points[0]
        x_support_B = points[-1]

    # Instantiate and assemble Beam
    beam = Beam(length=max(points))

    # Point loads & applied moments
    for x, load, moment in zip(points, point_loads, moments):
        if load != 0.0:
            beam.add_event(x, PointLoad(force=load))
        if moment != 0.0:
            beam.add_event(x, AppliedMoment(moment=moment))

    # UDLs
    for start_x, end_x, intensity in udls:
        beam.add_distributed_event(UniformDistributedLoad(start_x, end_x, intensity))

    # Supports
    beam.add_event(x_support_A, Support(support_type=PINNED))
    beam.add_event(x_support_B, Support(support_type=ROLLER))

    return beam