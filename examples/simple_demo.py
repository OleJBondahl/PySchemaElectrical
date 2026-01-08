"""
Simple Demo - PySchemaElectrical Simple API

This example demonstrates the simplified API for creating electrical schematics.
It creates a basic motor control circuit using minimal code.
"""

# Note: When running this, ensure the package is installed or add the src to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from pyschemaelectrical.simple_api import Circuit, Terminal, Contact, Coil, Assembly

def main():
    """Create a simple motor control circuit using the high-level API."""
    
    print("Creating simple motor control circuit...")
    
    # Create a new circuit with default settings
    circuit = Circuit()
    
    # Add components - they are automatically positioned and connected!
    circuit.add(Terminal("X10"))
    circuit.add(Assembly.emergency_stop("S0"))
    circuit.add(Contact.NO("S1"))
    circuit.add(Coil("K1"))
    circuit.add(Terminal("X11"))
    
    # Render to SVG
    output_file = "examples/output/simple_demo.svg"
    circuit.render(output_file, width="100mm", height="297mm")
    
    print(f"✓ Saved to {os.path.abspath(output_file)}")
    print(f"✓ Total components: 5")
    print("\nCompare this simple code to the complex demo_system.py!")
    print("Simple API: ~10 lines of code")
    print("Traditional API: ~50+ lines for similar circuit")


def demo_three_pole_circuit():
    """Create a three-pole motor circuit using the simple API."""
    
    print("\nCreating three-pole motor circuit...")
    
    circuit = Circuit(spacing=40)  # Tighter spacing for 3-pole components
    
    circuit.add(Terminal.three_pole("X1"))
    circuit.add(Breaker("Q1"))
    circuit.add(Protection("F1"))
    circuit.add(Terminal.three_pole("X2"))
    
    output_file = "examples/output/simple_motor.svg"
    circuit.render(output_file, width="297mm", height="210mm")
    
    print(f"✓ Saved to {os.path.abspath(output_file)}")


if __name__ == "__main__":
    main()
    
    # Uncomment to also generate the three-pole example
    # demo_three_pole_circuit()
