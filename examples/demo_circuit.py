import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import Point, Symbol
from src.symbols import (
    terminal, 
    normally_open, 
    normally_closed,
    three_pole_normally_open, 
    thermal_overload, 
    three_pole_thermal_overload,
    fuse,
    coil
)
from src.renderer import render_to_svg
from src.transform import translate
# from src.parts import text_element, standard_style # Removed invalid import

from src.layout import layout_vertical_chain 

def main():
    print("Generating comprehensive symbol demo...")
    
    all_elements = []

    # --- 1. Auto-Connect Demo (Motor Starter Chain) ---
    print("Generating Auto-Connected Circuit...")
    t1 = terminal("X1", pins=("L1",))
    f1 = thermal_overload("-F1", pins=("95", "96"))
    k1 = normally_closed("-S1", pins=("1", "2")) # Stop
    k2 = normally_open("-S2", pins=("3", "4")) # Start
    k3 = coil("-K1", pins=("A1", "A2"))
    t2 = terminal("X2", pins=("N",))
    
    chain_layout = layout_vertical_chain(
        symbols=[t1, f1, k1, k2, k3, t2],
        start=Point(40, 40),
        spacing=35.0
    )
    all_elements.extend(chain_layout)
    
    # Text label for the circuit
    # Using a dummy text element logic or just relying on symbol labels.
    
    # --- 2. Symbol Showcase (Grid) ---
    print("Generating Symbol Showcase...")
    
    # List of (Description, Factory Function, Kwargs)
    showcase_items = [
        ("Terminal", terminal, {"label": "X1", "pins": ("1",)}),
        ("NO Contact", normally_open, {"label": "-K1", "pins": ("13", "14")}),
        ("NC Contact", normally_closed, {"label": "-K2", "pins": ("21", "22")}),
        ("Thermal Overload", thermal_overload, {"label": "-F1", "pins": ("95", "96")}),
        ("Fuse", fuse, {"label": "-F2", "pins": ("1", "2")}),
        ("Coil", coil, {"label": "-K3", "pins": ("A1", "A2")}),
        ("3-Pole NO", three_pole_normally_open, {"label": "-K4", "pins": ("1", "2", "3", "4", "5", "6")}),
        ("3-Pole Thermal", three_pole_thermal_overload, {"label": "-F3", "pins": ("1", "2", "3", "4", "5", "6")}),
    ]
    
    start_x = 150 # Move to the right of the chain
    start_y = 50
    row_height = 80
    col_width = 80
    
    cols = 4
    
    for i, (desc, func, kwargs) in enumerate(showcase_items):
        row = i // cols
        col = i % cols
        
        x = start_x + col * col_width
        y = start_y + row * row_height
        
        # Create symbol
        sym = func(**kwargs)
        
        # Translate symbol to position
        placed_sym = translate(sym, x, y)
        
        all_elements.append(placed_sym)
        print(f"Added {desc} at ({x}, {y})")

    output_file = "iec_demo.svg"
    # Adjust canvas size
    render_to_svg(all_elements, output_file, width="297mm", height="210mm") # A4 Landscape
    print(f"Saved to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
