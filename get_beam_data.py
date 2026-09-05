from beam import Beam, Support, UniformDistributedLoad, UniformVaryingLoad, PointLoad, AppliedMoment, PINNED, ROLLER, FIXED
from Validation import (
    validate_points, validate_float_list, validate_udl_count, validate_udl_spec,
    validate_support_location, validate_support_order, validate_uvl_count,
    validate_uvl_spec, validate_support_count)


def get_beam_data(interactive=True) -> Beam:
    """Collects beam parameters and returns a populated Beam object."""
    print("\n--- Beam Configuration ---")

    # Length
    length = float(input("Enter length of beam (m): "))
    while length <= 0:
        print("Length must be > 0.")
        length = float(input("Enter length of beam (m): "))
    beam = Beam(length)

    # Supports
    supp_count_str = input("Enter number of supports (1 for Cantilever, 2 for Simply Supported): ")
    supp_count = validate_support_count(supp_count_str)

    if supp_count == 1:
        print("Cantilever selected: Fixed support automatically placed at x = 0.0m")
        beam.add_event(0.0, Support(FIXED))
    else:
        x_A_str = input(f"Enter location for Support A (m) [Default: 0]: ")
        x_A = validate_support_location(x_A_str, 0.0, length, "Support A")

        x_B_str = input(f"Enter location for Support B (m) [Default: {length}]: ")
        x_B = validate_support_location(x_B_str, length, length, "Support B")

        validate_support_order(x_A, x_B)
        beam.add_event(x_A, Support(PINNED))
        beam.add_event(x_B, Support(ROLLER))

    # Point Loads
    pt_loc_str = input("\nEnter Point Load locations separated by comma (press Enter to skip): ")
    if pt_loc_str.strip():
        pt_locs = validate_points(pt_loc_str, length)
        mag_str = input(f"Enter {len(pt_locs)} Point Load magnitudes separated by comma: ")
        pt_mags = validate_float_list(mag_str, len(pt_locs), "Point Load magnitudes")

        for loc, mag in zip(pt_locs, pt_mags):
            beam.add_event(loc, PointLoad(mag))

    # Applied Moments
    mom_loc_str = input("\nEnter Applied Moment locations separated by comma (press Enter to skip): ")
    if mom_loc_str.strip():
        mom_locs = validate_points(mom_loc_str, length)
        mag_str = input(f"Enter {len(mom_locs)} Moment magnitudes separated by comma: ")
        mom_mags = validate_float_list(mag_str, len(mom_locs), "Moment magnitudes")

        for loc, mag in zip(mom_locs, mom_mags):
            beam.add_event(loc, AppliedMoment(mag))

    # UDLs
    udl_count_str = input("\nEnter the number of Uniform Distributed Loads (UDLs) [Default: 0]: ")
    udl_count = validate_udl_count(udl_count_str)
    for i in range(udl_count):
        spec_str = input(f"  UDL {i + 1} (format: start_x, end_x, intensity): ")
        s, e, intensity = validate_udl_spec(spec_str, length)
        beam.add_distributed_event(UniformDistributedLoad(s, e, intensity))

    # UVLs
    uvl_count_str = input("\nEnter the number of Uniform Varying Loads (UVLs) [Default: 0]: ")
    uvl_count = validate_uvl_count(uvl_count_str)
    for i in range(uvl_count):
        spec_str = input(f"  UVL {i + 1} (format: start_x, end_x, w1, w2): ")
        s, e, w1, w2 = validate_uvl_spec(spec_str, length)
        beam.add_distributed_event(UniformVaryingLoad(s, e, w1, w2))
    return beam


if __name__ == "__main__":
    # Test runner logic if executed directly in terminal
    from solvers import solve_reactions
    try:
        b = get_beam_data()
        reactions = solve_reactions(b)
        print("\n--- Beam Reactions ---")
        if reactions["type"] == "cantilever":
            print(
                f"Fixed Support (x={reactions['x_A']}): Reaction = {reactions['R_A']} kN, Moment = {reactions['M_A']} kNm")
        else:
            print(f"Support A (x={reactions['x_A']}): {reactions['R_A']} kN")
            print(f"Support B (x={reactions['x_B']}): {reactions['R_B']} kN")
    except Exception as e:
        print(f"Error: {e}")