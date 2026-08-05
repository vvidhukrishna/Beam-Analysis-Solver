from get_beam_data import get_beam_data
from solvers import solve_reactions, calculate_sfd, calculate_bmd
from plotting import plot_sfd, plot_bmd


def main() -> None:
    """Main execution flow for gathering input, solving reactions, and plotting SFD/BMD."""
    mode = input("Run interactive mode? (y/n, press Enter for default test data): ").strip().lower()
    interactive = mode == "y"

    # 1. Collect input and create Beam structure
    beam = get_beam_data(interactive=interactive)

    # 2. Solve reaction forces
    solve_reactions(beam)

    # 3. Calculate SFD and BMD
    sfd_points = calculate_sfd(beam)
    bmd_points = calculate_bmd(beam)

    # 4. Render plots
    plot_sfd(sfd_points)
    plot_bmd(bmd_points)


if __name__ == "__main__":
    main()