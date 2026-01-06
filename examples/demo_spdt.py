import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.symbols.contacts import spdt_contact
from src.renderer import render_to_svg
from src.transform import translate, rotate
from src.constants import GRID_SIZE

def main():
    print("Generating SPDT Demo...")
    
    elements = []
    
    # 1. Standard SPDT
    s1 = translate(spdt_contact("S1", pins=("11", "12", "14")), 50, 50)
    elements.extend(s1.elements) # Flatten for simple rendering if needed, or keep as symbol
    # render_to_svg expects list of Elements (or Symbols which it likely handles or we need to extract elements)
    # Checking render_to_svg implementation or usage in demo_system.py:
    # in demo_system.py:
    # elements.append(t1) -> t1 is Symbol.
    # auto_connect returns [Line, Line...] -> extended.
    # render_to_svg(all_elements...)
    # So we should pass Symbols directly if render_to_svg handles them, OR extend their elements.
    # Let's check demo_system.py usage: 
    # elements.append(t1) 
    # ...
    # render_to_svg(all_elements, ...)
    # It seems render_to_svg handles Symbols or we should append the symbol itself to the list.
    # Wait, in demo_system.py:
    # state, circuit_elements = motor_circuit(...)
    # all_elements.extend(circuit_elements)
    # Let's look at render_to_svg signature if possible, or just assume it takes list of objects.
    # Actually, in demo_system.py: elements.append(t1) works. so [Symbol] is fine.
    
    elements = [s1]

    # 2. Rotated SPDT (180 deg) - like in motor control
    s2_sym = rotate(spdt_contact("S2", pins=("21", "22", "24")), 180)
    s2 = translate(s2_sym, 100, 50)
    elements.append(s2)
    
    # 3. No Labels
    s3 = translate(spdt_contact("", pins=()), 150, 50)
    elements.append(s3)

    output_file = "demo_spdt.svg"
    render_to_svg(elements, output_file, width="200mm", height="100mm")
    print(f"Saved to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
