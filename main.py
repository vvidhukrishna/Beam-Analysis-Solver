from get_beam_data import get_beam_data
from solve_reactions import solve_reactions
from beam import Support, Reaction


def main() -> None:
    """Main execution flow for gathering input, solving reactions, and outputting results."""
    mode = input("Run interactive mode? (y/n, press Enter for default test data): ").strip().lower()
    interactive = mode == "y"

    # Collect input and create Beam object structure
    beam = get_beam_data(interactive=interactive)

    # Solve reaction forces and attach Reaction events directly to the Beam
    solve_reactions(beam)

    # Print results from the data structure
    print("\nComputed Reaction Forces:")
    for pt in beam.points:
        has_support = any(isinstance(e, Support) for e in pt.events)
        if has_support:
            for event in pt.events:
                if isinstance(event, Reaction):
                    print(f"  Reaction force at x = {pt.x:.2f} m : {event.force:.4f} kN")


if __name__ == "__main__":
    main()