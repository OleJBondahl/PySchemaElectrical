"""
Example: Changeover Switch Circuit.

This example demonstrates how to create a changeover switch circuit using the
standard circuits library.
"""

from pathlib import Path

from .constants import Paths, Terminals

from pyschemaelectrical import create_autonumberer, render_system, std_circuits


def main():
    """
    Create a changeover switch circuit example.

    Demonstrates:
    - Creating a manual 3-pole changeover switch
    - Switching between main and emergency power supplies
    - Three-phase power distribution
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path(Paths.CHANGEOVER)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create changeover circuit
    print("Creating changeover switch circuit...")
    state, circuit, used_terminals = std_circuits.changeover(
        state=state,
        x=0,
        y=0,
        tm_top_left=Terminals.MAIN_SUPPLY,
        tm_top_right=Terminals.EMERGENCY_SUPPLY,
        tm_bot=Terminals.CHANGEOVER_OUTPUT,
    )

    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Changeover circuit saved to: {Paths.CHANGEOVER}")
    print(f"  Used terminals: {used_terminals}")


if __name__ == "__main__":
    main()
