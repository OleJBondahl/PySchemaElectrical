from pyschemaelectrical.system import Circuit, add_symbol, render_system
from pyschemaelectrical.symbols import three_pole_spdt
import os

def main():
    print("Creating three_pole_spdt demo...")
    os.makedirs("examples/output", exist_ok=True)
    
    circuit = Circuit()
    
    # Create symbol with default pins
    # Default pins in function: ("11", "12", "14", "21", "22", "24", "31", "32", "34")
    sym1 = three_pole_spdt(label="-K1")
    
    print("Symbol 1 Ports:", list(sym1.ports.keys()))
    
    add_symbol(circuit, sym1, 50, 50)
    
    # Create symbol with custom pins (just repeating default for demo)
    custom_pins = ("11", "12", "14", "21", "22", "24", "31", "32", "34")
    sym2 = three_pole_spdt(label="-K2", pins=custom_pins)
    
    print("Symbol 2 Ports:", list(sym2.ports.keys()))
    
    # Moved to 140 to account for wider symbol (spacing 20mm * 2 = 40mm width approx)
    add_symbol(circuit, sym2, 140, 50)
    
    output_path = "examples/output/three_pole_spdt_demo.svg"
    render_system(circuit, output_path)
    print(f"File saved to {output_path}")

if __name__ == "__main__":
    main()
