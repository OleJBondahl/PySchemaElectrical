"""
Example: Wire Labels.

This example demonstrates how to add wire labels (color, size) to circuit connections.
"""

from pathlib import Path
from pyschemaelectrical import create_autonumberer, std_circuits, render_system
from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit
from .constants import Terminals


def main():
    """
    Create a circuit example with wire labels.
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path("examples/output/wire_labels.svg")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Creating circuit with wire labels...")

    # Create a simple circuit (e.g. DOL starter)
    # The dol_starter function creates a direct-on-line motor starter circuit
    state, circuit, _ = std_circuits.dol_starter(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.MAIN_POWER,
        tm_bot=Terminals.MOTOR_1,
        tm_aux_1=Terminals.FUSED_24V,
        tm_aux_2=Terminals.GND,
    )

    # Define labels for the wires
    # Note: add_wire_labels_to_circuit applies labels to vertical wires found in the circuit.
    # The order depends on the internal creation order of lines in the circuit.
    # For a DOL starter, we expect main power lines and control lines.
    # We provide a list of labels to be applied cyclically if there are more wires than labels.
    labels = ["L1 2.5mm²", "L2 2.5mm²", "L3 2.5mm²", "RD 0.75mm²", "BK 0.75mm²"]

    # Add wire labels to the circuit
    add_wire_labels_to_circuit(circuit, labels)

    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Circuit with wire labels saved to: {output_path}")


if __name__ == "__main__":
    main()
