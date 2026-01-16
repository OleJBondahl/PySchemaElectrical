"""
Example: Motor Symbol.

This example tests the motor symbol connected to a 3-pole terminal
and a single PE terminal using the CircuitBuilder.
"""

from pathlib import Path
from pyschemaelectrical import (
    create_autonumberer,
    render_system,
    CircuitBuilder,
)
from pyschemaelectrical.symbols import (
    three_pole_motor_symbol,
)
from pyschemaelectrical.model.constants import DEFAULT_POLE_SPACING


def main():
    """
    Create an example circuit with a motor and terminals using CircuitBuilder.
    """
    print("\nCreating three-phase motor example...")

    # Initialize state
    state = create_autonumberer()

    # Create output directory
    output_dir = Path("examples/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Builder
    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0)

    # 1. Terminals (Row 1)

    # X1: 3-Pole Terminal (Pins 1, 2, 3)
    # y_increment=0 so PE stays on same row
    # X1: 3-Pole Terminal (Pins 1, 2, 3)
    # y_increment=0 so PE stays on same row
    # Capture index for connection
    _, idx_x1 = builder.add_terminal(
        tm_id="X1",
        poles=3,
        pins=("1", "2", "3"),
        label_pos="left",
        y_increment=0,
        auto_connect_next=False,
    )

    # PE: 1-Pole Terminal (Pin 1)
    # x_offset shifts it right
    # y_increment=50 moves down for the motor
    _, idx_pe = builder.add_terminal(
        tm_id="PE",
        poles=1,
        pins=("1",),
        label_pos="left",
        x_offset=3 * DEFAULT_POLE_SPACING,
        y_increment=50,
        auto_connect_next=False,
    )

    # 2. Motor (Row 2)
    # x_offset=DEFAULT_POLE_SPACING aligns Center(V) with X1:2
    _, idx_motor = builder.add_component(
        three_pole_motor_symbol,
        tag_prefix="-M",
        pins=("U", "V", "W", "PE"),
        x_offset=DEFAULT_POLE_SPACING,
    )

    # 3. Connections
    # X1 -> Motor
    for i in range(3):
        builder.add_connection(idx_x1, i, idx_motor, i)

    # PE -> Motor (Pole 3 = 4th pin usually, but PE is 4th pin in input tuple)
    # Motor pins: U(0), V(1), W(2), PE(3)
    builder.add_connection(idx_pe, 0, idx_motor, 3)

    # Build & Render
    result = builder.build()

    output_path = output_dir / "motor_symbol_test.svg"
    render_system(result.circuit, str(output_path))
    print(f"✓ Motor symbol test saved to: {output_path}")


if __name__ == "__main__":
    main()
