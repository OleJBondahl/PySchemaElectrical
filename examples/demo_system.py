import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import Point, Symbol, Element
from src.symbols.breakers import three_pole_circuit_breaker
from src.symbols.protection import three_pole_thermal_overload
from src.symbols.terminals import three_pole_terminal, terminal
from src.symbols.contacts import normally_open, spdt_contact
from src.symbols.coils import coil
from src.symbols.assemblies import contactor
from src.symbols.circuits import motor_circuit
from src.renderer import render_to_svg
from src.layout import auto_connect, auto_connect_labeled
from src.transform import translate, rotate
from src.constants import GRID_SIZE
from src.autonumbering import (
    create_autonumberer,
    next_tag,
    next_terminal_pins,
    auto_contact_pins,
    auto_thermal_pins,
    auto_coil_pins
)
from typing import List, Tuple, Dict
from functools import partial
from src.system import layout_horizontal





def create_control_circuit(
    x_position: float,
    y_start: float,
    spacing: float
) -> List[Symbol]:
    """
    Create a detailed motor control circuit (single pole).
    Contains: Terminal X10 -> NO Contact -> SPDT Contact.
    SPDT NC -> Coil -> Terminal X11.
    SPDT NO -> Terminal X12.
    """
    elements = []
    current_y = y_start
    
    # 1. Terminal X10
    t1 = translate(terminal("X10", pins=("1",)), x_position, current_y)
    elements.append(t1)
    current_y += spacing
    
    # 2. NO Contact (Start Button)
    # Using 'S1' as generic tag
    no_sw = translate(normally_open("S1", pins=("13", "14")), x_position, current_y)
    elements.append(no_sw)
    current_y += spacing
    
    # 3. SPDT Contact
    # Rotate 180 to have input (Common) at top.
    # Unrotated: Common=Bottom Right (+2.5), NC=Top Left (-2.5), NO=Top Right (+2.5). -- Wait, looking at contacts.py
    # contacts.py: Common=(x_right, h_half)=+2.5, +5. NO=(x_right, -h)=+2.5, -5. NC=(x_left, -h)=-2.5, -5.
    # Rotated 180: Common=(-2.5, -5) [Top Left relative to center]. 
    #              NO=(-2.5, +5)     [Bottom Left relative to center].
    #              NC=(+2.5, +5)     [Bottom Right relative to center].
    #
    # To align Common (-2.5) with S1 (0), we shift S2 center right by +2.5.
    shift_x = GRID_SIZE / 2
    s2_sym = rotate(spdt_contact("S2", pins=("11", "12", "14")), 180)
    
    # S2 center is at x_position + shift_x
    s2_y = current_y
    s2 = translate(s2_sym, x_position + shift_x, s2_y)
    elements.append(s2)
    current_y += spacing
    
    # Branch alignments relative to x_position:
    # Common Input: (x_pos + 2.5) - 2.5 = x_pos. (Aligned!)
    # NO Output:    (x_pos + 2.5) - 2.5 = x_pos. (Straight down)
    # NC Output:    (x_pos + 2.5) + 2.5 = x_pos + 5.0 (Right branch)
    
    # 4. Coil (NC path - Right side)
    # Connected to SPDT NC output (at x_pos + 5.0 = x_pos + GRID_SIZE)
    # Using 'K1' as generic tag for Contactor Coil
    k1 = translate(coil("K1", pins=("A1", "A2")), x_position + GRID_SIZE, current_y)
    elements.append(k1)
    
    current_y += spacing
    
    # 5. Terminal X11 (NC path end - Right side)
    # Connected after Coil (at x_pos + GRID_SIZE)
    t_nc_end = translate(terminal("X11", pins=("1",)), x_position + GRID_SIZE, current_y)
    elements.append(t_nc_end)
    
    # 6. Terminal X12 (NO path end - Center)
    # Connected to SPDT NO output. (at x_pos)
    # User requested small vertical gap underneath S2.
    # S2 is at s2_y. NO pin is at s2_y + 2.5.
    # Let's place X12 at s2_y + 4 * GRID_SIZE (10.0). Gap = 7.5mm.
    t_no_end = translate(terminal("X12", pins=("1",)), x_position, s2_y + 4 * GRID_SIZE)
    elements.append(t_no_end)
    
    # Connections
    elements.extend(auto_connect(t1, no_sw))
    
    # NO Switch to S2 Common
    # S2 Common is now physically at x_position (due to shift).
    elements.extend(auto_connect(no_sw, s2))
    
    # SPDT NC (Right) -> Coil
    elements.extend(auto_connect(s2, k1))
    
    # Coil -> X11
    elements.extend(auto_connect(k1, t_nc_end))
    
    # SPDT NO (Center) -> X12
    # This connects S2 NO output (at x_pos) to X12.
    elements.extend(auto_connect(s2, t_no_end))
    
    return elements


def main():
    """
    Generate a system drawing with multiple motor circuits side by side.
    
    This demonstrates the autonumbering system's ability to create
    multiple identical subcircuits with automatically incremented tags.
    """
    print("Generating System Drawing with Autonumbering...")
    
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
    
    # Define wire Label configurations per component prefix
    input_wires = [ ("RD", "2.5mm²"), ("BK", "2.5mm²"), ("BN", "2.5mm²") ]
    internal_wires = [ ("RD", "2.5mm²"), ("BK", "2.5mm²"), ("BN", "2.5mm²") ]
    output_wires = [ ("RD", "1.5mm²"), ("BK", "1.5mm²"), ("BN", "1.5mm²") ]
    
    config = {
        "X1": input_wires,     # Wires FROM X1
        "FT": internal_wires,  # Wires FROM Thermal Overload (FT...)
        "Q": output_wires      # Wires FROM Contactor (Q...)
    }
    
    # Create multiple circuits side by side
    # Create specific generator function for this layout
    # We use partial to bind static arguments, but x_position comes from layout_horizontal
    # We need to wrap it because layout_horizontal expects (state, x, y) -> (state, elems)
    # but motor_circuit takes more args.
    
    def generator(st, x, y):
        return motor_circuit(
            state=st,
            x_position=x,
            y_start=y,
            normal_spacing=normal_spacing,
            tight_spacing=tight_spacing,
            wire_config=config
        )

    # Use functional layout helper
    state, circuit_elements = layout_horizontal(
        start_state=state,
        start_x=start_x,
        start_y=start_y,
        spacing=circuit_spacing,
        count=num_circuits,
        generate_func=generator
    )
    all_elements.extend(circuit_elements)
    print(f"Created {num_circuits} circuits side by side.")
    
    # Render to SVG
    output_file = "demo_system.svg"
    render_to_svg(all_elements, output_file, width="297mm", height="297mm")  # Wide format for 3 circuits
    print(f"Saved to {os.path.abspath(output_file)}")
    print(f"Total circuits created: {num_circuits}")
    
    # Export system to CSV
    from src.system_analysis import export_terminals_to_csv
    csv_file = "demo_system.csv"
    export_terminals_to_csv(all_elements, csv_file)
    print(f"Exported terminals to {os.path.abspath(csv_file)}")

    # Generate Motor Control Circuit
    print("\nGenerating Motor Control Circuit...")
    control_elements = create_control_circuit(start_x, start_y, normal_spacing)
    
    control_file = "motor_control.svg"
    # Use a narrower width for the single circuit
    render_to_svg(control_elements, control_file, width="100mm", height="297mm")
    print(f"Saved to {os.path.abspath(control_file)}")


if __name__ == "__main__":
    main()
