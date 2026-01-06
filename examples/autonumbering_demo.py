"""
Example demonstrating the updated autonumbering system with terminal pins.

This script shows how terminals maintain constant tags (X1, X2) across
circuits while their pin numbers auto-increment sequentially.
"""

import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.autonumbering import (
    create_autonumberer,
    next_tag,
    next_terminal_pins,
    get_pin_counter
)


def main():
    """Demonstrate terminal pin autonumbering."""
    
    print("=== Terminal Pin Autonumbering Demo ===\n")
    
    # Create autonumbering state
    state = create_autonumberer()
    print("1. Initialize autonumbering state")
    print(f"   State: {state}\n")
    
    # Simulate creating 3 identical circuits
    print("2. Create 3 motor circuits with consistent terminal tags:\n")
    
    for circuit_num in range(1, 4):
        print(f"   Circuit {circuit_num}:")
        
        # Components with auto-incrementing tags
        state, f1 = next_tag(state, "F")
        state, f2 = next_tag(state, "F")
        state, q1 = next_tag(state, "Q")
        
        # Terminals with fixed tags but auto-incrementing pins
        state, x1_pins = next_terminal_pins(state, poles=3)
        state, x2_pins = next_terminal_pins(state, poles=3)
        
        print(f"     Top Terminal:    X1 (pins: {', '.join(x1_pins)})")
        print(f"     Breaker:         {f1}")
        print(f"     Thermal:         {f2}")
        print(f"     Contactor:       {q1}")
        print(f"     Bottom Terminal: X2 (pins: {', '.join(x2_pins)})")
        print()
    
    print(f"   Final pin counter: {get_pin_counter(state)}")
    print(f"   Final state: {state}\n")
    
    print("3. Key observations:")
    print("   - Terminal TAGS stay the same (X1, X2) in each circuit")
    print("   - Terminal PINS increment sequentially across circuits")
    print("   - Other component tags (F, Q) increment normally")
    print("   - This allows consistent terminal naming with unique pin numbers\n")
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()
