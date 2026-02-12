"""
Standard Control Circuits.

This module provides standard control circuit configurations.
All terminal IDs, tags, and pins are parameters with sensible defaults.
Layout values use constants from model.constants but can be overridden.
"""

from typing import Any, List, Optional, Tuple

from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.layout.layout import create_horizontal_layout
from pyschemaelectrical.model.constants import GRID_SIZE, LayoutDefaults, StandardTags
from pyschemaelectrical.model.core import Symbol
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.symbols.contacts import (
    normally_open_symbol,
    spdt_contact_symbol,
)
from pyschemaelectrical.symbols.references import ref_symbol
from pyschemaelectrical.symbols.terminals import terminal_symbol
from pyschemaelectrical.system.connection_registry import register_connection
from pyschemaelectrical.system.system import Circuit, add_symbol, auto_connect_circuit
from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins
from pyschemaelectrical.utils.transform import translate


def spdt(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameters
    tm_top: str,
    tm_bot_left: str,
    tm_bot_right: str,
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_CONTROL,
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_DEFAULT,
    column_offset: float = LayoutDefaults.CONTROL_COLUMN_OFFSET,
    # Component parameters (with defaults)
    coil_tag_prefix: str = StandardTags.CONTACTOR,
    contact_tag_prefix: str = StandardTags.RELAY,
    # Pin parameters
    coil_pins: Tuple[str, ...] = ("A1", "A2"),
    contact_pins: Tuple[str, ...] = ("1", "2", "4"),
    tm_top_pins: Optional[Tuple[str, ...]] = None,
    tm_bot_left_pins: Optional[Tuple[str, ...]] = None,
    tm_bot_right_pins: Optional[Tuple[str, ...]] = None,
    # Multi-count, wire labels, and relay tag
    count: int = 1,
    wire_labels: Optional[List[str]] = None,
    relay_tag: Optional[str] = None,
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a standard SPDT control circuit (Coil + Inverted SPDT).

    Layout (Single Column Vertical Stack):
    - Top Terminal (Input)
    - Coil
    - SPDT Contact (Inverted)
    - Output Terminals (Double)

    This creates a visual flow where the SPDT is underneath the Coil,
    and connected in sequence.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top: Top terminal ID (typically EM Stop or Input)
        tm_bot_left: Bottom Left Terminal ID (typically NC output)
        tm_bot_right: Bottom Right Terminal ID (typically NO output)
        spacing: Horizontal spacing between circuit instances
        symbol_spacing: Vertical spacing between components
        column_offset: Unused in single-column layout (kept for API compatibility)
        coil_tag_prefix: Tag prefix for coil (default: "Q")
        contact_tag_prefix: Tag prefix for feedback contact (default: "K")
        coil_pins: Pins for coil (Input, Output)
        contact_pins: Pins for SPDT (Common, NC, NO)
        tm_top_pins: Pins for Top terminal
        tm_bot_left_pins: Pins for Bottom Left terminal
        tm_bot_right_pins: Pins for Bottom Right terminal
        count: Number of circuit instances.
        wire_labels: Wire label strings to apply per instance.
        relay_tag: Fixed relay tag (e.g., "K2"). When set, the contact tag
                   is always this value and contact pins auto-increment.

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    terminal_maps = kwargs.get("terminal_maps") or {}

    # Build tag generators for relay_tag
    effective_tag_generators = dict(kwargs.get("tag_generators") or {})
    if relay_tag:
        def _fixed_contact_gen(s):
            return s, relay_tag
        effective_tag_generators[contact_tag_prefix] = _fixed_contact_gen

    def create_single_control(s, start_x, start_y, tag_gens, t_maps, instance):
        """Create a single Motor Control instance with dynamic pin numbering."""
        c = Circuit()

        # --- Tags ---
        # Check if custom tag generators are provided, otherwise use next_tag
        if tag_gens and coil_tag_prefix in tag_gens:
            s, coil_tag = tag_gens[coil_tag_prefix](s)
        else:
            s, coil_tag = next_tag(s, coil_tag_prefix)

        if tag_gens and contact_tag_prefix in tag_gens:
            s, contact_tag = tag_gens[contact_tag_prefix](s)
        else:
            s, contact_tag = next_tag(s, contact_tag_prefix)

        # --- Dynamic Pin Generation ---
        # If contact_pins is the default (1, 2, 4), generate instance-based pins
        # Instance 0: 11, 12, 14
        # Instance 1: 21, 22, 24
        # Instance 2: 31, 32, 34, etc.
        if contact_pins == ("1", "2", "4") and instance >= 0:
            # Generate pins based on instance: (i+1)1, (i+1)2, (i+1)4
            pin_prefix = str(instance + 1)
            dynamic_contact_pins = (
                f"{pin_prefix}1",
                f"{pin_prefix}2",
                f"{pin_prefix}4",
            )
        else:
            dynamic_contact_pins = contact_pins

        # --- Pins (Terminals) ---
        if tm_top_pins is None:
            s, p_top = next_terminal_pins(s, tm_top, 1)
        else:
            p_top = tm_top_pins

        if tm_bot_left_pins is None:
            s, p_left = next_terminal_pins(s, tm_bot_left, 1)
        else:
            p_left = tm_bot_left_pins

        if tm_bot_right_pins is None:
            s, p_right = next_terminal_pins(s, tm_bot_right, 1)
        else:
            p_right = tm_bot_right_pins

        # --- Coordinates ---
        # Vertical Stack
        y_r1 = start_y
        y_r2 = start_y + symbol_spacing
        y_r3 = start_y + (symbol_spacing * 2)
        y_r4 = start_y + (symbol_spacing * 3)

        # --- Components ---

        # 1. Top Terminal
        top_sym = terminal_symbol(tm_top, pins=p_top)
        add_symbol(c, top_sym, start_x, y_r1)

        # 2. Coil
        coil_sym = coil_symbol(coil_tag, pins=coil_pins)
        add_symbol(c, coil_sym, start_x, y_r2)

        # 3. SPDT Inverted (Underneath Coil) - use dynamic pins
        spdt_sym = spdt_contact_symbol(
            contact_tag, pins=dynamic_contact_pins, inverted=True
        )

        # Alignment Correction:
        # SPDT Inverted: Common pin is at local x=+2.5 (GRID_SIZE/2).
        # Coil: Bottom pin is at local x=0.
        # To align Common with Coil, we must shift the SPDT symbol LEFT by 2.5.
        spdt_offset = GRID_SIZE / 2
        add_symbol(c, spdt_sym, start_x - spdt_offset, y_r3)

        # 4. Double Terminal / Ref (Underneath SPDT)
        # We create a composite symbol for the 2 output locations to allow auto-connect branching
        t_left = terminal_symbol(tm_bot_left, pins=p_left, label_pos="left")

        # CHANGED: Use ref_symbol for the right branch instead of a terminal
        t_right = ref_symbol(
            tag=tm_bot_right, label=tm_bot_right, direction="down", label_pos="right"
        )

        # Alignment Correction for Terminals:
        # SPDT Center is now at (start_x - 2.5).
        # SPDT Pins relative to its center:
        #   NC Pin: -2.5 (Local). Global Alignment X = (start_x - 2.5) - 2.5 = start_x - 5.0.
        #   NO Pin: +2.5 (Local). Global Alignment X = (start_x - 2.5) + 2.5 = start_x.

        # Terminal positioning:
        # We place the composite symbol at start_x.
        # So inside the composite, we need relative offsets of -5.0 and 0.0.

        t_left = translate(t_left, -GRID_SIZE, 0)  # -5.0
        t_right = translate(t_right, 0, 0)  # 0.0

        # Merge ports with unique keys
        ports = {}
        for k, p in t_left.ports.items():
            ports[f"left_{k}"] = p
        for k, p in t_right.ports.items():
            ports[f"right_{k}"] = p

        term_sym = Symbol(t_left.elements + t_right.elements, ports, label="")
        add_symbol(c, term_sym, start_x, y_r4)

        # --- Auto Connect ---
        # Automatically connects sequence: Top -> Coil -> SPDT -> DoubleTerminal
        # Connect all symbols sequentially (Top->Coil->SPDT->Terminals)
        auto_connect_circuit(c)

        # --- Explicit Registry Registration ---
        # Use dynamic_contact_pins for registry
        # 1. Top Terminal (Output/Bottom "2") -> Coil (Input/Top "A1")
        if len(p_top) >= 2 and len(coil_pins) >= 1:
            s = register_connection(
                s, tm_top, p_top[1], coil_tag, coil_pins[0], side="bottom"
            )

        # 2. SPDT (NC "X2") -> Left Terminal (Input/Top "1")
        if len(dynamic_contact_pins) >= 2 and len(p_left) >= 1:
            # SPDT pins: (Com=X1, NC=X2, NO=X4). Index 1 is NC.
            s = register_connection(
                s,
                tm_bot_left,
                p_left[0],
                contact_tag,
                dynamic_contact_pins[1],
                side="top",
            )

        # 3. SPDT (NO "X4") -> Right Ref (Input/Top "1")
        if len(dynamic_contact_pins) >= 3:
            # SPDT pins: (Com=X1, NC=X2, NO=X4). Index 2 is NO.
            # Use "1" for the ref symbol port
            s = register_connection(
                s, tm_bot_right, "1", contact_tag, dynamic_contact_pins[2], side="top"
            )

        return s, c.elements

    # Use horizontal layout for multiple instances
    final_state, all_elements = create_horizontal_layout(
        state=state,
        start_x=x,
        start_y=y,
        count=count,
        spacing=spacing,
        generator_func_single=create_single_control,
        default_tag_generators={},
        tag_generators=effective_tag_generators if effective_tag_generators else kwargs.get("tag_generators"),
        terminal_maps=terminal_maps,
    )

    circuit = Circuit(elements=all_elements)

    # Apply wire labels if provided
    if wire_labels is not None:
        from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

        circuit = add_wire_labels_to_circuit(circuit, wire_labels)

    # Exclude tm_bot_right because it is a reference symbol, not a terminal strip
    used_terminals = [tm_top, tm_bot_left]

    return final_state, circuit, used_terminals


def no_contact(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameters
    tm_top: str,
    tm_bot: str,
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE,
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_STANDARD,
    # Component parameters (with defaults)
    tag_prefix: str = StandardTags.SWITCH,
    switch_pins: Tuple[str, ...] = ("3", "4"),
    tm_top_pins: Optional[Tuple[str, ...]] = None,
    tm_bot_pins: Optional[Tuple[str, ...]] = None,
    # Multi-count and wire labels
    count: int = 1,
    wire_labels: Optional[List[str]] = None,
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a simple Normally Open (NO) contact circuit.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top: Input terminal ID
        tm_bot: Output terminal ID (typically GND)
        spacing: Horizontal spacing between circuit instances
        symbol_spacing: Vertical spacing between components
        tag_prefix: Tag prefix for switch (default: "S")
        switch_pins: Pin labels for the switch (default: ("3", "4"))
        tm_top_pins: Explicit pins for top terminal
        tm_bot_pins: Explicit pins for bottom terminal
        count: Number of circuit instances.
        wire_labels: Wire label strings to apply per instance.

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    builder = CircuitBuilder(state)
    builder.set_layout(x=x, y=y, spacing=spacing, symbol_spacing=symbol_spacing)

    # 1. Input Terminal
    builder.add_terminal(tm_top, poles=1, pins=tm_top_pins)

    # 2. Switch (Normally Open)
    builder.add_component(
        normally_open_symbol, tag_prefix=tag_prefix, poles=1, pins=switch_pins
    )

    # 3. Output Terminal (GND)
    builder.add_terminal(tm_bot, poles=1, pins=tm_bot_pins)

    result = builder.build(
        count=count,
        start_indices=kwargs.get("start_indices"),
        terminal_start_indices=kwargs.get("terminal_start_indices"),
        tag_generators=kwargs.get("tag_generators"),
        terminal_maps=kwargs.get("terminal_maps"),
        wire_labels=wire_labels,
    )
    return result.state, result.circuit, result.used_terminals


def coil(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameter
    tm_top: str,
    # Layout parameters (with defaults from constants)
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_STANDARD,
    # Component parameters (with defaults)
    tag_prefix: str = StandardTags.RELAY,
    coil_pins: Tuple[str, ...] = ("A1", "A2"),
    tm_top_pins: Tuple[str, str] = ("1", "2"),
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a simple coil circuit (e.g. Voltage Monitor, Relay Coil).

    The coil is connected between two pins of the specified terminal.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top: Input terminal ID (monitors between two pins of this terminal)
        symbol_spacing: Vertical spacing between components
        tag_prefix: Tag prefix for coil (default: "K")
        coil_pins: Pins for the coil (default: ("A1", "A2"))
        tm_top_pins: Use specific pins for the top terminal (default: ("1", "2"))

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    builder = CircuitBuilder(state)
    builder.set_layout(x, y, symbol_spacing=symbol_spacing)

    # 1. Top Terminal (Pin 1 of tm_top)
    builder.add_terminal(
        tm_top,
        logical_name="INPUT",
        poles=1,
        pins=[tm_top_pins[0]],  # Explicitly connect to Pin 1
        x_offset=0,
        y_increment=symbol_spacing,
        auto_connect_next=True,
    )

    # 2. Coil (Middle)
    builder.add_component(
        coil_symbol,
        tag_prefix=tag_prefix,
        y_increment=symbol_spacing,
        pins=coil_pins,
        auto_connect_next=True,
    )

    # 3. Bottom Terminal (Pin 2 of tm_top)
    builder.add_terminal(
        tm_top,
        logical_name="INPUT",  # Reusing same terminal ID
        poles=1,
        pins=[tm_top_pins[1]],  # Explicitly connect to Pin 2
        x_offset=0,
        y_increment=0,
        auto_connect_next=True,  # Connects Coil output to this
    )

    result = builder.build(
        count=kwargs.get("count", 1), tag_generators=kwargs.get("tag_generators")
    )
    return result.state, result.circuit, result.used_terminals
