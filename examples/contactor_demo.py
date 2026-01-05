import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from iec_lib.core import Point
from iec_lib.library.assemblies import contactor
from iec_lib.renderer import render_to_svg
from iec_lib.layout import layout_vertical_chain

def main():
    print("Generating Contactor Demo Circuit...")
    
    # Create the contactor symbol
    # This combines the coil and the 3 power contacts
    k1 = contactor(
        label="-K1", 
        coil_pins=("A1", "A2"),
        contact_pins=("1", "2", "3", "4", "5", "6")
    )
    
    # We can just place it manually or use layout
    # Since we only have one main component for this demo, let's just place it.
    # But layout_vertical_chain expects a list.
    # Let's verify it renders correctly on its own.
    
    # Place it at (100, 100) to have space for the coil on the left
    from iec_lib.transform import translate
    k1_placed = translate(k1, 100, 100)
    
    circuit_elements = k1_placed.elements
    
    output_file = "contactor_demo.svg"
    # Using A4 size
    render_to_svg(circuit_elements, output_file, width="210mm", height="297mm")
    print(f"Saved to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
