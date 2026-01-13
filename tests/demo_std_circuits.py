import os
from pyschemaelectrical.autonumbering import create_autonumberer
from pyschemaelectrical import std_circuits, render_system, CircuitBuilder
from pyschemaelectrical.constants import Terminals

def main():
    state = create_autonumberer()
    
    # 1. Motor Circuit
    print("Generating Motor Circuit...")
    state, motor_circuit, _ = std_circuits.motor.create_dol_starter(
        state, x=0, y=0, count=2
    )
    render_system(motor_circuit, "demo_motor.svg")
    print("Saved demo_motor.svg")

    # 2. PSU Circuit
    print("Generating PSU Circuit...")
    state, psu_circuit, _ = std_circuits.power.create_psu(
        state, x=0, y=600  # Offset vertical
    )
    render_system(psu_circuit, "demo_psu.svg")
    print("Saved demo_psu.svg")
    
    # 3. Changeover Circuit
    print("Generating Changeover Circuit...")
    state, changeover_circuit, _ = std_circuits.power.create_changeover(
        state, x=500, y=600 
    )
    render_system(changeover_circuit, "demo_changeover.svg")
    print("Saved demo_changeover.svg")

if __name__ == "__main__":
    main()
