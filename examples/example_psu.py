"""
Example: Power Supply Unit (PSU) Circuit.

This example demonstrates how to create a PSU circuit using the
standard circuits library.
"""

from pathlib import Path
from pyschemaelectrical import create_autonumberer, std_circuits, render_system
from constants import Terminals, Pins, Paths


def main():
    """
    Create a PSU circuit example.
    
    Demonstrates:
    - Creating a power supply unit circuit
    - Configuring AC input (L/N/PE) and DC output (24V/GND) terminals
    - Custom pin configuration
    """
    # Initialize autonumbering state
    state = create_autonumberer()
    
    # Create output directory
    output_path = Path(Paths.PSU)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create PSU circuit
    print("Creating PSU circuit...")
    state, circuit, used_terminals = std_circuits.psu(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.AC_INPUT,
        tm_bot_left=Terminals.FUSED_24V,
        tm_bot_right=Terminals.GND,
        tm_top_pins=(Pins.L, Pins.N, Pins.PE),
        tm_bot_left_pins=(Pins.V24_PLUS,),
        tm_bot_right_pins=(Pins.GND,)
    )
    
    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ PSU circuit saved to: {Paths.PSU}")
    print(f"  Used terminals: {used_terminals}")


if __name__ == "__main__":
    main()
