from get_beam_data import get_beam_data
from solvers import solve_reactions, calculate_sfd_bmd
from plotting import plot_beam_results


def main():
    try:
        # 1. Get input data interactively
        beam = get_beam_data(interactive=False)

        # 2. Solve support reactions
        x_A, R_A, x_B, R_B = solve_reactions(beam)
        print(f"  • Reaction R_A at x = {x_A:.2f} m : {R_A:.2f} kN")
        print(f"  • Reaction R_B at x = {x_B:.2f} m : {R_B:.2f} kN\n")

        # 3. Calculate SFD and BMD arrays
        x_grid, V_grid, M_grid = calculate_sfd_bmd(beam)

        # 4. Render plots
        print("Rendering Shear Force and Bending Moment Diagrams...")
        plot_beam_results(beam, x_grid, V_grid, M_grid)

    except Exception as e:
        print(f"\n[Fatal Error] Could not complete analysis: {e}")


if __name__ == "__main__":
    main()