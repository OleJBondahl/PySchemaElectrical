"""
Example: Switch Circuit.

This example demonstrates how to create a simple switch circuit using the
standard circuits library.
"""

from pathlib import Path
from pyschemaelectrical import create_autonumberer, std_circuits, render_system
from constants import Terminals, Paths


def main():
    """
    Create a switch circuit example.
    
    Demonstrates:
    - Creating a simple normally-open switch circuit
    - Single-pole control
    - Common use case: switch between power source and ground
    """
    # Initialize autonumbering state
    state = create_autonumberer()
    
    # Create output directory
    output_path = Path(Paths.SWITCH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create switch circuit
    print("Creating switch circuit...")
    state, circuit, used_terminals = std_circuits.no_contact(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.FUSED_24V,
        tm_bot=Terminals.GND
    )
    
    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Switch circuit saved to: {Paths.SWITCH}")
    print(f"  Used terminals: {used_terminals}")


if __name__ == "__main__":
    main()
