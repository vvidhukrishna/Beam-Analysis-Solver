from get_beam_data import get_beam_data
from solve_reactions import solve_reactions
from SFD_solver import calculate_sfd
from BMD_solver import calculate_bmd
from beam import Support, Reaction


def main() -> None:
    """Main execution flow for gathering input, solving reactions, and calculating SFD."""
    mode = input("Run interactive mode? (y/n, press Enter for default test data): ").strip().lower()
    interactive = mode == "y"

    # 1. Collect input and create Beam object structure
    beam = get_beam_data(interactive=interactive)

    # 2. Solve reaction forces and attach Reaction events directly to the Beam
    solve_reactions(beam)

    # 3. Print computed reaction forces
    print("\nComputed Reaction Forces:")
    for pt in beam.points:
        has_support = any(isinstance(e, Support) for e in pt.events)
        if has_support:
            for event in pt.events:
                if isinstance(event, Reaction):
                    print(f"  Reaction force at x = {pt.x:.2f} m : {event.force:.4f} kN")

    # 4. Calculate Shear Force Diagram (SFD) data
    sfd_points = calculate_sfd(beam)

    # 5. Calculate Bending Moment Diagram (BMD) data
    bmd_points = calculate_bmd(beam)

    # 6. Print SFD output
    print("\nShear Force Diagram Data [(x, shear_force)]:")
    print(sfd_points)

    print("\nFormatted SFD Profile:")
    for x, shear in sfd_points:
        print(f"  x = {x:5.2f} m | V = {shear:7.2f} kN")

    # 7. Print BMD output
    print("\nBending Moment Diagram Data [(x, bending_moment)]:")
    print(bmd_points)

    print("\nFormatted BMD Profile:")
    for x, moment in bmd_points:
        print(f"  x = {x:5.2f} m | M = {moment:7.2f} kNm")

if __name__ == "__main__":
    main()