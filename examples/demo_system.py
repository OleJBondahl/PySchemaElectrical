import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from iec_lib.core import Point, Symbol
from iec_lib.library.breakers import three_pole_circuit_breaker
from iec_lib.library.protection import three_pole_thermal_overload
from iec_lib.library.terminals import three_pole_terminal
from iec_lib.library.assemblies import contactor
from iec_lib.renderer import render_to_svg
from iec_lib.layout import auto_connect, auto_connect_labeled
from iec_lib.transform import translate
from iec_lib.autonumbering import (
    create_autonumberer,
    next_tag,
    next_terminal_pins,
    auto_contact_pins,
    auto_thermal_pins,
    auto_coil_pins
)
from typing import List, Tuple, Dict


def create_motor_circuit(
    state: Dict[str, int],
    x_position: float,
    y_start: float,
    normal_spacing: float,
    tight_spacing: float
) -> Tuple[Dict[str, int], List[Symbol]]:
    """
    Create a complete motor protection circuit with autonumbered components.
    
    This function creates a vertical chain of:
    - Top terminal (X1) - tag stays the same, pins auto-increment
    - Circuit breaker (F) - tag auto-increments
    - Thermal overload (F) - tag auto-increments
    - Contactor (Q) - tag auto-increments
    - Bottom terminal (X2) - tag stays the same, pins auto-increment
    
    Terminal tags remain constant (X1, X2) across all circuits, but their
    pin numbers increment sequentially (1-6, 7-12, 13-18, etc.).
    Other components get new tag numbers for each circuit.
    
    Args:
        state: Current autonumbering state.
        x_position: Horizontal position for the circuit.
        y_start: Starting vertical position.
        normal_spacing: Standard spacing between components.
        tight_spacing: Tight spacing (e.g., between breaker and thermal).
        
    Returns:
        Tuple containing updated state and list of placed symbols/lines.
    """
    all_elements = []
    current_y = y_start
    
    # Generate auto-incrementing tags for F and Q components
    state, f1_tag = next_tag(state, "F")
    state, f2_tag = next_tag(state, "F")
    state, q_tag = next_tag(state, "Q")
    
    # Generate auto-incrementing pins for terminals (ONCE per circuit, shared by X1 and X2)
    state, terminal_pins = next_terminal_pins(state, poles=3)
    
    # Create components
    # Terminals: Fixed tags (X1, X2) with the SAME pins in both
    top_terminals = three_pole_terminal(
        label="X1",  # Always X1
        pins=terminal_pins  # Same pins for top and bottom: (1,2,3), then (4,5,6), etc.
    )
    
    circuit_breaker = three_pole_circuit_breaker(
        label=f1_tag,  # Auto-increment: F1, F2, F3, etc.
        pins=auto_contact_pins()
    )
    
    thermal_overload = three_pole_thermal_overload(
        label=f2_tag,  # Auto-increment: F2, F3, F4, etc.
        pins=auto_thermal_pins()
    )
    
    contactor_asm = contactor(
        label=q_tag,  # Auto-increment: Q1, Q2, Q3, etc.
        coil_pins=auto_coil_pins(),
        contact_pins=auto_contact_pins()
    )
    
    bot_terminals = three_pole_terminal(
        label="X2",  # Always X2
        pins=terminal_pins  # Same pins as X1: (1,2,3), then (4,5,6), etc.
    )
    
    # Place components vertically
    # 1. Top terminals
    top_placed = translate(top_terminals, x_position, current_y)
    all_elements.append(top_placed)
    current_y += normal_spacing
    
    # 2. Circuit breaker
    f1_placed = translate(circuit_breaker, x_position, current_y)
    all_elements.append(f1_placed)
    current_y += tight_spacing
    
    # 3. Thermal overload (tight spacing from breaker)
    f2_placed = translate(thermal_overload, x_position, current_y)
    all_elements.append(f2_placed)
    current_y += normal_spacing
    
    # 4. Contactor
    q_placed = translate(contactor_asm, x_position, current_y)
    all_elements.append(q_placed)
    current_y += normal_spacing
    
    # 5. Bottom terminals
    bot_placed = translate(bot_terminals, x_position, current_y)
    all_elements.append(bot_placed)
    
    # Define wire specifications for each connection
    # Wire specs: port_id -> (color, size)
    # Note: For three-pole symbols, downward-facing ports are IDs 2, 4, 6
    wire_specs_input = {
        "2": ("RD", "2.5mm²"),    # L1 - Red, 2.5mm²
        "4": ("BK", "2.5mm²"),    # L2 - Black, 2.5mm²
        "6": ("BN", "2.5mm²")     # L3 - Brown, 2.5mm²
    }
    
    wire_specs_output = {
        "2": ("RD", "1.5mm²"),    # U1 - Red, 1.5mm²
        "4": ("BK", "1.5mm²"),    # U2 - Black, 1.5mm²
        "6": ("BN", "1.5mm²")     # U3 - Brown, 1.5mm²
    }
    
    # Auto-connect all components with labeled wires
    # Input side (from terminals through breaker and thermal to contactor)
    all_elements.extend(auto_connect_labeled(top_placed, f1_placed, wire_specs_input))
    all_elements.extend(auto_connect_labeled(f1_placed, f2_placed, wire_specs_input))
    all_elements.extend(auto_connect_labeled(f2_placed, q_placed, wire_specs_input))
    
    # Output side (from contactor to bottom terminals)
    all_elements.extend(auto_connect_labeled(q_placed, bot_placed, wire_specs_output))
    
    return state, all_elements


def main():
    """
    Generate a system drawing with multiple motor circuits side by side.
    
    This demonstrates the autonumbering system's ability to create
    multiple identical subcircuits with automatically incremented tags.
    """
    print("Generating System Drawing with Autonumbering...")
    
    from iec_lib.constants import GRID_SIZE
    
    # Define layout parameters
    start_x = 50
    start_y = 50
    circuit_spacing = 15 * GRID_SIZE  # 100mm between circuits
    normal_spacing = 10 * GRID_SIZE   # 25mm - normal spacing between components
    tight_spacing = 4 * GRID_SIZE     # 10mm - tight spacing between F1 and F2
    
    # Configure number of circuits to create
    num_circuits = 3
    
    # Initialize autonumbering state
    state = create_autonumberer()
    all_elements = []
    
    # Create multiple circuits side by side
    for i in range(num_circuits):
        x_pos = start_x + (i * circuit_spacing)
        state, circuit_elements = create_motor_circuit(
            state=state,
            x_position=x_pos,
            y_start=start_y,
            normal_spacing=normal_spacing,
            tight_spacing=tight_spacing
        )
        all_elements.extend(circuit_elements)
        print(f"Created circuit {i+1} at x={x_pos}")
    
    # Render to SVG
    output_file = "demo_system.svg"
    render_to_svg(all_elements, output_file, width="297mm", height="297mm")  # Wide format for 3 circuits
    print(f"Saved to {os.path.abspath(output_file)}")
    print(f"Total circuits created: {num_circuits}")


if __name__ == "__main__":
    main()
