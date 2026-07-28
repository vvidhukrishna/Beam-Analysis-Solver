from calculate_reactions import calculate_reactions
from get_beam_data import get_beam_data


def main():
    # Prompt user for interaction choice or use defaults
    mode = (input("Run interactive mode? (y/n, press Enter for default test data): ").strip().lower())
    interactive = mode == "y"

    # Collect and validate beam input data
    beam_data = get_beam_data(interactive=interactive)

    # Calculate reactions and validate equilibrium
    reactions = calculate_reactions(beam_data)

    # Print results
    print("\nComputed Reaction Forces:")
    print(f"  Reaction R_A at x = {reactions['x_support_A']:.2f} m : {reactions['R_A']:.4f} kN")
    print(f"  Reaction R_B at x = {reactions['x_support_B']:.2f} m : {reactions['R_B']:.4f} kN")


if __name__ == "__main__":
    main()