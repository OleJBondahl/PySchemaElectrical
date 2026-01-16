"""
Standard Motor Circuits.

This module provides standard motor circuit configurations.
All terminal IDs, tags, and pins are parameters with sensible defaults.
Layout values use constants from model.constants but can be overridden.
"""

from typing import Any, List, Tuple, Optional

from pyschemaelectrical.system.system import Circuit, add_symbol, auto_connect_circuit
from pyschemaelectrical.symbols.assemblies import contactor_symbol
from pyschemaelectrical.symbols.breakers import three_pole_circuit_breaker_symbol
from pyschemaelectrical.symbols.protection import three_pole_thermal_overload_symbol
from pyschemaelectrical.symbols.transducers import current_transducer_assembly_symbol
from pyschemaelectrical.symbols.terminals import (
    three_pole_terminal_symbol,
    terminal_symbol,
)
from pyschemaelectrical.symbols.motors import three_pole_motor_symbol
from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins
from pyschemaelectrical.layout.layout import create_horizontal_layout, auto_connect
from pyschemaelectrical.model.constants import (
    LayoutDefaults,
    StandardTags,
    DEFAULT_POLE_SPACING,
)
from pyschemaelectrical.system.connection_registry import register_connection


def dol_starter(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameters
    tm_top: str,
    tm_bot: str,
    tm_bot_right: str,
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_MOTOR,
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_DEFAULT,
    # Component parameters (with defaults)
    breaker_tag_prefix: str = StandardTags.BREAKER,
    thermal_tag_prefix: str = "FT",
    contactor_tag_prefix: str = StandardTags.CONTACTOR,
    ct_tag_prefix: str = "CT",
    motor_tag_prefix: str = StandardTags.MOTOR,
    # Pin parameters for symbols (with defaults)
    breaker_pins: Tuple[str, str, str, str, str, str] = ("1", "2", "3", "4", "5", "6"),
    thermal_pins: Tuple[str, str, str, str, str, str] = ("", "T1", "", "T2", "", "T3"),
    contactor_pins: Tuple[str, str, str, str, str, str] = (
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
    ),
    ct_pins: Tuple[str, ...] = ("1", "2", "3", "4"),
    # Pin parameters for terminals (None = auto-number)
    tm_top_pins: Optional[Tuple[str, ...]] = None,
    tm_bot_pins: Optional[Tuple[str, ...]] = None,
    tm_bot_right_pins: Optional[Tuple[str, ...]] = None,
    # Optional aux terminals
    tm_aux_1: Optional[str] = None,
    tm_aux_2: Optional[str] = None,
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Create a Direct-On-Line (DOL) Motor Starter.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top: Top terminal ID (Input)
        tm_bot: Bottom terminal ID (Output)
        spacing: Horizontal spacing between circuit instances
        symbol_spacing: Vertical spacing between components
        breaker_tag_prefix: Tag prefix for circuit breaker (default: "F")
        thermal_tag_prefix: Tag prefix for thermal overload (default: "FT")
        contactor_tag_prefix: Tag prefix for contactor (default: "Q")
        ct_tag_prefix: Tag prefix for current transducer (default: "CT")
        breaker_pins: Pin labels for circuit breaker (default: ("1", "2", "3", "4", "5", "6"))
        thermal_pins: Pin labels for thermal overload (default: ("", "T1", "", "T2", "", "T3"))
        contactor_pins: Pin labels for contactor (default: ("1", "2", "3", "4", "5", "6"))
        ct_pins: Pin labels for current transducer (default: ("1", "2", "3", "4"))
        tm_top_pins: Pin labels for top terminal (None = auto-number)
        tm_bot_pins: Pin labels for bottom terminal (None = auto-number)
        tm_bot_right: Terminal ID for the single pole terminal at the bottom right (PE)
        tm_bot_right_pins: Pin labels for the bottom right terminal (None = auto-number)
        tm_aux_1: Optional terminal ID for 24V aux connection
        tm_aux_2: Optional terminal ID for GND aux connection

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    # Support legacy terminal_maps parameter
    terminal_maps = kwargs.get("terminal_maps") or {}
    if not tm_aux_1:
        tm_aux_1 = terminal_maps.get("FUSED_24V")
    if not tm_aux_2:
        tm_aux_2 = terminal_maps.get("GND")

    def create_single_dol(s, start_x, start_y, tag_gens, t_maps, instance):
        """Create a single DOL starter instance."""
        c = Circuit()
        current_y = start_y
        used_terminals_list = [tm_top, tm_bot, tm_bot_right]

        # Get terminal pins (auto-number if not provided)
        if tm_top_pins is None:
            s, input_pins = next_terminal_pins(s, tm_top, 3)
        else:
            input_pins = tm_top_pins

        if tm_bot_pins is None:
            s, output_pins = next_terminal_pins(s, tm_bot, 3)
        else:
            output_pins = tm_bot_pins

        if tm_bot_right_pins is None:
            s, output_right_pins = next_terminal_pins(s, tm_bot_right, 1)
        else:
            output_right_pins = tm_bot_right_pins

        # Get component tags
        s, breaker_tag = next_tag(s, breaker_tag_prefix)
        s, thermal_tag = next_tag(s, thermal_tag_prefix)
        s, cont_tag = next_tag(s, contactor_tag_prefix)
        s, ct_tag = next_tag(s, ct_tag_prefix)
        s, motor_tag = next_tag(s, motor_tag_prefix)

        # 1. Input Terminal
        sym = three_pole_terminal_symbol(tm_top, pins=input_pins, label_pos="left")
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing

        # 2. Circuit Breaker
        sym = three_pole_circuit_breaker_symbol(breaker_tag, pins=breaker_pins)
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing / 2  # Half spacing to thermal overload

        # 3. Thermal Overload (top pins hidden)
        sym = three_pole_thermal_overload_symbol(thermal_tag, pins=thermal_pins)
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing

        # 4. Contactor
        sym = contactor_symbol(cont_tag, contact_pins=contactor_pins)
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing

        # 5. Current Transducer (inline with connection)
        sym = current_transducer_assembly_symbol(ct_tag, pins=ct_pins)
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing

        # 6. Output Terminal
        sym = three_pole_terminal_symbol(tm_bot, pins=output_pins, label_pos="left")
        tm_bot_sym = add_symbol(c, sym, start_x, current_y)

        # 6b. PE Terminal (tm_bot_right) - same Y level
        sym = terminal_symbol(tm_bot_right, pins=output_right_pins, label_pos="right")
        add_symbol(c, sym, start_x + 3 * DEFAULT_POLE_SPACING, current_y)

        # 7. Motor - Below terminals
        current_y += symbol_spacing
        motor_pins = ("U", "V", "W", "PE")
        sym = three_pole_motor_symbol(motor_tag, pins=motor_pins)
        motor_sym = add_symbol(c, sym, start_x + DEFAULT_POLE_SPACING, current_y)

        # Connect all symbols sequentially
        auto_connect_circuit(c)

        # Manually connect Main Terminals -> Motor (because PE terminal breaks sequential chain)
        c.elements.extend(auto_connect(tm_bot_sym, motor_sym))

        # --- Explicit Registry Registration ---
        # 1. Top Terminal (Output Side/Bottom) -> Circuit Breaker (Input Side/Top)
        # input_pins: sequential pins from next_terminal_pins, e.g. ("1", "2", "3")
        # breaker pins: [1, 2, 3, 4, 5, 6] -> Inputs: 1, 3, 5 (indices 0, 2, 4)
        for i in range(3):
            # Terminal pins are sequential: input_pins[0], input_pins[1], input_pins[2]
            if i < len(input_pins):
                term_pin = input_pins[i]

                # Breaker input pins are at indices 0, 2, 4 (pins "1", "3", "5")
                brk_pin_idx = i * 2
                if brk_pin_idx < len(breaker_pins):
                    brk_pin = breaker_pins[brk_pin_idx]

                    s = register_connection(
                        s, tm_top, term_pin, breaker_tag, brk_pin, side="bottom"
                    )

        # 2. Contactor (Output Side/Bottom) -> Bottom Terminal (Input Side/Top)
        # output_pins: sequential pins from next_terminal_pins, e.g. ("4", "5", "6")
        # contactor pins: [1, 2, 3, 4, 5, 6] -> Outputs: 2, 4, 6 (indices 1, 3, 5)
        # Note: CT is inline but we register contactor to terminal for clarity
        for i in range(3):
            # Terminal pins are sequential: output_pins[0], output_pins[1], output_pins[2]
            if i < len(output_pins):
                term_pin = output_pins[i]

                # Contactor output pins are at indices 1, 3, 5 (pins "2", "4", "6")
                cont_pin_idx = (i * 2) + 1
                if cont_pin_idx < len(contactor_pins):
                    cont_pin = contactor_pins[cont_pin_idx]
                    s = register_connection(
                        s, tm_bot, term_pin, cont_tag, cont_pin, side="top"
                    )

        # 3. Bottom Terminal (Output Side/Bottom) -> Motor (Input Side/Top)
        # Motor: U, V, W
        # Connect tm_bot (1, 2, 3) to Motor (U, V, W)
        for i, motor_pin in enumerate(["U", "V", "W"]):
            if i < len(output_pins):
                term_pin = output_pins[i]
                s = register_connection(
                    s, tm_bot, term_pin, motor_tag, motor_pin, side="bottom"
                )

        # 4. PE Terminal -> Motor PE
        if len(output_right_pins) > 0:
            pe_pin = output_right_pins[0]
            s = register_connection(
                s, tm_bot_right, pe_pin, motor_tag, "PE", side="bottom"
            )

        return s, c.elements

    # Use horizontal layout for multiple instances
    count = kwargs.get("count", 1)
    final_state, all_elements = create_horizontal_layout(
        state=state,
        start_x=x,
        start_y=y,
        count=count,
        spacing=spacing,
        generator_func_single=create_single_dol,
        default_tag_generators={},
        tag_generators=kwargs.get("tag_generators"),
        terminal_maps=terminal_maps,
    )

    circuit = Circuit(elements=all_elements)
    used_terminals = [tm_top, tm_bot, tm_bot_right]

    return final_state, circuit, used_terminals
