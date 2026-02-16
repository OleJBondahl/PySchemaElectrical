from dataclasses import replace
from typing import List

from pyschemaelectrical.model.constants import (
    COLOR_BLACK,
    DEFAULT_POLE_SPACING,
    GRID_SIZE,
    TEXT_FONT_FAMILY_AUX,
    TEXT_SIZE_PIN,
)
from pyschemaelectrical.model.core import Point, Port, Style, Symbol, Vector
from pyschemaelectrical.model.parts import (
    create_pin_labels,
    standard_style,
    standard_text,
    three_pole_factory,
)
from pyschemaelectrical.model.primitives import Element, Line, Text
from pyschemaelectrical.utils.transform import translate

"""
IEC 60617 Contact Symbols.

This module contains functions to generate contact symbols including:
- Normally Open (NO)
- Normally Closed (NC)
- Changeover (SPDT)
"""


def three_pole_normally_open_symbol(
    label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")
) -> Symbol:
    """
    Create an IEC 60617 Three Pole Normally Open Contact.

    Composed of 3 single NO contacts.

    Args:
        label (str): The component tag (e.g. "-K1").
        pins (tuple): A tuple of 6 pin numbers (e.g. ("1","2","3","4","5","6")).

    Returns:
        Symbol: The 3-pole symbol.
    """
    return three_pole_factory(normally_open_symbol, label, pins)


def normally_open_symbol(label: str = "", pins: tuple = ()) -> Symbol:
    """
    Create an IEC 60617 Normally Open Contact.

    Symbol Layout:
        |
       /
      |

    Dimensions:
        Height: 10mm (2 * GRID_SIZE)
        Width: Compatible with standard grid.

    Args:
        label (str): The component tag.
        pins (tuple): A tuple of pin numbers (up to 2).

    Returns:
        Symbol: The symbol.
    """

    h_half = GRID_SIZE  # 5.0

    # Gap: -2.5 to 2.5 (5mm gap)
    top_y = -GRID_SIZE / 2
    bot_y = GRID_SIZE / 2

    style = standard_style()

    # Vertical leads
    l1 = Line(Point(0, -h_half), Point(0, top_y), style)
    l2 = Line(Point(0, bot_y), Point(0, h_half), style)

    # Blade
    # Starts at the bottom contact point (0, 2.5)
    # End to the LEFT (-2.5, -2.5)
    blade_start = Point(0, bot_y)
    blade_end = Point(-GRID_SIZE / 2, top_y)

    blade = Line(blade_start, blade_end, style)

    elements: List[Element] = [l1, l2, blade]
    if label:
        elements.append(standard_text(label, Point(0, 0)))

    ports = {
        "1": Port("1", Point(0, -h_half), Vector(0, -1)),
        "2": Port("2", Point(0, h_half), Vector(0, 1)),
    }

    if pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)


def three_pole_normally_closed_symbol(
    label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")
) -> Symbol:
    """
    Create an IEC 60617 Three Pole Normally Closed Contact.

    Args:
        label (str): The component tag.
        pins (tuple): A tuple of 6 pin numbers.

    Returns:
        Symbol: The 3-pole symbol.
    """
    return three_pole_factory(normally_closed_symbol, label, pins)


def normally_closed_symbol(label: str = "", pins: tuple = ()) -> Symbol:
    """
    Create an IEC 60617 Normally Closed Contact.

    Symbol Layout:
       |
       |--
      /
     |

    Args:
        label (str): The component tag.
        pins (tuple): A tuple of pin numbers (up to 2).

    Returns:
        Symbol: The symbol.
    """

    h_half = GRID_SIZE  # 5.0
    top_y = -GRID_SIZE / 2  # -2.5
    bot_y = GRID_SIZE / 2  # 2.5

    style = standard_style()

    # Vertical lines (Terminals)
    l1 = Line(Point(0, -h_half), Point(0, top_y), style)
    l2 = Line(Point(0, bot_y), Point(0, h_half), style)

    # Horizontal Seat (Contact point)
    # Extends from top contact point to the right, to meet the blade
    seat_end_x = GRID_SIZE / 2  # 2.5
    seat = Line(Point(0, top_y), Point(seat_end_x, top_y), style)

    # Blade
    # Starts bottom-center, passes through the seat endpoint
    blade_start = Point(0, bot_y)

    # Calculate vector to the seat point
    target_x = seat_end_x
    target_y = top_y

    dx = target_x - blade_start.x
    dy = target_y - blade_start.y
    length = (dx**2 + dy**2) ** 0.5

    # Extend by 1/4 grid
    extension = GRID_SIZE / 4
    new_length = length + extension
    scale = new_length / length

    blade_end = Point(blade_start.x + dx * scale, blade_start.y + dy * scale)
    blade = Line(blade_start, blade_end, style)

    elements: List[Element] = [l1, l2, seat, blade]

    if label:
        elements.append(standard_text(label, Point(0, 0)))

    ports = {
        "1": Port("1", Point(0, -h_half), Vector(0, -1)),
        "2": Port("2", Point(0, h_half), Vector(0, 1)),
    }

    if pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)


def spdt_contact_symbol(
    label: str = "", pins: tuple = ("1", "2", "4"), inverted: bool = False
) -> Symbol:
    r"""
    Create an IEC 60617 Single Pole Double Throw (SPDT) Contact (Changeover).

    Combined NO and NC contact.
    One input (Common) and two outputs (NC, NO).
    Breaker arm rests at the NC contact.

    Symbol Layout (Standard):
       NC      NO
        |__     |
           \    |
            \   |
             \  |
              \ |
               \|
               Com

    Alignment:
    - Common and NO are vertically aligned on the right.
    - NC is on the left.
    - Blade spans from Common (Right) to NC (Left).

    Args:
        label (str): The component tag.
        pins (tuple): A tuple of 3 pin numbers (Common, NC, NO).
        inverted (bool): If True, Common is at Top, NC/NO at Bottom.

    Returns:
        Symbol: The symbol.
    """

    h_half = GRID_SIZE  # 5.0

    # Standard Orientation
    top_y = -GRID_SIZE / 2  # -2.5
    bot_y = GRID_SIZE / 2  # 2.5

    x_right = GRID_SIZE / 2  # 2.5
    x_left = -GRID_SIZE / 2  # -2.5

    style = standard_style()

    elements: List[Element] = []

    if not inverted:
        # Standard: Common (Input) - Bottom Right
        l_com = Line(Point(x_right, bot_y), Point(x_right, h_half), style)

        # NO (Output) - Top Right
        l_no = Line(Point(x_right, -h_half), Point(x_right, top_y), style)

        # NC (Output) - Top Left
        l_nc = Line(Point(x_left, -h_half), Point(x_left, top_y), style)

        # NC Seat (Top)
        nc_seat_end_x = 0
        seat_nc = Line(Point(x_left, top_y), Point(nc_seat_end_x, top_y), style)

        # Blade: Common (Bot Right) -> NC Seat (Top Center)
        blade_start = Point(x_right, bot_y)
        target_x = nc_seat_end_x
        target_y = top_y

        ports = {
            "1": Port("1", Point(x_right, h_half), Vector(0, 1)),  # Common (Bottom)
            "2": Port("2", Point(x_left, -h_half), Vector(0, -1)),  # NC (Top Left)
            "4": Port("4", Point(x_right, -h_half), Vector(0, -1)),  # NO (Top Right)
        }
    else:
        # Inverted: Common (Input) - Top Right
        # Common line goes UP from pivot
        l_com = Line(Point(x_right, top_y), Point(x_right, -h_half), style)

        # NO (Output) - Bottom Right
        l_no = Line(Point(x_right, bot_y), Point(x_right, h_half), style)

        # NC (Output) - Bottom Left
        l_nc = Line(Point(x_left, bot_y), Point(x_left, h_half), style)

        # NC Seat (Bottom)
        nc_seat_end_x = 0
        seat_nc = Line(Point(x_left, bot_y), Point(nc_seat_end_x, bot_y), style)

        # Blade: Common (Top Right) -> NC Seat (Bottom Center)
        blade_start = Point(x_right, top_y)
        target_x = nc_seat_end_x
        target_y = bot_y

        ports = {
            "1": Port("1", Point(x_right, -h_half), Vector(0, -1)),  # Common (Top)
            "2": Port("2", Point(x_left, h_half), Vector(0, 1)),  # NC (Bottom Left)
            "4": Port("4", Point(x_right, h_half), Vector(0, 1)),  # NO (Bottom Right)
        }

    # Calculate Blade (Shared Logic)
    dx = target_x - blade_start.x
    dy = target_y - blade_start.y
    length = (dx**2 + dy**2) ** 0.5

    extension = GRID_SIZE / 4
    new_length = length + extension
    scale = new_length / length

    blade_end = Point(blade_start.x + dx * scale, blade_start.y + dy * scale)
    blade = Line(blade_start, blade_end, style)

    elements.extend([l_com, l_no, l_nc, seat_nc, blade])

    if label:
        elements.append(standard_text(label, Point(0, 0)))

    if pins:
        # Expected tuple: (Common, NC, NO)
        p_labels = list(pins)
        while len(p_labels) < 3:
            p_labels.append("")

        common_pin, nc_pin, no_pin = p_labels[0], p_labels[1], p_labels[2]

        offset = 2.0  # mm

        if common_pin and "1" in ports:
            pos = ports["1"].position
            # Common aligns Right
            elements.append(
                Text(
                    content=common_pin,
                    position=Point(pos.x + offset, pos.y),
                    anchor="start",
                    font_size=TEXT_SIZE_PIN,
                    style=Style(
                        stroke="none",
                        fill=COLOR_BLACK,
                        font_family=TEXT_FONT_FAMILY_AUX,
                    ),
                )
            )

        if nc_pin and "2" in ports:
            pos = ports["2"].position
            # NC aligns Left
            elements.append(
                Text(
                    content=nc_pin,
                    position=Point(pos.x - offset, pos.y),
                    anchor="end",
                    font_size=TEXT_SIZE_PIN,
                    style=Style(
                        stroke="none",
                        fill=COLOR_BLACK,
                        font_family=TEXT_FONT_FAMILY_AUX,
                    ),
                )
            )

        if no_pin and "4" in ports:
            pos = ports["4"].position
            # NO aligns Right
            elements.append(
                Text(
                    content=no_pin,
                    position=Point(pos.x + offset, pos.y),
                    anchor="start",
                    font_size=TEXT_SIZE_PIN,
                    style=Style(
                        stroke="none",
                        fill=COLOR_BLACK,
                        font_family=TEXT_FONT_FAMILY_AUX,
                    ),
                )
            )

    return Symbol(elements, ports, label=label)


def multi_pole_spdt_symbol(
    poles: int = 3,
    label: str = "",
    pins: tuple = (),
) -> Symbol:
    """
    Create an IEC 60617 Multi-Pole SPDT Contact.

    Composed of N single SPDT contacts arranged horizontally.

    Args:
        poles: Number of poles.
        label: The component tag.
        pins: Pin numbers, 3 per pole (Common, NC, NO).
              Defaults to standard IEC numbering (11,12,14, 21,22,24, ...).

    Returns:
        Symbol with ports keyed as "{pole_index}_{type}":
        "1_com", "1_nc", "1_no", "2_com", etc.
    """
    expected = poles * 3
    if not pins:
        pins = tuple(
            f"{p}{s}" for p in range(1, poles + 1) for s in ("1", "2", "4")
        )
    if len(pins) < expected:
        pins = tuple(list(pins) + [""] * (expected - len(pins)))

    spacing = DEFAULT_POLE_SPACING * 4.0

    pole_syms = []
    all_elements = []
    for i in range(poles):
        p = spdt_contact_symbol(
            label=label if i == 0 else "", pins=pins[i * 3 : i * 3 + 3]
        )
        if i > 0:
            p = translate(p, spacing * i, 0)
        pole_syms.append(p)
        all_elements.extend(p.elements)

    new_ports = {}
    for i, p in enumerate(pole_syms):
        pole_id = str(i + 1)
        if "1" in p.ports:
            new_key = f"{pole_id}_com"
            new_ports[new_key] = replace(p.ports["1"], id=new_key)
        if "2" in p.ports:
            new_key = f"{pole_id}_nc"
            new_ports[new_key] = replace(p.ports["2"], id=new_key)
        if "4" in p.ports:
            new_key = f"{pole_id}_no"
            new_ports[new_key] = replace(p.ports["4"], id=new_key)

    return Symbol(all_elements, new_ports, label=label)


def three_pole_spdt_symbol(
    label: str = "",
    pins: tuple = ("11", "12", "14", "21", "22", "24", "31", "32", "34"),
) -> Symbol:
    """
    Create an IEC 60617 Three Pole SPDT Contact.

    Convenience wrapper around multi_pole_spdt_symbol for 3-pole contacts.

    Args:
        label: The component tag.
        pins: A tuple of 9 pin numbers (Common, NC, NO per pole).

    Returns:
        Symbol: The 3-pole symbol.
    """
    return multi_pole_spdt_symbol(poles=3, label=label, pins=pins)
