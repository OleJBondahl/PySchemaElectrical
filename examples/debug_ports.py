"""Debug script to check port IDs"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from iec_lib.library.terminals import three_pole_terminal
from iec_lib.library.breakers import three_pole_circuit_breaker
from iec_lib.autonumbering import next_terminal_pins, auto_contact_pins, create_autonumberer

# Create a simple circuit
state = create_autonumberer()
state, terminal_pins = next_terminal_pins(state, poles=3)

top_terminals = three_pole_terminal(label="X1", pins=terminal_pins)
circuit_breaker = three_pole_circuit_breaker(label="F1", pins=auto_contact_pins())

print("Top Terminal Ports:")
for port_id, port in top_terminals.ports.items():
    print(f"  ID: {port_id}, Direction: {port.direction}, Position: {port.position}")

print("\nCircuit Breaker Ports:")
for port_id, port in circuit_breaker.ports.items():
    print(f"  ID: {port_id}, Direction: {port.direction}, Position: {port.position}")
