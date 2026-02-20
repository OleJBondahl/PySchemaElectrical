"""
Example: Declarative Circuit Definition with Descriptors.

Demonstrates the ref/comp/term descriptor syntax for defining linear
circuits without writing a builder function. Descriptors are lightweight
data objects that describe what to build, and build_from_descriptors()
assembles them into a full circuit.

Run with:
    python -m examples.example_descriptors
"""

from pyschemaelectrical.descriptors import build_from_descriptors, comp, ref, term
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.symbols.contacts import normally_open_symbol
from pyschemaelectrical.system.system import render_system
from pyschemaelectrical.utils.autonumbering import create_autonumberer


def main():
    """Build a simple relay circuit using descriptors."""

    print("=" * 60)
    print("PySchemaElectrical — Descriptor Example")
    print("=" * 60)

    state = create_autonumberer()

    # Define the circuit as a list of descriptors.
    # This is equivalent to using CircuitBuilder but more concise.
    descriptors = [
        ref("PLC:DO"),  # PLC digital output reference
        comp(normally_open_symbol, "S", pins=("13", "14")),  # NO contact
        comp(coil_symbol, "K", pins=("A1", "A2")),  # Relay coil
        term("X1"),  # Physical terminal
    ]

    # Build with count=2 to create two identical instances
    result = build_from_descriptors(
        state,
        descriptors,
        x=0,
        y=0,
        spacing=80,
        count=2,
    )

    # Access results
    print(f"\nGenerated tags: {result.component_map}")
    print(f"Used terminals: {result.used_terminals}")
    print(f"Terminal pins:  {result.terminal_pin_map}")
    print(f"Elements:       {len(result.circuit.elements)}")

    # Render to SVG
    render_system(result.circuit, "examples/output/descriptors.svg")
    print("\nSVG written to examples/output/descriptors.svg")


if __name__ == "__main__":
    main()
