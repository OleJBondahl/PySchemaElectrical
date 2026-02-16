"""
Example: Dynamic Block with 5 Pins Connected to 5 Single Pole Terminals.

This example demonstrates how to use the library's dynamic block symbol
to create a custom block with 5 pins and connect each pin
to a separate single pole terminal.
"""

from pyschemaelectrical import Circuit, add_symbol, create_autonumberer, render_system
from pyschemaelectrical.model.constants import DEFAULT_POLE_SPACING
from pyschemaelectrical.symbols import dynamic_block_symbol, terminal_symbol
from pyschemaelectrical.system.connection_registry import register_connection
from pyschemaelectrical.utils.autonumbering import next_tag

from .constants import Paths, Terminals


def main():
    """
    Create an example circuit with a dynamic block connected to 5 single pole terminals.

    Demonstrates:
    - Library dynamic block symbol with 5 pins
    - 5 separate single pole terminals
    - Connections between each pin and its corresponding terminal
    """

    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    from pathlib import Path

    output_path = Path(Paths.DYNAMIC_BLOCK)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Creating dynamic block example with 5 terminals...")

    # Create circuit
    circuit = Circuit()

    # Create 5 single pole terminals at the top
    # Terminals will be spaced horizontally
    terminal_y = 0
    terminal_tags = [
        Terminals.DB_INPUT_1,
        Terminals.DB_INPUT_2,
        Terminals.DB_INPUT_3,
        Terminals.DB_INPUT_4,
        Terminals.DB_INPUT_5,
    ]

    placed_terminals = []
    for i, term_tag in enumerate(terminal_tags):
        x_pos = i * DEFAULT_POLE_SPACING

        term = terminal_symbol(term_tag, pins=(str(i + 1),), label_pos="left")
        placed_term = add_symbol(circuit, term, x_pos, terminal_y)
        placed_terminals.append(placed_term)

    # Create dynamic block below the terminals
    # We want pin 1 at x=0 (under X1), pin 2 at x=5 (under X2), etc.
    # The library dynamic_block_symbol places the first pin at the insertion origin.
    # So we place the block at x=0.
    block_x = 0
    block_y = 50  # Below terminals

    state, block_tag = next_tag(state, "DB")

    # Use the library symbol. We want 5 pins on top.
    block = dynamic_block_symbol(block_tag, top_pins=("1", "2", "3", "4", "5"))
    block_placed = add_symbol(circuit, block, block_x, block_y)

    # Register connections for terminal list
    # Each terminal's bottom port (port "2") connects to corresponding block pin
    for i in range(5):
        terminal_tag = terminal_tags[i]
        block_pin = str(i + 1)
        state = register_connection(
            state, terminal_tag, "2", block_tag, block_pin, side="bottom"
        )

    # Explicitly connect each terminal to the block
    # This is necessary because auto_connect_circuit connects sequentially,
    # but we have a many-to-one relationship (5 terminals -> 1 block)
    from pyschemaelectrical.layout.layout import auto_connect

    for term in placed_terminals:
        lines = auto_connect(term, block_placed)
        circuit.elements.extend(lines)

    # Render the circuit
    render_system(circuit, str(output_path))

    print(f"✓ Dynamic block example saved to: {output_path}")
    print(f"  Block tag: {block_tag}")
    print(f"  Terminal tags: {terminal_tags}")
    print("  Connections:")
    for i in range(5):
        print(f"    {terminal_tags[i]}:2 -> {block_tag}:{i + 1}")


if __name__ == "__main__":
    main()
