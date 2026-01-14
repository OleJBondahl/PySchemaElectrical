"""
Example: All Standard Circuits.

This example demonstrates all available standard circuits from the library,
creating each one and rendering them to individual SVG files.
"""

from pathlib import Path
from pyschemaelectrical import (
    create_autonumberer,
    render_system,
    std_circuits
)
from constants import Terminals, Pins, Paths


def create_all_examples():
    """
    Create all standard circuit examples and save them to individual SVG files.
    
    This demonstrates the complete library of standard circuits available.
    """
    
    # Create output directory
    output_dir = Path(Paths.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("Creating All Standard Circuit Examples")
    print("=" * 80)
    
    # 1. DOL Starter
    print("\n[1/8] DOL Motor Starter")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.dol_starter(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.MAIN_POWER,
        tm_bot=Terminals.MOTOR_1,
        tm_aux_1=Terminals.FUSED_24V,
        tm_aux_2=Terminals.GND
    )
    render_system(circuit, Paths.DOL_STARTER)
    print(f"✓ Saved: {Paths.DOL_STARTER}")
    print(f"  Terminals: {terminals}")
    
    # 2. Emergency Stop
    print("\n[2/8] Emergency Stop Circuit")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.emergency_stop(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.FUSED_24V,
        tm_bot=Terminals.EM_STOP
    )
    render_system(circuit, Paths.EMERGENCY_STOP)
    print(f"✓ Saved: {Paths.EMERGENCY_STOP}")
    print(f"  Terminals: {terminals}")
    
    # 3. PSU
    print("\n[3/8] Power Supply Unit")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.psu(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.AC_INPUT,
        tm_bot_left=Terminals.FUSED_24V,
        tm_bot_right=Terminals.GND,
        tm_top_pins=(Pins.L, Pins.N),
        tm_bot_left_pins=(Pins.V24_PLUS,),
        tm_bot_right_pins=(Pins.GND,)
    )
    render_system(circuit, Paths.PSU)
    print(f"✓ Saved: {Paths.PSU}")
    print(f"  Terminals: {terminals}")
    
    # 4. Changeover
    print("\n[4/8] Changeover Switch")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.changeover(
        state=state,
        x=0,
        y=0,
        tm_top_left=Terminals.MAIN_SUPPLY,
        tm_top_right=Terminals.EMERGENCY_SUPPLY,
        tm_bot=Terminals.CHANGEOVER_OUTPUT
    )
    render_system(circuit, Paths.CHANGEOVER)
    print(f"✓ Saved: {Paths.CHANGEOVER}")
    print(f"  Terminals: {terminals}")
    
    # 5. Voltage Monitor
    print("\n[5/8] Voltage Monitor")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.coil(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.VOLTAGE_MONITOR,
        tm_top_pins=Pins.VM_INPUT[:2]
    )
    render_system(circuit, Paths.VOLTAGE_MONITOR)
    print(f"✓ Saved: {Paths.VOLTAGE_MONITOR}")
    print(f"  Terminals: {terminals}")
    
    # 6. Power Distribution (Combined system)
    print("\n[6/8] Power Distribution System")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.power_distribution(
        state=state,
        x=0,
        y=0,
        terminal_maps={
            'INPUT_1': Terminals.MAIN_SUPPLY,
            'INPUT_2': Terminals.EMERGENCY_SUPPLY,
            'OUTPUT': Terminals.CHANGEOVER_OUTPUT,
            'PSU_INPUT': Terminals.AC_INPUT,
            'PSU_OUTPUT_1': Terminals.FUSED_24V,
            'PSU_OUTPUT_2': Terminals.GND
        }
    )
    render_system(circuit, Paths.POWER_DISTRIBUTION)
    print(f"✓ Saved: {Paths.POWER_DISTRIBUTION}")
    print(f"  Terminals: {terminals}")
    
    # 7. Motor Control
    print("\n[7/8] Motor Control Circuit")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.spdt(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.EM_STOP,
        tm_bot_left=Terminals.LIGHTS_SWITCHES,
        tm_bot_right=Terminals.LIGHTS_SWITCHES
    )
    render_system(circuit, Paths.MOTOR_CONTROL)
    print(f"✓ Saved: {Paths.MOTOR_CONTROL}")
    print(f"  Terminals: {terminals}")
    
    # 8. Switch
    print("\n[8/8] Simple Switch Circuit")
    print("-" * 40)
    state = create_autonumberer()
    state, circuit, terminals = std_circuits.no_contact(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.FUSED_24V,
        tm_bot=Terminals.GND
    )
    render_system(circuit, Paths.SWITCH)
    print(f"✓ Saved: {Paths.SWITCH}")
    print(f"  Terminals: {terminals}")
    
    # Summary
    print("\n" + "=" * 80)
    print("All Examples Complete!")
    print("=" * 80)
    print(f"\nOutput directory: {Paths.OUTPUT_DIR}")
    print("\nGenerated files:")
    print(f"  1. {Paths.DOL_STARTER}")
    print(f"  2. {Paths.EMERGENCY_STOP}")
    print(f"  3. {Paths.PSU}")
    print(f"  4. {Paths.CHANGEOVER}")
    print(f"  5. {Paths.VOLTAGE_MONITOR}")
    print(f"  6. {Paths.POWER_DISTRIBUTION}")
    print(f"  7. {Paths.MOTOR_CONTROL}")
    print(f"  8. {Paths.SWITCH}")
    print()


if __name__ == "__main__":
    create_all_examples()
