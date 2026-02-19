import math

from pyschemaelectrical.model.constants import (
    COLOR_BLACK,
    DEFAULT_POLE_SPACING,
    GRID_SIZE,
    TEXT_FONT_FAMILY,
)
from pyschemaelectrical.model.core import Element, Point, Port, Style, Symbol, Vector
from pyschemaelectrical.model.parts import (
    PIN_LABEL_OFFSET_X,
    PIN_LABEL_OFFSET_Y_ADJUST,
    TEXT_FONT_FAMILY_AUX,
    TEXT_SIZE_PIN,
    create_pin_labels,
    standard_style,
    standard_text,
)
from pyschemaelectrical.model.primitives import Circle, Line, Text

"""
IEC 60617 Motor Symbols.

This module contains motor symbols following IEC 60617 standard:
- Three-phase AC motor (most common in industrial applications)
- Generic motor symbol
"""


def three_pole_motor_symbol(  # noqa: C901
    label: str = "", pins: tuple[str, ...] = ("U", "V", "W", "PE")
) -> Symbol:
    """
    Create an IEC 60617 Three-Phase AC Motor symbol.

    Symbol represents a 3-phase asynchronous motor (squirrel cage) - the most
    common type in industrial applications.

    Symbol Layout:
       U  V  W
       |  |  |
      +---------+
     (           )  |
     (    M      )  | PE
     (    3~     )  |
     (           )
      +---------+

    The three phase terminals (U, V, W) are centered on top with standard
    GRID_SIZE spacing. The PE (Protective Earth) terminal is positioned
    tangentially on the right side of the circle.

    Circle is sized to accommodate the pin layout with proper spacing.

    Args:
        label (str): The component tag (e.g. "-M1").
        pins (tuple): Pin designations (default: ("U", "V", "W", "PE")).
                      The first 3 pins are mapped Left, Center, Right on top.
                      The 4th pin (if present) is mapped to PE (right side).

    Returns:
        Symbol: The 3-phase motor symbol.
    """
    style = standard_style()

    # Pin spacing - use standard spacing to match terminals
    pin_spacing = DEFAULT_POLE_SPACING  # 10mm (2*GRID_SIZE)

    # Three phase pins at x = -5, 0, 5 (total span = 10mm)
    # Circle needs to accommodate this span on the top arc
    # For a chord of length 2*pin_spacing (10mm), we need sufficient radius
    # Using radius = 2 * pin_spacing gives good proportions
    radius = 2 * pin_spacing  # 10mm

    elements: list[Element] = []
    ports = {}

    # Main circle - centered at origin
    circle = Circle(center=Point(0, 0), radius=radius, style=style)
    elements.append(circle)

    # Add component tag inside the circle - centered using standard label style
    if label:
        # Use anchor="middle" to truly center the label
        label_text = Text(
            content=label,
            position=Point(0, 0),
            anchor="middle",
            font_size=5.0,
            style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY),
        )
        elements.append(label_text)

    # Pin labels from tuple
    pin_labels = list(pins) if pins else ["U", "V", "W", "PE"]

    terminal_length = pin_spacing  # 5mm lead length

    # Three phase terminals (U, V, W) on top arc
    # with DEFAULT_POLE_SPACING. Matches the
    # three-pole terminal symbol spacing.
    # U at x = -DEFAULT_POLE_SPACING (-5mm) - LEFTMOST
    # V at x = 0 (center)
    # W at x = +DEFAULT_POLE_SPACING (+5mm)
    # PE at x = 2*DEFAULT_POLE_SPACING (+10mm) - RIGHTMOST

    phase_x_positions = [
        -pin_spacing,  # U (left)
        0,  # V (center - top of circle)
        pin_spacing,  # W (right)
    ]

    for i, x_pos in enumerate(phase_x_positions):
        if i >= len(pin_labels):
            break

        pin_id = pin_labels[i]

        # Calculate y position on circle for this x position
        # Circle equation: x² + y² = r²
        # Solve for y (top half, so negative y): y = -sqrt(r² - x²)
        y_on_circle = -math.sqrt(radius**2 - x_pos**2)

        terminal_bottom = Point(x_pos, y_on_circle)
        terminal_top = Point(x_pos, y_on_circle - terminal_length)

        elements.append(Line(terminal_bottom, terminal_top, style))

        ports[pin_id] = Port(id=pin_id, position=terminal_top, direction=Vector(0, -1))

    # PE (Protective Earth) terminal - RIGHTMOST, tangent on the RIGHT side of circle
    if len(pin_labels) > 3:
        pe_label = pin_labels[3]

        # PE is at the rightmost point of the circle (90° to the right)
        # Position: (radius, 0) on the circle
        pe_x_on_circle = radius
        pe_y_on_circle = 0

        # Terminal pointing upward from there
        pe_terminal_bottom = Point(pe_x_on_circle, pe_y_on_circle)
        pe_terminal_top = Point(pe_x_on_circle, pe_y_on_circle - terminal_length)

        elements.append(Line(pe_terminal_bottom, pe_terminal_top, style))

        ports[pe_label] = Port(
            id=pe_label, position=pe_terminal_top, direction=Vector(0, -1)
        )

    # Add pin labels if provided
    if pins:
        # Manually create labels to ensure they match the
        # geometric order (Left -> Right).
        # create_pin_labels sorts by key, which scrambles
        # semantic ordering (e.g. U, V, W)
        for i, pin_text in enumerate(pin_labels):
            if not pin_text or pin_text not in ports:
                continue

            port = ports[pin_text]

            # Position logic
            # Default: Left (-X)
            pos_x = port.position.x - PIN_LABEL_OFFSET_X
            pos_y = port.position.y
            anchor = "end"

            # PE (4th pin) special handing - Place on RIGHT side
            if i == 3:
                pos_x = port.position.x + PIN_LABEL_OFFSET_X
                anchor = "start"

            # Adjustment for Up/Down direction
            if port.direction.dy < -0.1:  # UP
                pos_y += PIN_LABEL_OFFSET_Y_ADJUST
            elif port.direction.dy > 0.1:  # DOWN
                pos_y -= PIN_LABEL_OFFSET_Y_ADJUST

            elements.append(
                Text(
                    content=pin_text,
                    position=Point(pos_x, pos_y),
                    anchor=anchor,
                    font_size=TEXT_SIZE_PIN,
                    style=Style(
                        stroke="none",
                        fill=COLOR_BLACK,
                        font_family=TEXT_FONT_FAMILY_AUX,
                    ),
                )
            )

    return Symbol(elements, ports, label=label)


def motor_symbol(label: str = "", pins: tuple[str, ...] = ()) -> Symbol:
    """
    Create an IEC 60617 generic single-phase Motor symbol.

    Symbol Layout:
         |
        ---
       (   )
       ( M )
       (   )
        ---
         |

    Dimensions:
        Diameter: 15mm (3 * GRID_SIZE)

    Args:
        label (str): The component tag (e.g. "-M1").
        pins (tuple): Pin numbers (e.g. ("1", "2")).

    Returns:
        Symbol: The motor symbol.
    """
    style = standard_style()

    # Motor circle diameter
    diameter = 3 * GRID_SIZE  # 15mm
    radius = diameter / 2

    elements: list[Element] = []

    # Main circle
    circle = Circle(center=Point(0, 0), radius=radius, style=style)
    elements.append(circle)

    # Add "M" text
    m_text = Text(
        content="M",
        position=Point(0, 0),
        anchor="middle",
        font_size=4.0,
        style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY),
    )
    elements.append(m_text)

    # Terminal leads
    terminal_length = GRID_SIZE  # 5mm

    # Top terminal
    elements.append(Line(Point(0, -radius), Point(0, -radius - terminal_length), style))

    # Bottom terminal
    elements.append(Line(Point(0, radius), Point(0, radius + terminal_length), style))

    # Ports
    ports = {
        "1": Port("1", Point(0, -radius - terminal_length), Vector(0, -1)),
        "2": Port("2", Point(0, radius + terminal_length), Vector(0, 1)),
    }

    # Label
    if label:
        elements.append(standard_text(label, Point(radius + GRID_SIZE / 2, 0)))

    # Pin labels
    if pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)
