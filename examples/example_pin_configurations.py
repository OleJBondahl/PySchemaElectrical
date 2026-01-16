"""
DOL Starter Pin Configuration Examples

This example demonstrates three different ways to use the create_dol_starter function:
1. Default behavior (auto-numbering)
2. Passing project autonumber state (sharing state across circuits)
3. Setting specific terminal and symbol pin numbers
"""

from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.std_circuits import dol_starter
from pyschemaelectrical.system.system import render_system


def main():
    # Example 1: Default Behavior (Auto-numbering)
    # ==================================================
    # Terminals are auto-numbered, symbols use default pins
    print("=" * 80)
    print("Example 1: Default Behavior (Auto-numbering)")
    print("=" * 80)

    state1 = create_autonumberer()
    state1, circuit1, terminals1 = dol_starter(
        state=state1, x=0, y=0, tm_top="X1", tm_bot="X10", tm_bot_right="PE"
    )

    render_system(circuit1, "examples/output/dol_pins_example1_auto.svg")
    print("✓ Auto-numbered DOL starter saved")
    print(f"  Used terminals: {terminals1}")
    print()

    # Example 2: Passing Project Autonumber (Shared State)
    # ==================================================
    # Create a shared autonumber state and use it across multiple circuits
    print("=" * 80)
    print("Example 2: Passing Project Autonumber (Shared State)")
    print("=" * 80)

    # Create a shared project autonumber state
    project_state = create_autonumberer()

    # First circuit
    project_state, circuit2a, terminals2a = dol_starter(
        state=project_state,  # Pass shared state
        x=0,
        y=0,
        tm_top="X1",
        tm_bot="X10",
        tm_bot_right="PE",
    )

    # Second circuit - continues numbering from where first circuit left off
    project_state, circuit2b, terminals2b = dol_starter(
        state=project_state,  # Same state object - continues numbering
        x=80,
        y=0,
        tm_top="X1",  # Same terminal ID but will get next available pins
        tm_bot="X10",
        tm_bot_right="PE",
    )

    # Combine circuits
    combined_circuit = circuit2a
    combined_circuit.elements.extend(circuit2b.elements)

    render_system(
        combined_circuit, "examples/output/dol_pins_example2_shared_state.svg"
    )
    print("✓ Two DOL starters with shared autonumbering saved")
    print(f"  First circuit terminals: {terminals2a}")
    print(f"  Second circuit terminals: {terminals2b}")
    print("  Notice how X1 pins continue: 1,2,3 then 4,5,6")
    print()

    # Example 3: Setting Specific Pin Numbers
    # ==================================================
    # Override both terminal pins and symbol pins with custom values
    print("=" * 80)
    print("Example 3: Setting Specific Terminal and Symbol Pin Numbers")
    print("=" * 80)

    state3 = create_autonumberer()
    state3, circuit3, terminals3 = dol_starter(
        state=state3,
        x=0,
        y=0,
        tm_top="X1",
        tm_bot="X10",
        tm_bot_right="PE",
        # Custom terminal pins (instead of auto-numbering)
        tm_top_pins=("L1", "L2", "L3"),
        tm_bot_pins=("U", "V", "W"),
        # Custom symbol pins
        breaker_pins=("1L1", "2T1", "3L2", "4T2", "5L3", "6T3"),
        thermal_pins=("", "", "", "", "", ""),  # Hide all pins
        contactor_pins=("A1", "A2", "13", "14", "21", "22"),
        ct_pins=("S1", "S2", "K", "L"),
    )

    render_system(circuit3, "examples/output/dol_pins_example3_custom_pins.svg")
    print("✓ DOL starter with custom pins saved")
    print(f"  Used terminals: {terminals3}")
    print("  Input terminal pins: L1, L2, L3 (instead of auto 1,2,3)")
    print("  Output terminal pins: U, V, W (instead of auto 1,2,3)")
    print("  Circuit breaker pins: Custom IEC nomenclature")
    print("  Thermal overload pins: All hidden")
    print("  Contactor pins: Using NO/NC notation")
    print("  CT pins: Custom S1, S2, K, L labels")
    print()

    # Example 4: Mixed Approach
    # ==================================================
    # Auto-number terminals, but customize symbol pins
    print("=" * 80)
    print("Example 4: Mixed Approach (Auto terminals, Custom symbol pins)")
    print("=" * 80)

    state4 = create_autonumberer()
    state4, circuit4, terminals4 = dol_starter(
        state=state4,
        x=0,
        y=0,
        tm_top="X1",
        tm_bot="X10",
        tm_bot_right="PE",
        # Leave terminal pins as None (auto-number)
        tm_top_pins=None,
        tm_bot_pins=None,
        # But customize some symbol pins
        thermal_pins=("", "T1", "", "T2", "", "T3"),
        ct_pins=("CT1+", "CT1-", "CT2+", "CT2-"),
    )

    render_system(circuit4, "examples/output/dol_pins_example4_mixed.svg")
    print("✓ DOL starter with mixed approach saved")
    print(f"  Used terminals: {terminals4}")
    print("  Terminal pins: Auto-numbered (default)")
    print("  Symbol pins: Partially customized")
    print()

    print("=" * 80)
    print("All Examples Complete!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  1. examples/output/dol_pins_example1_auto.svg - Default auto-numbering")
    print(
        "  2. examples/output/dol_pins_example2_shared_state.svg - Shared state across circuits"
    )
    print("  3. examples/output/dol_pins_example3_custom_pins.svg - Fully custom pins")
    print("  4. examples/output/dol_pins_example4_mixed.svg - Mixed approach")


if __name__ == "__main__":
    main()
