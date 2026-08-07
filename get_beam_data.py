from typing import Callable, TypeVar
from beam import Beam, PointLoad, AppliedMoment, Support, UniformDistributedLoad, UniformVaryingLoad, PINNED, ROLLER
from Validation import (
    validate_support_count, validate_points, validate_float_list,
    validate_udl_count, validate_udl_spec, validate_uvl_count, validate_uvl_spec,
    validate_support_location, validate_support_separation,
)

T = TypeVar("T")


def prompt_until_valid(prompt_text: str, validator_fn: Callable[[str], T]) -> T:
    while True:
        try:
            raw_val = input(prompt_text)
            return validator_fn(raw_val)
        except (ValueError, TypeError) as e:
            print(f"  [Input Error] {e} Please try again.\n")


def get_beam_data(interactive: bool = True) -> Beam:
    print("--- Beam Data Input ---")

    if interactive:
        number_of_supports = prompt_until_valid("Enter number of supports (e.g., 2): ", validate_support_count)

        print("\nEnter point locations as comma-separated values (e.g., 0.0, 3.0, 4.5, 6.0):")
        points = prompt_until_valid("  Point locations x (m): ", validate_points)
        num_pts, beam_length = len(points), max(points)

        point_loads = prompt_until_valid(
            f"  Point loads ({num_pts} values in kN): ",
            lambda raw: validate_float_list(raw, num_pts, "Point loads"),
        )
        moments = prompt_until_valid(
            f"  Applied moments ({num_pts} values in kNm): ",
            lambda raw: validate_float_list(raw, num_pts, "Applied moments"),
        )

        udl_count = prompt_until_valid("\nEnter number of UDLs [default = 0]: ", validate_udl_count)
        udls = []
        for i in range(udl_count):
            udls.append(prompt_until_valid(
                f"  UDL #{i + 1} (start_x, end_x, intensity): ",
                lambda raw: validate_udl_spec(raw, beam_length)
            ))

        uvl_count = prompt_until_valid("\nEnter number of UVLs [default = 0]: ", validate_uvl_count)
        uvls = []
        for i in range(uvl_count):
            uvls.append(prompt_until_valid(
                f"  UVL #{i + 1} (start_x, end_x, w1, w2): ",
                lambda raw: validate_uvl_spec(raw, beam_length)
            ))

        x_support_A = prompt_until_valid(
            f"\nEnter Support A location [default = {points[0]}]: ",
            lambda raw: validate_support_location(raw, points[0], beam_length, "Support A"),
        )

        def validate_b_wrapper(raw_input: str) -> float:
            xB = validate_support_location(raw_input, points[-1], beam_length, "Support B")
            validate_support_separation(x_support_A, xB)
            return xB

        x_support_B = prompt_until_valid(f"Enter Support B location [default = {points[-1]}]: ", validate_b_wrapper)

    else:
        # DEFAULT TEST CASE includes Point Load, UDL, and UVL (Triangle)
        points = [0.0, 2.5, 5.0, 8.0]
        point_loads = [0.0, -15.0, 0.0, 0.0]
        moments = [0.0, 0.0, 0.0, 0.0]
        udls = [(0.0, 2.5, -10.0)]
        uvls = [(5.0, 8.0, 0.0, -20.0)]  # Triangle load growing to -20kN/m
        x_support_A, x_support_B = 0.0, 8.0

    beam = Beam(length=max(points))

    for x, load, moment in zip(points, point_loads, moments):
        if load != 0: beam.add_event(x, PointLoad(force=load))
        if moment != 0: beam.add_event(x, AppliedMoment(moment=moment))

    for start_x, end_x, intensity in udls:
        beam.add_distributed_event(UniformDistributedLoad(start_x, end_x, intensity))

    for start_x, end_x, w1, w2 in uvls:
        beam.add_distributed_event(UniformVaryingLoad(start_x, end_x, w1, w2))

    beam.add_event(x_support_A, Support(support_type=PINNED))
    beam.add_event(x_support_B, Support(support_type=ROLLER))

    return beam