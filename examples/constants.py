"""
Project-Specific Constants for Examples.

This module defines constants that vary from project to project:
- Terminal IDs
- Pin numbers
- Tag prefixes (when different from library defaults)

Layout constants (grid, spacing) are handled by the library's model.constants module.
"""


# =============================================================================
# Terminal Identifiers
# =============================================================================
class Terminals:
    """Terminal block identifiers used in this project."""

    # Power Terminals (3-phase)
    MAIN_POWER = "X1"  # Main incoming power
    MOTOR_1 = "X10"  # Motor 1 output
    MOTOR_2 = "X11"  # Motor 2 output
    MOTOR_3 = "X12"  # Motor 3 output

    # Power Supply Terminals
    AC_INPUT = "X2"  # AC input for PSU
    FUSED_24V = "X3"  # 24V DC output
    GND = "X4"  # Ground/0V

    # Changeover Terminals
    MAIN_SUPPLY = "X5"  # Main power supply input
    EMERGENCY_SUPPLY = "X6"  # Emergency power supply input
    CHANGEOVER_OUTPUT = "X7"  # Changeover output

    # Control Terminals
    EM_STOP = "X20"  # Emergency stop circuit
    LIGHTS_SWITCHES = "X21"  # Lights and switches output
    VOLTAGE_MONITOR = "X22"  # Voltage monitoring input
    VOLTAGE_MONITOR_OUTPUT = "X23"  # Voltage monitoring output

    # Dynamic Block Terminals
    DB_INPUT_1 = "X30"
    DB_INPUT_2 = "X31"
    DB_INPUT_3 = "X32"
    DB_INPUT_4 = "X33"
    DB_INPUT_5 = "X34"

    # Ground/PE
    PE = "PE"


# =============================================================================
# Pin Configurations
# =============================================================================
class Pins:
    """Pin numbers/labels used in this project."""

    # Power pins
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"

    # AC power
    L = "L"
    N = "N"
    PE = "PE"

    # DC power
    V24_PLUS = "1"  # 24V positive
    GND = "2"  # Ground/0V

    # Voltage monitor
    VM_INPUT = ("L1", "L2", "L3")
    VM_OUTPUT = ("11", "12", "14")


# =============================================================================
# Tag Prefixes (Override library defaults if needed)
# =============================================================================
class Tags:
    """
    Component tag prefixes.
    Only define here if overriding library defaults from StandardTags.
    """

    # Example custom tags (if needed)
    # CUSTOM_BREAKER = "FB"  # Custom breaker prefix

    pass  # Use library defaults from pyschemaelectrical.model.constants.StandardTags


# =============================================================================
# File Paths
# =============================================================================
class Paths:
    """Output paths for generated files."""

    OUTPUT_DIR = "examples/output"

    # Individual circuit outputs
    DOL_STARTER = f"{OUTPUT_DIR}/dol_starter.svg"
    EMERGENCY_STOP = f"{OUTPUT_DIR}/emergency_stop.svg"
    PSU = f"{OUTPUT_DIR}/psu.svg"
    CHANGEOVER = f"{OUTPUT_DIR}/changeover.svg"
    VOLTAGE_MONITOR = f"{OUTPUT_DIR}/voltage_monitor.svg"
    POWER_DISTRIBUTION = f"{OUTPUT_DIR}/power_distribution.svg"
    MOTOR_CONTROL = f"{OUTPUT_DIR}/motor_control.svg"
    SWITCH = f"{OUTPUT_DIR}/switch.svg"
    TURN_SWITCH = f"{OUTPUT_DIR}/turn_switch.svg"
    DYNAMIC_BLOCK = f"{OUTPUT_DIR}/dynamic_block_5_terminals.svg"
    WIRE_LABELS = f"{OUTPUT_DIR}/wire_labels.svg"
    TWO_COILS = f"{OUTPUT_DIR}/two_coils.svg"
    THREE_PHASE_MOTOR = f"{OUTPUT_DIR}/three_phase_motor.svg"

    # Combined examples
    ALL_CIRCUITS = f"{OUTPUT_DIR}/all_circuits.svg"
