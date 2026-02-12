"""
Example: Motor Control Circuit.

This example demonstrates how to create a motor control circuit using the
standard circuits library.
"""

from pathlib import Path

from pyschemaelectrical import create_autonumberer, render_system, std_circuits

from .constants import Paths, Terminals


def main():
    """
    Create a motor control circuit example.

    Demonstrates:
    - Creating a standard motor control circuit with new layout
    - Inverted SPDT contact for correct schematics
    - Manual layout handling within the builder
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path(Paths.MOTOR_CONTROL)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create motor control circuit
    print("Creating motor control circuit...")

    # Note: We configure the output terminals explicitly to use
    # different pins on the same terminal strip (LIGHTS_SWITCHES).
    state, circuit, used_terminals = std_circuits.spdt(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.EM_STOP,
        tm_bot_left=Terminals.LIGHTS_SWITCHES,
        tm_bot_right=Terminals.LIGHTS_SWITCHES,
        tm_bot_left_pins=("1",),
        tm_bot_right_pins=("2",),
    )

    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Motor control circuit saved to: {Paths.MOTOR_CONTROL}")
    print(f"  Used terminals: {used_terminals}")


if __name__ == "__main__":
    main()
