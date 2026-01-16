"""
Example: Dynamic Block with Non-Uniform Pin Spacing.

This example demonstrates the new explicit pin positioning feature
for dynamic blocks, which is useful for PSU shared output blocks and
other scenarios where pins don't align with uniform spacing.
"""

from .constants import Paths
from pyschemaelectrical import create_autonumberer, Circuit, render_system, add_symbol
from pyschemaelectrical.symbols import dynamic_block_symbol
from pyschemaelectrical.utils.autonumbering import next_tag


def main():
    """
    Create an example circuit demonstrating non-uniform pin spacing.

    Demonstrates:
    - Explicit pin positions (non-uniform spacing)
    - Backward compatibility with uniform spacing
    - Combining different spacing patterns in top/bottom pins
    """

    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    from pathlib import Path

    output_dir = Path(Paths.DYNAMIC_BLOCK).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "example_dynamic_block_nonuniform.svg"

    print("Creating dynamic block example with non-uniform spacing...")

    # Create circuit
    circuit = Circuit()

    # Example 1: Backward compatible - uniform spacing (existing behavior)
    state, tag1 = next_tag(state, "U")
    block1 = dynamic_block_symbol(
        label=tag1,
        top_pins=("L", "N", "PE"),
        bottom_pins=("24V", "GND"),
        pin_spacing=10.0,  # Traditional uniform spacing
    )
    add_symbol(circuit, block1, 0, 0)

    # Example 2: Non-uniform spacing - simulating 2 PSUs at 40mm spacing
    # PSU1 outputs at x=0 (24V) and x=10 (GND)
    # PSU2 outputs at x=40 (24V) and x=50 (GND)
    state, tag2 = next_tag(state, "U")
    block2 = dynamic_block_symbol(
        label=tag2,
        top_pins=("+1", "-1", "+2", "-2"),
        top_pin_positions=(0.0, 10.0, 40.0, 50.0),  # Explicit positions
    )
    add_symbol(circuit, block2, 80, 0)

    # Example 3: Mixed - explicit top positions, uniform bottom spacing
    state, tag3 = next_tag(state, "U")
    block3 = dynamic_block_symbol(
        label=tag3,
        top_pins=("A", "B", "C"),
        top_pin_positions=(0.0, 15.0, 45.0),  # Non-uniform top
        bottom_pins=("1", "2", "3"),
        # bottom uses uniform spacing (pin_spacing) by default
        pin_spacing=5.0,
    )
    add_symbol(circuit, block3, 160, 0)

    # Example 4: Both explicit
    state, tag4 = next_tag(state, "U")
    block4 = dynamic_block_symbol(
        label=tag4,
        top_pins=("IN1", "IN2", "IN3"),
        top_pin_positions=(0.0, 20.0, 30.0),
        bottom_pins=("OUT1", "OUT2"),
        bottom_pin_positions=(5.0, 25.0),
    )
    add_symbol(circuit, block4, 230, 0)

    # Render the circuit
    render_system(circuit, str(output_path))

    print(f"✓ Non-uniform dynamic block example saved to: {output_path}")
    print(f"  Example 1 ({tag1}): Backward compatible uniform spacing")
    print(f"  Example 2 ({tag2}): Non-uniform top pins (PSU-style)")
    print(f"  Example 3 ({tag3}): Mixed explicit/uniform")
    print(f"  Example 4 ({tag4}): Fully explicit positioning")


if __name__ == "__main__":
    main()
