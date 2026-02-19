"""
Component parts and factory functions for electrical symbols.

This module provides reusable parts and factory functions for building
electrical symbols according to IEC 60617 standards. It includes:
- Standard styling and text formatting functions
- Terminal and box primitives
- Pin label creation
- Three-pole symbol factory for creating multi-pole components

All constants are imported from the constants module.
"""

from dataclasses import replace
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from pyschemaelectrical.model.primitives import Line

from pyschemaelectrical.utils.transform import translate

from .constants import (
    COLOR_BLACK,
    DEFAULT_POLE_SPACING,
    GRID_SIZE,
    LINE_WIDTH_THIN,
    PIN_LABEL_OFFSET_X,
    PIN_LABEL_OFFSET_Y_ADJUST,
    TERMINAL_RADIUS,
    TERMINAL_TEXT_OFFSET_X,
    TERMINAL_TEXT_SIZE,
    TEXT_FONT_FAMILY,
    TEXT_FONT_FAMILY_AUX,
    TEXT_OFFSET_X,
    TEXT_SIZE_MAIN,
    TEXT_SIZE_PIN,
)
from .core import Point, Style, Symbol
from .primitives import Circle, Element, Polygon, Text


def standard_style(filled: bool = False) -> Style:
    """
    Create a standard style for symbols.

    Args:
        filled (bool): Whether the element should be filled (black) or not (none).

    Returns:
        Style: The configured style object.
    """
    return Style(
        stroke=COLOR_BLACK,
        stroke_width=LINE_WIDTH_THIN,
        fill=COLOR_BLACK if filled else "none",
    )


def create_pin_label_text(
    content: str,
    position: Point,
    anchor: str = "start",
) -> "Text":
    """Create a styled pin-label text element.

    Args:
        content: The pin label string.
        position: Where to place the text.
        anchor: Text anchor ('start', 'middle', 'end').

    Returns:
        A Text element with standard pin label styling.
    """
    from pyschemaelectrical.model.primitives import Text

    return Text(
        content=content,
        position=position,
        font_size=TEXT_SIZE_PIN,
        style=Style(
            stroke="none",
            fill=COLOR_BLACK,
            font_family=TEXT_FONT_FAMILY_AUX,
        ),
        anchor=anchor,
    )


def standard_text(content: str, parent_origin: Point, label_pos: str = "left") -> Text:
    """
    Create component label text formatted according to standards.

    Args:
        content (str): The text content (e.g. "-K1").
        parent_origin (Point): The origin of the parent symbol.
        label_pos (str): 'left' or 'right' of the symbol.

    Returns:
        Text: The configured text element.
    """
    if label_pos == "right":
        pos = Point(parent_origin.x - TEXT_OFFSET_X, parent_origin.y)
        anchor = "start"
    else:
        pos = Point(parent_origin.x + TEXT_OFFSET_X, parent_origin.y)
        anchor = "end"

    return Text(
        content=content,
        position=pos,
        anchor=anchor,
        font_size=TEXT_SIZE_MAIN,
        style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY),
    )


def terminal_text(
    content: str, parent_origin: Point, label_pos: str = "left"
) -> Text:
    """
    Create terminal label text — smaller and further from the symbol
    than standard_text to avoid collision with pin numbers.
    """
    if label_pos == "right":
        pos = Point(parent_origin.x - TERMINAL_TEXT_OFFSET_X, parent_origin.y)
        anchor = "start"
    else:
        pos = Point(parent_origin.x + TERMINAL_TEXT_OFFSET_X, parent_origin.y)
        anchor = "end"

    return Text(
        content=content,
        position=pos,
        anchor=anchor,
        font_size=TERMINAL_TEXT_SIZE,
        style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY),
    )


def terminal_circle(
    center: Point | None = None, filled: bool = False
) -> Element:
    """
    Create a standard connection terminal circle.

    Args:
        center: Center of the terminal. Defaults to Point(0, 0) if None.
        filled (bool): Whether it is filled (e.g. for
            potential connection points vs loose ends).

    Returns:
        Element: The circle element.
    """
    if center is None:
        center = Point(0, 0)
    return Circle(center, TERMINAL_RADIUS, standard_style(filled))


def create_extended_blade(
    start: Point,
    target: Point,
    style: Style,
    extension: float = GRID_SIZE / 4,
) -> "Line":
    """
    Create a blade line extended past the target by `extension` mm.

    Used for NC and SPDT contact blade geometry. If start and target
    coincide (zero length), returns a zero-length line.

    Args:
        start: Blade start point.
        target: Point the blade passes through.
        style: Line style.
        extension: How far past target to extend (default: GRID_SIZE/4).

    Returns:
        Line from start to the extended endpoint.
    """
    from pyschemaelectrical.model.primitives import Line

    dx = target.x - start.x
    dy = target.y - start.y
    length = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return Line(start, target, style)
    scale = (length + extension) / length
    end = Point(start.x + dx * scale, start.y + dy * scale)
    return Line(start, end, style)


def box(center: Point, width: float, height: float, filled: bool = False) -> Element:
    """
    Create a rectangular box centered at a point.

    Args:
        center (Point): Center of the box.
        width (float): Width of the box.
        height (float): Height of the box.
        filled (bool): Whether to fill the box.

    Returns:
        Element: A Polygon element representing the box.
    """
    half_w = width / 2
    half_h = height / 2

    x1, y1 = center.x - half_w, center.y - half_h
    x2, y2 = center.x + half_w, center.y + half_h

    # Create points for Polygon
    p1 = Point(x1, y1)
    p2 = Point(x2, y1)
    p3 = Point(x2, y2)
    p4 = Point(x1, y2)

    return Polygon(points=[p1, p2, p3, p4], style=standard_style(filled))


def create_pin_labels(ports: dict[str, Any], pins: tuple[str, ...]) -> list[Text]:
    """
    Generate text labels for pins based on ports.

    Args:
        ports (dict[str, Port]): The ports dictionary of the symbol.
        pins (tuple[str, ...]): Pin labels to assign (e.g. ("13", "14")).
                                Use empty string "" to skip label (port still exists).

    Returns:
        list[Text]: A list of Text elements for the pin numbers.

    Note:
        Labels are assigned in port insertion order.
    """
    labels = []
    # Sort port keys to have deterministic mapping
    # Use insertion order (Python 3.7+ dict ordering) instead of alphabetical
    p_keys = list(ports.keys())

    for i, p_key in enumerate(p_keys):
        if i >= len(pins):
            break

        p_text = str(pins[i])

        # Skip creating label if pin text is empty
        if not p_text:
            continue

        port = ports[p_key]

        # Position logic
        # Default: Left (-X)
        pos_x = port.position.x - PIN_LABEL_OFFSET_X
        pos_y = port.position.y

        # Inward shift based on direction
        # If dir is UP (0, -1), move DOWN (y+)
        if port.direction.dy < -0.1:  # UP
            pos_y += PIN_LABEL_OFFSET_Y_ADJUST
        elif port.direction.dy > 0.1:  # DOWN
            pos_y -= PIN_LABEL_OFFSET_Y_ADJUST

        labels.append(
            Text(
                content=p_text,
                position=Point(pos_x, pos_y),
                anchor="end",
                font_size=TEXT_SIZE_PIN,
                style=Style(
                    stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX
                ),
            )
        )

    return labels


def _add_remapped_ports(
    symbol: Symbol, in_key: str, out_key: str, port_ids: tuple[str, str], target: dict
) -> None:
    """Add ports from *symbol* to *target* with remapped IDs.

    For each key (*in_key*, *out_key*) found in *symbol.ports*, the
    corresponding port is copied into *target* under the ID taken from
    *port_ids*.

    Args:
        symbol: Source symbol whose ports are being remapped.
        in_key: Port key in *symbol* for the input port.
        out_key: Port key in *symbol* for the output port.
        port_ids: Two-element tuple of new port IDs (input, output).
        target: Mutable dict that collects the remapped ports.
    """
    if in_key in symbol.ports:
        p = symbol.ports[in_key]
        new_id = port_ids[0]
        target[new_id] = replace(p, id=new_id)
    if out_key in symbol.ports:
        p = symbol.ports[out_key]
        new_id = port_ids[1]
        target[new_id] = replace(p, id=new_id)


def pad_pins(pins: tuple[str, ...], count: int, fill: str = "") -> list[str]:
    """Pad a pin tuple to *count* entries with *fill* value."""
    result = list(pins)
    while len(result) < count:
        result.append(fill)
    return result


def three_pole_factory(
    single_pole_func: Callable[..., Symbol],
    label: str = "",
    pins: tuple[str, ...] = ("1", "2", "3", "4", "5", "6"),
    pole_spacing: float = DEFAULT_POLE_SPACING,
) -> Symbol:
    """
    Factory to create a three pole symbol from a single pole function.

    Args:
        single_pole_func (Callable): A function that returns a single pole Symbol.
        label (str): The label for the composite symbol (e.g. "-Q1").
        pins (tuple[str, ...]): A tuple of 6 pin labels (use "" to hide label).
        pole_spacing (float): Horizontal spacing between poles.

    Returns:
        Symbol: The combined 3-pole symbol.

    Raises:
        ValueError: If pins tuple does not have exactly 6 elements.
    """
    if len(pins) != 6:
        raise ValueError(f"Three pole symbol requires 6 pin labels, got {len(pins)}")

    # Pole 1
    p1 = single_pole_func(label=label, pins=(pins[0], pins[1]))

    # Pole 2
    p2 = single_pole_func(label="", pins=(pins[2], pins[3]))
    p2 = translate(p2, pole_spacing, 0)

    # Pole 3
    p3 = single_pole_func(label="", pins=(pins[4], pins[5]))
    p3 = translate(p3, pole_spacing * 2, 0)

    # Combine elements
    all_elements = p1.elements + p2.elements + p3.elements

    new_ports: dict = {}

    # Use fixed port IDs (1-6) regardless of pin labels
    # This ensures ports always exist even if pin labels are empty
    _add_remapped_ports(p1, "1", "2", ("1", "2"), new_ports)
    _add_remapped_ports(p2, "1", "2", ("3", "4"), new_ports)
    _add_remapped_ports(p3, "1", "2", ("5", "6"), new_ports)

    return Symbol(elements=all_elements, ports=new_ports, label=label)


def two_pole_factory(
    single_pole_func: Callable[..., Symbol],
    label: str = "",
    pins: tuple[str, ...] = ("1", "2", "3", "4"),
    pole_spacing: float = DEFAULT_POLE_SPACING,
) -> Symbol:
    """
    Factory to create a two pole symbol from a single pole function.

    Args:
        single_pole_func (Callable): A function that returns a single pole Symbol.
        label (str): The label for the composite symbol (e.g. "-F1").
        pins (tuple[str, ...]): A tuple of 4 pin labels.
        pole_spacing (float): Horizontal spacing between poles.

    Returns:
        Symbol: The combined 2-pole symbol.
    """
    if len(pins) != 4:
        raise ValueError(f"Two pole symbol requires 4 pin labels, got {len(pins)}")

    # Pole 1
    p1 = single_pole_func(label=label, pins=(pins[0], pins[1]))

    # Pole 2
    p2 = single_pole_func(label="", pins=(pins[2], pins[3]))
    p2 = translate(p2, pole_spacing, 0)

    # Combine elements
    all_elements = p1.elements + p2.elements

    new_ports: dict = {}

    # Use fixed port IDs (1-4)
    _add_remapped_ports(p1, "1", "2", ("1", "2"), new_ports)
    _add_remapped_ports(p2, "1", "2", ("3", "4"), new_ports)

    return Symbol(elements=all_elements, ports=new_ports, label=label)
