"""
Standard Control Circuits.

This module provides standard control circuit configurations.
All terminal IDs, tags, and pins are parameters with sensible defaults.
Layout values use constants from model.constants but can be overridden.
"""

from typing import Any, Tuple, List, Optional

from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.system.system import Circuit, add_symbol, auto_connect_circuit
from pyschemaelectrical.layout.layout import create_horizontal_layout
from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins
from pyschemaelectrical.utils.transform import translate
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.symbols.contacts import spdt_contact_symbol, normally_open_symbol
from pyschemaelectrical.symbols.terminals import terminal_symbol
from pyschemaelectrical.model.core import Symbol
from pyschemaelectrical.model.constants import (
    LayoutDefaults,
    StandardTags,
    GRID_SIZE
)


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
    **kwargs
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

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    terminal_maps = kwargs.get('terminal_maps') or {}

    def create_single_control(s, start_x, start_y, tag_gens, t_maps):
        """Create a single Motor Control instance."""
        c = Circuit()
        
        # --- Tags ---
        s, coil_tag = next_tag(s, coil_tag_prefix)
        s, contact_tag = next_tag(s, contact_tag_prefix)
        
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
        
        # 3. SPDT Inverted (Underneath Coil)
        spdt_sym = spdt_contact_symbol(contact_tag, pins=contact_pins, inverted=True)
        
        # Alignment Correction:
        # SPDT Inverted: Common pin is at local x=+2.5 (GRID_SIZE/2).
        # Coil: Bottom pin is at local x=0.
        # To align Common with Coil, we must shift the SPDT symbol LEFT by 2.5.
        spdt_offset = GRID_SIZE / 2
        add_symbol(c, spdt_sym, start_x - spdt_offset, y_r3)
        
        # 4. Double Terminal (Underneath SPDT)
        # We create a composite symbol for the 2 output terminals to allow auto-connect branching
        t_left = terminal_symbol(tm_bot_left, pins=p_left, label_pos="left")
        t_right = terminal_symbol(tm_bot_right, pins=p_right, label_pos="right")
        
        # Alignment Correction for Terminals:
        # SPDT Center is now at (start_x - 2.5).
        # SPDT Pins relative to its center:
        #   NC Pin: -2.5 (Local). Global Alignment X = (start_x - 2.5) - 2.5 = start_x - 5.0.
        #   NO Pin: +2.5 (Local). Global Alignment X = (start_x - 2.5) + 2.5 = start_x.
        
        # Terminal positioning:
        # We place the composite symbol at start_x.
        # So inside the composite, we need relative offsets of -5.0 and 0.0.
        
        t_left = translate(t_left, -GRID_SIZE, 0) # -5.0
        t_right = translate(t_right, 0, 0)          # 0.0
        
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
        # The geometric alignment ensures proper connections.
        auto_connect_circuit(c)
        
        return s, c.elements

    # Use horizontal layout for multiple instances
    count = kwargs.get("count", 1)
    final_state, all_elements = create_horizontal_layout(
        state=state,
        start_x=x,
        start_y=y,
        count=count,
        spacing=spacing,
        generator_func_single=create_single_control,
        default_tag_generators={},
        tag_generators=kwargs.get("tag_generators"),
        terminal_maps=terminal_maps
    )
    
    circuit = Circuit(elements=all_elements)
    used_terminals = [tm_top, tm_bot_left, tm_bot_right]
    
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
    **kwargs
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

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    builder = CircuitBuilder(state)
    builder.set_layout(
        x=x,
        y=y,
        spacing=spacing,
        symbol_spacing=symbol_spacing
    )

    # 1. Input Terminal
    builder.add_terminal(tm_top, poles=1)

    # 2. Switch (Normally Open)
    builder.add_component(normally_open_symbol, tag_prefix=tag_prefix, poles=1, pins=switch_pins)

    # 3. Output Terminal (GND)
    builder.add_terminal(tm_bot, poles=1)

    result = builder.build(
        count=kwargs.get("count", 1),
        start_indices=kwargs.get("start_indices"),
        terminal_start_indices=kwargs.get("terminal_start_indices"),
        tag_generators=kwargs.get("tag_generators"),
        terminal_maps=kwargs.get("terminal_maps")
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
    **kwargs
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
        logical_name='INPUT',
        poles=1,
        pins=[tm_top_pins[0]], # Explicitly connect to Pin 1
        x_offset=0,
        y_increment=symbol_spacing,
        auto_connect_next=True
    )

    # 2. Coil (Middle)
    builder.add_component(
        coil_symbol,
        tag_prefix=tag_prefix,
        y_increment=symbol_spacing,
        pins=coil_pins,
        auto_connect_next=True
    )

    # 3. Bottom Terminal (Pin 2 of tm_top)
    builder.add_terminal(
        tm_top,
        logical_name='INPUT', # Reusing same terminal ID
        poles=1,
        pins=[tm_top_pins[1]], # Explicitly connect to Pin 2
        x_offset=0,
        y_increment=0,
        auto_connect_next=True # Connects Coil output to this
    )

    result = builder.build(count=kwargs.get("count", 1))
    return result.state, result.circuit, result.used_terminals
