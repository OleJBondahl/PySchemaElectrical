"""Debug script to test auto_connect_labeled"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyschemaelectrical.symbols.terminals import three_pole_terminal
from pyschemaelectrical.symbols.breakers import three_pole_circuit_breaker
from pyschemaelectrical.autonumbering import next_terminal_pins, auto_contact_pins, create_autonumberer
from pyschemaelectrical.transform import translate
from pyschemaelectrical.layout import auto_connect_labeled
from pyschemaelectrical.renderer import render_to_svg

# Create a simple circuit
state = create_autonumberer()
state, terminal_pins = next_terminal_pins(state, poles=3)

top_terminals = three_pole_terminal(label="X1", pins=terminal_pins)
circuit_breaker = three_pole_circuit_breaker(label="F1", pins=auto_contact_pins())

# Place them
top_placed = translate(top_terminals, 50, 50)
f1_placed = translate(circuit_breaker, 50, 100)

wire_specs = {
    "2": ("RD", "2.5mmÂ²"),
    "4": ("BK", "2.5mmÂ²"),
    "6": ("BN", "2.5mmÂ²")
}

print("Calling auto_connect_labeled...")
connections = auto_connect_labeled(top_placed, f1_placed, wire_specs)

print(f"\nNumber of connection elements: {len(connections)}")
for i, elem in enumerate(connections):
    print(f"Element {i}: {type(elem).__name__}")
    if hasattr(elem, 'content'):
        print(f"  Content: '{elem.content}'")
        print(f"  Position: {elem.position}")
    if hasattr(elem, 'start'):
        print(f"  Start: {elem.start}, End: {elem.end}")

# Render
all_elements = [top_placed, f1_placed] + connections
render_to_svg(all_elements, "test_labeled_connection.svg", width="200mm", height="200mm")
print("\nSaved to test_labeled_connection.svg")
