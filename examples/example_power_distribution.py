"""
Example: Power Distribution System.

This example demonstrates how to create a complete power distribution system
using the standard circuits library.
"""

from pathlib import Path
from pyschemaelectrical import create_autonumberer, std_circuits, render_system
from .constants import Terminals, Paths


def main():
    """
    Create a power distribution system example.

    Demonstrates:
    - Creating a complete power distribution system
    - Combining changeover, voltage monitor, and PSU circuits
    - Complex multi-component system integration
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path(Paths.POWER_DISTRIBUTION)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create power distribution system
    print("Creating power distribution system...")
    state, circuit, used_terminals = std_circuits.power_distribution(
        state=state,
        x=0,
        y=0,
        terminal_maps={
            "INPUT_1": Terminals.MAIN_SUPPLY,
            "INPUT_2": Terminals.EMERGENCY_SUPPLY,
            "OUTPUT": Terminals.CHANGEOVER_OUTPUT,
            "PSU_INPUT": Terminals.AC_INPUT,
            "PSU_OUTPUT_1": Terminals.FUSED_24V,
            "PSU_OUTPUT_2": Terminals.GND,
        },
    )

    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Power distribution system saved to: {Paths.POWER_DISTRIBUTION}")
    print(f"  Used terminals: {used_terminals}")


if __name__ == "__main__":
    main()
