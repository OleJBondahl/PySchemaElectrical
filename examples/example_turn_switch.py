"""
Example: Turn Switch Circuit.

This example demonstrates how to create a turn switch circuit using the
CircuitBuilder API with the turn_switch_assembly_symbol.
"""

from pathlib import Path
from pyschemaelectrical import create_autonumberer, render_system
from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.symbols.assemblies import turn_switch_assembly_symbol
from .constants import Terminals, Paths


def main():
    """
    Create a turn switch circuit example.

    Demonstrates:
    - Using the turn switch assembly symbol with CircuitBuilder
    - Creating a simple manual control circuit
    - CircuitBuilder.add_component() with turn_switch_assembly_symbol
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path(Paths.TURN_SWITCH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build circuit using CircuitBuilder
    print("Creating turn switch circuit...")
    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=150, symbol_spacing=50)

    # 1. Input Terminal
    builder.add_terminal(Terminals.FUSED_24V, poles=1)

    # 2. Turn Switch Assembly (NO contact + turn switch actuator)
    builder.add_component(
        turn_switch_assembly_symbol, tag_prefix="S", poles=1, pins=("13", "14")
    )

    # 3. Output Terminal
    builder.add_terminal(Terminals.GND, poles=1)

    # Build the circuit
    result = builder.build()

    # Render to SVG
    render_system(result.circuit, str(output_path))
    print(f"✓ Turn switch circuit saved to: {output_path}")
    print(f"  Used terminals: {result.used_terminals}")


if __name__ == "__main__":
    main()
