"""
Demo for dynamic_block symbol with custom pin labels.

This example demonstrates a dynamic block with:
- 3 top pins labeled: L, N, PE
- 2 bottom pins labeled: 24V, GND
"""
from pyschemaelectrical.system import Circuit, add_symbol, render_system
from pyschemaelectrical.symbols.blocks import dynamic_block, psu
import os


def main():
    """Create and render a dynamic block demo."""
    print("Creating dynamic_block demo...")
    
    # Ensure output directory exists
    os.makedirs("examples/output", exist_ok=True)
    
    # Create a circuit
    circuit = Circuit()
    
    # Create a PSU symbol
    # This automatically includes the diagonal, AC/DC text, and correct pins
    block = psu(label="U1")
    
    # Add the block to the circuit at position (50, 50)
    add_symbol(circuit, block, 50, 50)
    
    # Render the circuit
    output_path = "examples/output/dynamic_block_demo.svg"
    render_system(circuit, output_path)
    
    print(f"✓ Demo complete! SVG saved to: {output_path}")


if __name__ == "__main__":
    main()
