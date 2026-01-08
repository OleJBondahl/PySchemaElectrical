from pyschemaelectrical.system import Circuit, add_symbol, auto_connect_circuit, render_system
from pyschemaelectrical.symbols.terminals import terminal
from pyschemaelectrical.symbols.contacts import normally_open
from pyschemaelectrical.symbols.coils import coil
import os

def main():
    print("Testing New Helper API...")
    
    # Ensure output directory exists
    os.makedirs("examples/output", exist_ok=True)
    
    # Create a circuit
    c = Circuit()
    
    # Add symbols
    # X1 at 50, 50
    add_symbol(c, terminal("X1"), 50, 50)
    
    # S1 at 50, 100
    add_symbol(c, normally_open("S1"), 50, 100)
    
    # K1 at 50, 150
    add_symbol(c, coil("K1"), 50, 150)
    
    # X2 at 50, 200
    add_symbol(c, terminal("X2"), 50, 200)
    
    # Auto connect
    auto_connect_circuit(c)
    
    # Render
    output_path = "examples/output/new_api_demo.svg"
    render_system(c, output_path)
    print(f"Done! Saved to {output_path}")

if __name__ == "__main__":
    main()
