import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyschemaelectrical.core import Point
from pyschemaelectrical.symbols.contacts import three_pole_normally_open, three_pole_normally_closed
from pyschemaelectrical.symbols.protection import three_pole_thermal_overload
from pyschemaelectrical.symbols.terminals import three_pole_terminal
from pyschemaelectrical.renderer import render_to_svg
from pyschemaelectrical.layout import layout_vertical_chain

def main():
    print("Generating Three Pole Demo Circuit...")
    
    # 1. Terminals (Top)
    # Using L1, L2, L3 input.
    # Pins: Input/Output pairs? 
    # Usually terminals have 1 connection point physically, but here we model flow.
    # If "1, 2" are pairs, we can name them "L1_in", "L1_out"? 
    # Or just "L1", "L1'"?
    # Let's use simple numbers 1-6 for the flow.
    top_terminals = three_pole_terminal(label="X1", pins=("1", "2", "3", "4", "5", "6"))
    
    # 2. NO Contacts (Main Contactor)
    # 1-2, 3-4, 5-6
    # Note: If we use 1-6 here, and 1-6 above, it's fine, labels don't clash for connectivity, 
    # but visuals might duplicate pin numbers.
    # Let's use standard marking. 1/L1 - 2/T1.
    k1 = three_pole_normally_open(label="-K1", pins=("1", "2", "3", "4", "5", "6"))
    
    # 3. NC Contacts
    # Maybe a safety contactor?
    # 21-22 is usually control.
    # But for power, maybe we just show it.
    k2 = three_pole_normally_closed(label="-K2", pins=("11", "12", "13", "14", "15", "16"))
    
    # 4. Thermal Protection
    f1 = three_pole_thermal_overload(label="-F1", pins=("1", "2", "3", "4", "5", "6"))
    
    # 5. Terminals (Bottom)
    bot_terminals = three_pole_terminal(label="X2", pins=("U", "V", "W", "X", "Y", "Z"))
    
    # Layout
    # All auto-connected in a vertical chain
    circuit_elements = layout_vertical_chain(
        symbols=[top_terminals, k1, k2, f1, bot_terminals],
        start=Point(50, 50),
        spacing=40.0
    )
    
    output_file = "three_pole_demo.svg"
    render_to_svg(circuit_elements, output_file, width="210mm", height="297mm")
    print(f"Saved to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
