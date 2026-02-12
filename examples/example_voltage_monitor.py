"""
Example: Voltage Monitor Circuit.

This example demonstrates how to create a voltage monitor circuit using the
standard circuits library.
"""

from pathlib import Path

from pyschemaelectrical import create_autonumberer, render_system, std_circuits

from .constants import Paths, Terminals


def main():
    """
    Create a voltage monitor circuit example.

    Demonstrates:
    - Creating a voltage monitoring circuit
    - Monitoring three-phase voltage
    - Custom pin configuration for inputs and outputs
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path(Paths.VOLTAGE_MONITOR)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create voltage monitor circuit (modeled as a coil circuit)
    print("Creating voltage monitor circuit...")
    state, circuit, used_terminals = std_circuits.coil(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.VOLTAGE_MONITOR,  # Monitors Pin 1 and Pin 2 of this terminal
    )

    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Voltage monitor circuit saved to: {Paths.VOLTAGE_MONITOR}")
    print(f"  Used terminals: {used_terminals}")


if __name__ == "__main__":
    main()
