"""
Example: All Standard Circuits.

This example runs all other example scripts to generate the full set of
demonstration SVGs.
"""

# Import main functions from all example scripts
from .example_changeover import main as changeover_main
from .example_dol_starter import main as dol_main
from .example_dynamic_block import main as dynamic_block_main
from .example_emergency_stop import main as estop_main
from .example_motor_control import main as motor_control_main
from .example_motor_symbol import main as motor_symbol_main
from .example_pin_configurations import main as pin_configs_main
from .example_power_distribution import main as power_dist_main
from .example_psu import main as psu_main
from .example_switch import main as switch_main
from .example_turn_switch import main as turn_switch_main
from .example_voltage_monitor import main as voltage_monitor_main
from .example_wire_labels import main as wire_labels_main


def create_all_examples():
    """Run all example scripts."""
    print("=" * 80)
    print("Running All Example Scripts")
    print("=" * 80)

    print("\n--- 1. DOL Starter Examples ---")
    dol_main()

    print("\n--- 2. Emergency Stop Example ---")
    estop_main()

    print("\n--- 3. PSU Example ---")
    psu_main()

    print("\n--- 4. Changeover Example ---")
    changeover_main()

    print("\n--- 5. Voltage Monitor Example ---")
    voltage_monitor_main()

    print("\n--- 6. Power Distribution Example ---")
    power_dist_main()

    print("\n--- 7. Motor Control Example ---")
    motor_control_main()

    print("\n--- 8. Switch Example ---")
    switch_main()

    print("\n--- 9. Turn Switch Example ---")
    turn_switch_main()

    print("\n--- 10. Wire Labels Example ---")
    wire_labels_main()

    print("\n--- 11. Dynamic Block Example ---")
    dynamic_block_main()

    print("\n--- 12. Pin Configurations Examples ---")
    pin_configs_main()

    print("\n--- 13. Motor Symbol Test ---")
    motor_symbol_main()

    print("\n" + "=" * 80)
    print("All Examples Complete!")
    print("=" * 80)


if __name__ == "__main__":
    create_all_examples()
