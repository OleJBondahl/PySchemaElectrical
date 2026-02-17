"""
Standard Motor Circuits.

This module provides standard motor circuit configurations.
All terminal IDs, tags, and pins are parameters with sensible defaults.
Layout values use constants from model.constants but can be overridden.
"""

from __future__ import annotations

from typing import Any

from pyschemaelectrical.builder import BuildResult
from pyschemaelectrical.layout.layout import create_horizontal_layout
from pyschemaelectrical.model.constants import (
    LayoutDefaults,
    REF_ARROW_LENGTH,
    StandardTags,
)
from pyschemaelectrical.model.core import Point
from pyschemaelectrical.model.parts import standard_style
from pyschemaelectrical.model.primitives import Line
from pyschemaelectrical.symbols.assemblies import contactor_symbol
from pyschemaelectrical.symbols.breakers import three_pole_circuit_breaker_symbol
from pyschemaelectrical.symbols.protection import three_pole_thermal_overload_symbol
from pyschemaelectrical.symbols.references import ref_symbol
from pyschemaelectrical.symbols.terminals import (
    multi_pole_terminal_symbol,
    terminal_symbol,
)
from pyschemaelectrical.symbols.transducers import current_transducer_assembly_symbol
from pyschemaelectrical.system.connection_registry import register_connection
from pyschemaelectrical.system.system import Circuit, add_symbol, auto_connect_circuit
from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins


def dol_starter(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameters
    tm_top: str,
    tm_bot: str | list[str],
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_MOTOR,
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_DEFAULT,
    # Component parameters (with defaults)
    breaker_tag_prefix: str = StandardTags.BREAKER,
    thermal_tag_prefix: str = "FT",
    contactor_tag_prefix: str = StandardTags.CONTACTOR,
    ct_tag_prefix: str = "CT",
    # Pin parameters for symbols (with defaults)
    breaker_pins: tuple[str, str, str, str, str, str] = ("1", "2", "3", "4", "5", "6"),
    thermal_pins: tuple[str, str, str, str, str, str] = ("", "T1", "", "T2", "", "T3"),
    contactor_pins: tuple[str, str, str, str, str, str] = (
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
    ),
    ct_pins: tuple[str, ...] = ("1", "2", "3", "4"),
    ct_terminals: tuple[str, ...] | None = None,
    # Pin parameters for terminals (None = auto-number)
    tm_top_pins: tuple[str, ...] | None = None,
    tm_bot_pins: tuple[str, ...] | None = None,
    # Terminal poles (default 3 for three-phase)
    poles: int = 3,
    # Optional aux terminals
    tm_aux_1: str | None = None,
    tm_aux_2: str | None = None,
    # Multi-count and wire label parameters
    count: int = 1,
    wire_labels: list[str] | None = None,
    **kwargs,
) -> BuildResult:
    """
    Create a Direct-On-Line (DOL) Motor Starter.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top: Top terminal ID (Input)
        tm_bot: Bottom terminal ID (Output). Can be a list
            for per-instance terminals.
        spacing: Horizontal spacing between circuit instances
        symbol_spacing: Vertical spacing between components
        breaker_tag_prefix: Tag prefix for circuit breaker (default: "F")
        thermal_tag_prefix: Tag prefix for thermal overload (default: "FT")
        contactor_tag_prefix: Tag prefix for contactor (default: "Q")
        ct_tag_prefix: Tag prefix for current transducer (default: "CT")
        tm_top_pins: Pin labels for top terminal (None = auto-number)
        tm_bot_pins: Pin labels for bottom terminal (None = auto-number)
        poles: Number of terminal poles (default 3 for three-phase)
        tm_aux_1: Optional terminal ID for 24V aux connection
        tm_aux_2: Optional terminal ID for GND aux connection
        count: Number of circuit instances to create.
        wire_labels: Wire label strings to apply to vertical
            wires per instance.

    Returns:
        BuildResult containing (state, circuit, used_terminals).
    """
    # Support legacy terminal_maps parameter
    terminal_maps = kwargs.get("terminal_maps") or {}
    if not tm_aux_1:
        tm_aux_1 = terminal_maps.get("FUSED_24V")
    if not tm_aux_2:
        tm_aux_2 = terminal_maps.get("GND")

    # Resolve per-instance terminal: tm_bot can be a list
    tm_bot_list = tm_bot if isinstance(tm_bot, list) else None

    # Accumulators for BuildResult metadata
    tag_accumulator: dict[str, list[str]] = {}
    pin_accumulator: dict[str, list[str]] = {}

    def create_single_dol(s, start_x, start_y, tag_gens, t_maps, instance):
        """Create a single DOL starter instance."""
        c = Circuit()
        current_y = start_y

        # Resolve per-instance bottom terminal
        instance_tm_bot = tm_bot_list[instance] if tm_bot_list else tm_bot

        # Get terminal pins (auto-number if not provided)
        if tm_top_pins is None:
            s, input_pins = next_terminal_pins(s, tm_top, poles)
        else:
            input_pins = tm_top_pins
        pin_accumulator.setdefault(str(tm_top), []).extend(input_pins)

        if tm_bot_pins is None:
            s, output_pins = next_terminal_pins(s, instance_tm_bot, poles)
        else:
            output_pins = tm_bot_pins
        pin_accumulator.setdefault(str(instance_tm_bot), []).extend(output_pins)

        # Get component tags
        s, breaker_tag = next_tag(s, breaker_tag_prefix)
        tag_accumulator.setdefault(breaker_tag_prefix, []).append(breaker_tag)
        s, thermal_tag = next_tag(s, thermal_tag_prefix)
        tag_accumulator.setdefault(thermal_tag_prefix, []).append(thermal_tag)
        s, cont_tag = next_tag(s, contactor_tag_prefix)
        tag_accumulator.setdefault(contactor_tag_prefix, []).append(cont_tag)
        s, ct_tag = next_tag(s, ct_tag_prefix)
        tag_accumulator.setdefault(ct_tag_prefix, []).append(ct_tag)

        # 1. Input Terminal
        sym = multi_pole_terminal_symbol(
            tm_top, pins=input_pins, poles=poles, label_pos="left"
        )
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing

        # 2. Circuit Breaker
        sym = three_pole_circuit_breaker_symbol(breaker_tag, pins=breaker_pins)
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing

        # 3. Contactor
        sym = contactor_symbol(cont_tag, contact_pins=contactor_pins)
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing/2

        # 4. Thermal Overload (top pins hidden)
        sym = three_pole_thermal_overload_symbol(thermal_tag, pins=thermal_pins)
        add_symbol(c, sym, start_x, current_y)
        current_y += symbol_spacing

        # 5. Current Transducer (inline with connection)
        sym = current_transducer_assembly_symbol(ct_tag, pins=ct_pins)
        ct_placed = add_symbol(c, sym, start_x, current_y)

        current_y += symbol_spacing

        # 6. Output Terminal
        sym = multi_pole_terminal_symbol(
            instance_tm_bot, pins=output_pins, poles=poles, label_pos="left"
        )
        add_symbol(c, sym, start_x, current_y)

        # Connect all symbols sequentially
        auto_connect_circuit(c)

        # 7. Terminals/References above CT pins (after auto_connect to
        # avoid interfering with the main sequential wiring chain)
        if ct_terminals:
            wire_style = standard_style()
            ct_offset_y = symbol_spacing / 2
            for i, tid in enumerate(ct_terminals):
                if i >= len(ct_pins):
                    break
                port_id = ct_pins[i]
                if port_id not in ct_placed.ports:
                    continue
                port = ct_placed.ports[port_id]
                px, py = port.position.x, port.position.y
                target_y = py - ct_offset_y
                # Within each CT pair, right pin labels face right
                lpos = "right" if i % 2 == 1 else "left"

                is_ref = getattr(tid, "reference", False)
                if is_ref:
                    # Place reference higher so tail aligns with terminal level
                    ref_y = target_y - REF_ARROW_LENGTH
                    sym = ref_symbol(
                        tag=str(tid), direction="up", label_pos=lpos
                    )
                    placed = add_symbol(c, sym, px, ref_y)
                    wire_end_y = placed.ports["2"].position.y
                    # Register PLC reference in the connection registry
                    s, ref_pins = next_terminal_pins(s, str(tid), 1)
                    s = register_connection(
                        s, str(tid), ref_pins[0], ct_tag, port_id, side="bottom"
                    )
                else:
                    s, ct_tm_pins = next_terminal_pins(s, str(tid), 1)
                    sym = terminal_symbol(
                        str(tid), pins=ct_tm_pins, label_pos=lpos
                    )
                    placed = add_symbol(c, sym, px, target_y)
                    wire_end_y = placed.ports["2"].position.y
                    s = register_connection(
                        s, str(tid), ct_tm_pins[0], ct_tag, port_id, side="bottom"
                    )

                # Wire from CT port up to terminal/reference
                c.elements.append(
                    Line(Point(px, py), Point(px, wire_end_y), wire_style)
                )

        # --- Explicit Registry Registration ---
        # 1. Top Terminal (Output Side/Bottom) -> Circuit Breaker (Input Side/Top)
        # input_pins: sequential pins from next_terminal_pins, e.g. ("1", "2", "3")
        # breaker pins: [1, 2, 3, 4, 5, 6] -> Inputs: 1, 3, 5 (indices 0, 2, 4)
        for i in range(poles):
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
        for i in range(poles):
            if i < len(output_pins):
                term_pin = output_pins[i]

                # Contactor output pins are at indices 1, 3, 5 (pins "2", "4", "6")
                cont_pin_idx = (i * 2) + 1
                if cont_pin_idx < len(contactor_pins):
                    cont_pin = contactor_pins[cont_pin_idx]
                    s = register_connection(
                        s, instance_tm_bot, term_pin, cont_tag, cont_pin, side="top"
                    )

        return s, c.elements

    # Use horizontal layout for multiple instances
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

    # Apply wire labels if provided
    if wire_labels is not None:
        from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

        circuit = add_wire_labels_to_circuit(circuit, wire_labels)

    # Collect used terminals
    bot_list = tm_bot_list if tm_bot_list else [tm_bot]
    used_terminals = [tm_top] + bot_list
    if ct_terminals:
        for tid in ct_terminals:
            if not getattr(tid, "reference", False) and tid not in used_terminals:
                used_terminals.append(tid)

    return BuildResult(
        state=final_state,
        circuit=circuit,
        used_terminals=used_terminals,
        component_map=tag_accumulator,
        terminal_pin_map=pin_accumulator,
    )
