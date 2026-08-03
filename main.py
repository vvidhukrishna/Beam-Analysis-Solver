from get_beam_data import get_beam_data
from solve_reactions import solve_reactions
from SFD_solver import calculate_sfd
from BMD_solver import calculate_bmd
from plot_sfd import plot_sfd
from plot_bmd import plot_bmd


def main() -> None:
    """Main execution flow for gathering input, solving reactions, and plotting SFD/BMD."""
    mode = input("Run interactive mode? (y/n, press Enter for default test data): ").strip().lower()
    interactive = mode == "y"

    # 1. Collect input and create Beam object structure
    beam = get_beam_data(interactive=interactive)

    # 2. Solve reaction forces and attach Reaction events directly to the Beam
    solve_reactions(beam)

    # 3. Calculate Shear Force Diagram (SFD) and Bending Moment Diagram (BMD) data
    sfd_points = calculate_sfd(beam)
    bmd_points = calculate_bmd(beam)

    # 4. Render plots
    plot_sfd(sfd_points)
    plot_bmd(bmd_points)

if __name__ == "__main__":
    main()