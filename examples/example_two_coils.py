"""
Example: Two Coils with Shared Terminal and Horizontal Connection.

This example demonstrates how to use the low-level API to create a custom
circuit with two coils side by side, connected horizontally at the A1 pins,
with a shared input terminal above and individual output terminals below.
"""

from pathlib import Path

from pyschemaelectrical import Circuit, add_symbol, create_autonumberer, render_system
from pyschemaelectrical.layout.layout import auto_connect
from pyschemaelectrical.model.parts import standard_style
from pyschemaelectrical.model.primitives import Line
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.symbols.terminals import terminal_symbol
from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins

from .constants import Paths, Terminals

COIL_SPACING = 20.0  # Horizontal distance between coil centers
SYMBOL_SPACING = 50.0  # Vertical distance between component rows


def main():
    """
    Create a two-coil circuit example.

    Layout:
        [Terminal]
            |
        [Coil 1] --- [Coil 2]   (A1 pins connected horizontally)
            |              |
        [Terminal]   [Terminal]
    """
    state = create_autonumberer()

    output_path = Path(Paths.TWO_COILS)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Creating two-coil circuit...")

    circuit = Circuit()

    # Positions
    x_left = 0.0
    x_right = x_left + COIL_SPACING
    y_top_terminal = 0.0
    y_coils = y_top_terminal + SYMBOL_SPACING
    y_bot_terminals = y_coils + SYMBOL_SPACING

    # Get terminal pins
    state, top_pins = next_terminal_pins(state, Terminals.FUSED_24V, 1)
    state, bot_left_pins = next_terminal_pins(state, Terminals.GND, 1)
    state, bot_right_pins = next_terminal_pins(state, Terminals.GND, 1)

    # Get coil tags
    state, coil1_tag = next_tag(state, "K")
    state, coil2_tag = next_tag(state, "K")

    # 1. Top terminal (above left coil A1)
    sym = terminal_symbol(Terminals.FUSED_24V, pins=top_pins, label_pos="left")
    top_term = add_symbol(circuit, sym, x_left, y_top_terminal)

    # 2. Left coil
    sym = coil_symbol(coil1_tag, pins=("A1", "A2"))
    coil1 = add_symbol(circuit, sym, x_left, y_coils)

    # 3. Right coil
    sym = coil_symbol(coil2_tag, pins=("A1", "A2"))
    coil2 = add_symbol(circuit, sym, x_right, y_coils)

    # 4. Bottom left terminal (under left coil A2)
    sym = terminal_symbol(Terminals.GND, pins=bot_left_pins, label_pos="left")
    bot_left_term = add_symbol(circuit, sym, x_left, y_bot_terminals)

    # 5. Bottom right terminal (under right coil A2)
    sym = terminal_symbol(Terminals.GND, pins=bot_right_pins, label_pos="left")
    bot_right_term = add_symbol(circuit, sym, x_right, y_bot_terminals)

    # --- Connections ---

    # Vertical: top terminal -> left coil A1
    circuit.elements.extend(auto_connect(top_term, coil1))

    # Vertical: left coil A2 -> bottom left terminal
    circuit.elements.extend(auto_connect(coil1, bot_left_term))

    # Vertical: right coil A2 -> bottom right terminal
    circuit.elements.extend(auto_connect(coil2, bot_right_term))

    # Horizontal: left coil A1 -> right coil A1
    a1_left = coil1.ports["A1"].position
    a1_right = coil2.ports["A1"].position
    circuit.elements.append(Line(a1_left, a1_right, standard_style()))

    # Render
    render_system(circuit, str(output_path))
    print(f"  Saved to: {output_path}")
    print(f"  Coils: {coil1_tag}, {coil2_tag}")


if __name__ == "__main__":
    main()
