"""
Example: Emergency Stop Circuit.

This example demonstrates how to create an emergency stop circuit using the
standard circuits library.
"""

from pathlib import Path
from pyschemaelectrical import create_autonumberer, std_circuits, render_system
from .constants import Terminals, Paths


def main():
    """
    Create an emergency stop circuit example.

    Demonstrates:
    - Creating a basic emergency stop circuit
    - Single-pole safety circuit configuration
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path(Paths.EMERGENCY_STOP)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create emergency stop circuit
    print("Creating emergency stop circuit...")
    state, circuit, used_terminals = std_circuits.emergency_stop(
        state=state, x=0, y=0, tm_top=Terminals.FUSED_24V, tm_bot=Terminals.EM_STOP
    )

    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Emergency stop circuit saved to: {Paths.EMERGENCY_STOP}")
    print(f"  Used terminals: {used_terminals}")


if __name__ == "__main__":
    main()
