from typing import Tuple, Dict, Any, Optional
from dataclasses import replace
from pyschemaelectrical.model.core import Symbol, Point, Style, Element, Vector
from pyschemaelectrical.model.primitives import Line
from pyschemaelectrical.utils.transform import translate
from pyschemaelectrical.model.constants import (
    DEFAULT_POLE_SPACING,
    GRID_SIZE,
    LINE_WIDTH_THIN,
    LINKAGE_DASH_PATTERN,
    COLOR_BLACK,
)
from pyschemaelectrical.model.parts import standard_text
from .contacts import (
    three_pole_normally_open_symbol,
    normally_closed_symbol,
    normally_open_symbol,
)
from .coils import coil_symbol
from .actuators import emergency_stop_button_symbol, turn_switch_symbol


def contactor_symbol(
    label: str = "",
    coil_pins: Optional[Tuple[str, str]] = None,
    contact_pins: Tuple[str, str, str, str, str, str] = ("1", "2", "3", "4", "5", "6"),
) -> Symbol:
    """
    High-level contactor symbol.

    Combines a 3-pole NO contact block and a Coil.
    The coil is placed to the left of the contacts.
    A mechanical linkage (stippled line) connects the coil to the contacts.

    Args:
        label (str): The device label (e.g. "-K1").
        coil_pins (Optional[Tuple[str, str]]): Pins for the coil (A1, A2). If None, coil terminals are hidden.
        contact_pins (Tuple[str, ...]): Pins for the 3-pole contact (1..6).

    Returns:
        Symbol: The composite contactor symbol.
    """

    # 1. Create the contacts
    # The contacts are centered at (0,0), (10,0), (20,0) by default in three_pole_normally_open
    # (assuming DEFAULT_POLE_SPACING is 10mm)
    contacts_sym = three_pole_normally_open_symbol(label="", pins=contact_pins)

    # 2. Create the coil with label - it handles its own label placement
    coil_offset_x = -DEFAULT_POLE_SPACING * 2

    # Only show coil terminals/ports if pins are provided
    show_coil_terminals = coil_pins is not None
    safe_coil_pins = coil_pins if coil_pins is not None else ()

    coil_sym = coil_symbol(
        label=label, pins=safe_coil_pins, show_terminals=show_coil_terminals
    )
    coil_sym = translate(coil_sym, coil_offset_x, 0)

    # 3. Create the mechanical linkage (stippled line)
    linkage_start = Point(coil_offset_x + DEFAULT_POLE_SPACING / 2, 0)
    linkage_end = Point(DEFAULT_POLE_SPACING * 1.75, 0)

    linkage_style = Style(
        stroke=COLOR_BLACK,
        stroke_width=LINE_WIDTH_THIN,
        stroke_dasharray=LINKAGE_DASH_PATTERN,
    )

    linkage_line = Line(linkage_start, linkage_end, linkage_style)

    # 4. Combine everything - coil already has the label
    all_elements = contacts_sym.elements + coil_sym.elements + [linkage_line]

    # Merge ports
    all_ports = {**contacts_sym.ports, **coil_sym.ports}

    return Symbol(elements=all_elements, ports=all_ports, label=label)


def emergency_stop_assembly_symbol(
    label: str = "", pins: Tuple[str, str] = ("1", "2")
) -> Symbol:
    """
    Emergency Stop Assembly.

    Combines a Normally Closed contact with an Emergency Stop Mushroom Head.
    The Button is placed to the LEFT of the contact.
    Linkage: 1 Grid (5mm) to the Left.
    Head: At end of linkage, pointing Left.
    """
    # 1. Contact (Vertical)
    contact_sym = normally_closed_symbol(label=label, pins=pins)

    # 2. Linkage (Dashed line from contact center to Left)
    linkage_len = GRID_SIZE / 2  # 2.5mm
    linkage_vector = Vector(-linkage_len, 0)  # Left

    linkage = Line(
        Point(0, 0),
        Point(linkage_vector.dx, linkage_vector.dy),
        Style(
            stroke=COLOR_BLACK,
            stroke_width=LINE_WIDTH_THIN,
            stroke_dasharray=LINKAGE_DASH_PATTERN,
        ),
    )

    # 3. Button (Mushroom Head)
    # New Geometry: 0 deg points Right.
    # We want it pointing Left (180 deg).
    # Position: At (-5, 0).

    button_sym = emergency_stop_button_symbol(rotation=180)
    button_sym = translate(button_sym, linkage_vector.dx, linkage_vector.dy)

    all_elements = contact_sym.elements + [linkage] + button_sym.elements

    return Symbol(elements=all_elements, ports=contact_sym.ports, label=label)


def turn_switch_assembly_symbol(
    label: str = "", pins: Tuple[str, str] = ("1", "2")
) -> Symbol:
    """
    Turn Switch Assembly.

    Combines a Normally Open contact with a Turn Switch actuator.
    The Turn Switch is placed to the LEFT of the contact.

    Composition:
    - NO Contact (vertical, standard orientation)
    - Dashed mechanical linkage (connects to blade at -GRID_SIZE/4)
    - Turn Switch S-shape at end of linkage (-GRID_SIZE)

    Args:
        label: Component label (e.g. "-S1").
        pins: Tuple of 2 pin labels for the contact.

    Returns:
        Symbol: The composite turn switch assembly.
    """
    # 1. NO Contact (vertical)
    contact_sym = normally_open_symbol(label=label, pins=pins)

    # 2. Linkage
    # Connects the contact blade (at x approx -1.25mm) to the actuator (at x = -5.0mm)
    blade_x_at_center = -GRID_SIZE / 4
    actuator_x = -GRID_SIZE / 2

    linkage = Line(
        Point(blade_x_at_center, 0),
        Point(actuator_x, 0),
        Style(
            stroke=COLOR_BLACK,
            stroke_width=LINE_WIDTH_THIN,
            stroke_dasharray=LINKAGE_DASH_PATTERN,
        ),
    )

    # 3. Turn Switch actuator (rotated 180° so attachment is on right, facing the contact)
    actuator_sym = turn_switch_symbol(rotation=180)
    actuator_sym = translate(actuator_sym, actuator_x, 0)

    # 4. Combine all elements
    all_elements = contact_sym.elements + [linkage] + actuator_sym.elements

    return Symbol(elements=all_elements, ports=contact_sym.ports, label=label)
