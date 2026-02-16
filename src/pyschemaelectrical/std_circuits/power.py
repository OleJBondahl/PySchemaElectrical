"""
Standard Power Circuits.

This module provides standard power circuit configurations.
All terminal IDs, tags, and pins are parameters with sensible defaults.
Layout values use constants from model.constants but can be overridden.
"""

from typing import Any, Dict, List, Optional, Tuple

from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.model.constants import (
    DEFAULT_POLE_SPACING,
    GRID_SIZE,
    LayoutDefaults,
    StandardTags,
)
from pyschemaelectrical.symbols.blocks import psu_symbol
from pyschemaelectrical.symbols.breakers import two_pole_circuit_breaker_symbol
from pyschemaelectrical.symbols.contacts import multi_pole_spdt_symbol, three_pole_spdt_symbol
from pyschemaelectrical.system.system import Circuit
from pyschemaelectrical.utils.autonumbering import next_terminal_pins

from .control import coil


def psu(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameters
    tm_top: str,
    tm_bot_left: str,
    tm_bot_right: str,
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_POWER,
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_STANDARD,
    # Kept for back-compat but ignored
    terminal_offset: float = LayoutDefaults.PSU_TERMINAL_OFFSET,
    # Component parameters (with defaults)
    tag_prefix: str = StandardTags.POWER_SUPPLY,
    # Multi-count and wire labels
    count: int = 1,
    wire_labels: Optional[List[str]] = None,
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a standardized PSU block circuit using CircuitBuilder.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top: Terminal ID for AC input (Input 1/Input 2)
        tm_bot_left: Terminal ID for Output 1 (e.g. 24V)
        tm_bot_right: Terminal ID for Output 2 (e.g. GND)
        spacing: Horizontal spacing between circuit instances
        symbol_spacing: Vertical spacing between components
        terminal_offset: Horizontal offset (Ignored)
        tag_prefix: Tag prefix for PSU component (default: "G")
        count: Number of PSU instances.
        wire_labels: Wire label strings to apply per instance.

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    builder = CircuitBuilder(state)

    system_circuit = Circuit(elements=[])
    used_terminals = []

    # Iterate based on count
    current_x = x

    for _i in range(count):
        # Calculate pins for this iteration first (updates state counters)
        state, tm_top_pins = next_terminal_pins(state, tm_top, poles=3)
        state, tm_b_left_pins = next_terminal_pins(state, tm_bot_left, poles=1)
        state, tm_b_right_pins = next_terminal_pins(state, tm_bot_right, poles=1)

        # Initialize builder with the state containing updated counters
        builder = CircuitBuilder(state)
        builder.set_layout(current_x, y, spacing=spacing, symbol_spacing=symbol_spacing)

        # 1. Input Terminal (Top) - 3 Pole (L, N, PE)
        builder.add_terminal(
            tm_top,
            logical_name="INPUT",
            poles=3,
            pins=tm_top_pins,
            x_offset=0,
            y_increment=symbol_spacing,
            auto_connect_next=False,
        )

        # 2. Circuit Breaker (Middle Top)
        breaker_tag_prefix = kwargs.get("breaker_tag_prefix", StandardTags.BREAKER)

        builder.add_component(
            two_pole_circuit_breaker_symbol,
            tag_prefix=breaker_tag_prefix,
            y_increment=symbol_spacing,
            pins=("1", "2", "3", "4"),
            x_offset=0,
            auto_connect_next=False,
        )

        # 3. PSU Block (Middle Bottom)
        psu_pins = ("L", "N", "PE", "24V", "GND")
        builder.add_component(
            psu_symbol,
            tag_prefix=tag_prefix,
            y_increment=symbol_spacing,
            pins=psu_pins,
            auto_connect_next=False,
        )

        # 4. Output 1 Terminal (Bottom Left - 24V)
        builder.add_terminal(
            tm_bot_left,
            logical_name="OUTPUT_1",
            x_offset=0,
            y_increment=0,
            pins=tm_b_left_pins,
            auto_connect_next=False,
        )

        # 5. Output 2 Terminal (Bottom Right - GND)
        builder.add_terminal(
            tm_bot_right,
            logical_name="OUTPUT_2",
            x_offset=DEFAULT_POLE_SPACING,
            y_increment=symbol_spacing,
            pins=tm_b_right_pins,
            label_pos="right",
            auto_connect_next=False,
        )

        # Manual Connections
        # Components: 0=TM_IN, 1=BREAKER, 2=PSU, 3=TM_OUT1, 4=TM_OUT2
        builder.add_connection(0, 0, 1, 0, side_a="bottom", side_b="top")
        builder.add_connection(0, 1, 1, 2, side_a="bottom", side_b="top")
        builder.add_connection(0, 2, 2, 2, side_a="bottom", side_b="top")
        builder.add_connection(1, 1, 2, 0, side_a="bottom", side_b="top")
        builder.add_connection(1, 3, 2, 1, side_a="bottom", side_b="top")
        builder.add_connection(2, 3, 3, 0, side_a="bottom", side_b="top")
        builder.add_connection(2, 4, 4, 0, side_a="bottom", side_b="top")

        result = builder.build(count=1)

        state = result.state
        system_circuit.elements.extend(result.circuit.elements)
        used_terminals.extend(result.used_terminals)

        # Move X for next iteration
        current_x += spacing

    # Apply wire labels if provided
    if wire_labels is not None:
        from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

        system_circuit = add_wire_labels_to_circuit(system_circuit, wire_labels)

    return state, system_circuit, list(set(used_terminals))


def changeover(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameters
    tm_top_left: str,
    tm_top_right: str,
    tm_bot: str,
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_POWER,
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_STANDARD,
    terminal_offset: float = (LayoutDefaults.CHANGEOVER_TERMINAL_OFFSET),
    # Component parameters (with defaults)
    tag_prefix: str = StandardTags.RELAY,
    poles: int = 3,
    # Optional terminal pin tuples (auto-generated if not provided)
    tm_top_left_pins: Optional[tuple] = None,
    tm_top_right_pins: Optional[tuple] = None,
    tm_bot_pins: Optional[tuple] = None,
    # Multi-count and wire labels
    count: int = 1,
    wire_labels: Optional[List[str]] = None,
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a manual changeover switch circuit using single terminals.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top_left: First input terminal ID (e.g., main power)
        tm_top_right: Second input terminal ID (e.g., emergency power)
        tm_bot: Output terminal ID
        spacing: Horizontal spacing between circuit instances
        symbol_spacing: Vertical spacing between components
        terminal_offset: Horizontal offset for input
            terminals (plus/minus offset from center)
        tag_prefix: Tag prefix for changeover switch (default: "K")
        poles: Number of SPDT poles (default: 3)
        tm_top_left_pins: Optional tuple of pin numbers for top-left terminals.
        tm_top_right_pins: Optional tuple of pin numbers for top-right terminals.
        tm_bot_pins: Optional tuple of pin numbers for bottom terminals.
        count: Number of circuit instances.
        wire_labels: Wire label strings to apply per instance.

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    from pyschemaelectrical.layout.layout import auto_connect, create_horizontal_layout
    from pyschemaelectrical.symbols.terminals import terminal_symbol
    from pyschemaelectrical.system.system import Circuit, add_symbol
    from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins

    # SPDT contact structure (from contacts.py):
    # - Port "2" (NC): at (-2.5, -5.0) relative to pole center
    # - Port "4" (NO): at (2.5, -5.0) relative to pole center
    # - Port "1" (COM): at (2.5, 5.0) relative to pole center

    pole_spacing = GRID_SIZE * 8  # 40mm between poles

    def create_single_changeover(s, start_x, start_y, tag_gens, t_maps, instance):
        """Create a single changeover instance with single terminals."""
        c = Circuit()

        # Use provided pins or auto-generate
        if tm_top_left_pins is not None:
            input1_pins = tm_top_left_pins
        else:
            s, input1_pins = next_terminal_pins(s, tm_top_left, poles)
        if tm_top_right_pins is not None:
            input2_pins = tm_top_right_pins
        else:
            s, input2_pins = next_terminal_pins(s, tm_top_right, poles)
        if tm_bot_pins is not None:
            output_pins = tm_bot_pins
        else:
            s, output_pins = next_terminal_pins(s, tm_bot, poles)

        # Get switch tag
        s, switch_tag = next_tag(s, tag_prefix)

        # Position the switch (middle)
        switch_y = start_y + symbol_spacing
        switch_sym = multi_pole_spdt_symbol(poles=poles, label=switch_tag)
        switch_sym = add_symbol(c, switch_sym, start_x, switch_y)

        for i in range(poles):
            pole_x = start_x + (i * pole_spacing)

            # Top Left: NC terminal for input_1
            nc_x = pole_x - 2.5
            nc_y = switch_y - symbol_spacing
            nc_sym = terminal_symbol(
                tm_top_left, pins=(input1_pins[i],), label_pos="left" if i == 0 else ""
            )
            nc_sym = add_symbol(c, nc_sym, nc_x, nc_y)
            lines = auto_connect(nc_sym, switch_sym)
            c.elements.extend(lines)

            # Top Right: NO terminal for input_2
            no_x = pole_x + 2.5
            no_y = switch_y - symbol_spacing
            no_sym = terminal_symbol(
                tm_top_right, pins=(input2_pins[i],), label_pos="right"
            )
            no_sym = add_symbol(c, no_sym, no_x, no_y)
            lines = auto_connect(no_sym, switch_sym)
            c.elements.extend(lines)

            # Bottom: Common terminal for output
            com_x = pole_x + 2.5
            com_y = switch_y + symbol_spacing
            com_sym = terminal_symbol(
                tm_bot, pins=(output_pins[i],), label_pos="left" if i == 0 else ""
            )
            com_sym = add_symbol(c, com_sym, com_x, com_y)
            lines = auto_connect(switch_sym, com_sym)
            c.elements.extend(lines)

        return s, c.elements

    final_state, all_elements = create_horizontal_layout(
        state=state,
        start_x=x,
        start_y=y,
        count=count,
        spacing=spacing,
        generator_func_single=create_single_changeover,
        default_tag_generators={},
        tag_generators=kwargs.get("tag_generators"),
        terminal_maps=kwargs.get("terminal_maps"),
    )

    circuit = Circuit(elements=all_elements)

    # Apply wire labels if provided
    if wire_labels is not None:
        from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

        circuit = add_wire_labels_to_circuit(circuit, wire_labels)

    used_terminals = [tm_top_left, tm_top_right, tm_bot]

    return final_state, circuit, used_terminals


def power_distribution(
    state: Any,
    x: float,
    y: float,
    # Terminal maps (required)
    terminal_maps: Dict[str, str],
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_POWER,
    spacing_single_pole: float = LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE,
    voltage_monitor_offset: float = LayoutDefaults.VOLTAGE_MONITOR_OFFSET,
    psu_offset: float = LayoutDefaults.PSU_LAYOUT_OFFSET,
    count: int = 1,
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a complete power distribution system (Changeover + Voltage Monitor + PSU).

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        terminal_maps: Dict mapping logical keys to physical
            terminal IDs. Required keys: 'INPUT_1',
            'INPUT_2', 'OUTPUT', 'PSU_INPUT',
            'PSU_OUTPUT_1', 'PSU_OUTPUT_2'
        spacing: Horizontal spacing between changeover circuits
        spacing_single_pole: Spacing for single-pole circuits
        voltage_monitor_offset: Offset after changeover circuits for voltage monitor
        psu_offset: Additional offset after voltage monitor for PSU
        count: Number of changeover circuit instances.

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    required_keys = [
        "INPUT_1",
        "INPUT_2",
        "OUTPUT",
        "PSU_INPUT",
        "PSU_OUTPUT_1",
        "PSU_OUTPUT_2",
    ]
    missing_keys = [k for k in required_keys if k not in terminal_maps]
    if missing_keys:
        # Fallback for legacy keys if new ones are missing
        if "PSU_OUTPUT_24V" in terminal_maps and "PSU_OUTPUT_1" not in terminal_maps:
            terminal_maps["PSU_OUTPUT_1"] = terminal_maps["PSU_OUTPUT_24V"]
        if "PSU_OUTPUT_GND" in terminal_maps and "PSU_OUTPUT_2" not in terminal_maps:
            terminal_maps["PSU_OUTPUT_2"] = terminal_maps["PSU_OUTPUT_GND"]

        # Check again
        missing_keys = [k for k in required_keys if k not in terminal_maps]
        if missing_keys:
            raise ValueError(f"terminal_maps missing required keys: {missing_keys}")

    all_elements = []
    all_terminals = []

    current_x = x

    # 1. Changeover circuits
    for _ in range(count):
        state, circuit, terminals = changeover(
            state,
            current_x,
            y,
            tm_top_left=terminal_maps["INPUT_1"],
            tm_top_right=terminal_maps["INPUT_2"],
            tm_bot=terminal_maps["OUTPUT"],
            spacing=spacing,
        )
        all_elements.extend(circuit.elements)
        all_terminals.extend(terminals)
        current_x += spacing

    # 2. Voltage Monitor
    vm_x = x + (count * spacing) + voltage_monitor_offset

    state, vm_circuit, vm_terms = coil(
        state=state, x=vm_x, y=y, tm_top=terminal_maps["INPUT_1"]
    )
    all_elements.extend(vm_circuit.elements)
    all_terminals.extend(vm_terms)

    # 3. 24V PSU
    psu_x = vm_x + spacing_single_pole + psu_offset

    state, psu_c, psu_terms = psu(
        state=state,
        x=psu_x,
        y=y,
        tm_top=terminal_maps["PSU_INPUT"],
        tm_bot_left=terminal_maps["PSU_OUTPUT_1"],
        tm_bot_right=terminal_maps["PSU_OUTPUT_2"],
    )
    all_elements.extend(psu_c.elements)
    all_terminals.extend(psu_terms)

    # Combine everything
    system_circuit = Circuit(elements=all_elements)

    return state, system_circuit, list(set(all_terminals))
