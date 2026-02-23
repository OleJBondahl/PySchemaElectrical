from pyschemaelectrical.model.constants import CT_ASSEMBLY_PINS, GRID_SIZE
from pyschemaelectrical.model.core import Point, Port, Symbol
from pyschemaelectrical.model.parts import standard_style
from pyschemaelectrical.model.primitives import Circle, Element, Line
from pyschemaelectrical.utils.transform import translate

from .blocks import terminal_box_symbol


def current_transducer_symbol() -> Symbol:
    """
    Create a Current Transducer Symbol.

    Visuals:
        - A circle centered on the wire (assumed origin 0,0).
        - A line extending to the left from the left edge of the circle.
        - No pin numbers.
        - No connections (ports).

    Dimensions:
        - Circle Radius: GRID_SIZE / 2 (2.5mm) -> Diameter 5mm (1 Grid).
        - Line Length: 1 Grid unit (5mm)? Or just "out to the left".

    Returns:
        Symbol: The symbol.
    """
    style = standard_style()

    # Circle
    radius = GRID_SIZE / 2
    circle = Circle(Point(0, 0), radius, style)

    # Line
    # From left edge (-radius, 0) to left (-radius - length, 0)
    line_length = GRID_SIZE
    line_start = Point(-radius, 0)
    line_end = Point(-radius - line_length, 0)
    line = Line(line_start, line_end, style)

    elements: list[Element] = [circle, line]

    # No ports
    ports: dict[str, Port] = {}

    return Symbol(elements, ports, label="")


def current_transducer_assembly_symbol(
    label: str = "", pins: tuple[str, ...] = CT_ASSEMBLY_PINS
) -> Symbol:
    """
    Create a Current Transducer Assembly.

    Combines:
    - A Current Transducer Symbol (Circle on wire).
    - A Rectangular Terminal Box (to the left).

    The line from the transducer hits the right side of the box.

    Args:
        label (str): Label for the box (or assembly).
        pins (tuple[str, ...]): Pin numbers for the terminal box.

    Returns:
        Symbol: The combined symbol. Origin at the Transducer center.
    """

    # 1. Transducer (Origin 0,0)
    ct = current_transducer_symbol()

    # 2. Terminal Box
    # "Line from transducer hits the side of the box"
    # Transducer line goes from (-2.5, 0) to (-7.5, 0).
    # Box Right Edge needs to be at (-7.5, 0).
    # Box Vertical Center should be at Y=0.

    box_sym = terminal_box_symbol(label=label, pins=pins)

    # Calculate Box Dimensions to determine offset
    # Box Origin is at Top-Left Pin (0,0 of box local coords).
    # Box Center Y = 2.5.
    # We want Box Local Y=2.5 to be at Global Y=0. -> Shift Y = -2.5.

    # Box Right Edge X (local) = span + padding
    # span = (num_pins - 1) * DEFAULT_POLE_SPACING
    # padding = 2.5
    from pyschemaelectrical.model.constants import DEFAULT_POLE_SPACING

    span = (len(pins) - 1) * DEFAULT_POLE_SPACING
    box_right_edge_x_local = span + (GRID_SIZE / 2)

    # We want Global X of Right Edge to be -7.5 (Transducer Line End)
    # Global X = Box Origin X + Box Right Edge X Local
    # -7.5 = Box Origin X + box_right_edge_x_local
    # Box Origin X = -7.5 - box_right_edge_x_local

    shift_x = (
        -7.5 - box_right_edge_x_local
    )  # -7.5 because line extends 5mm from -2.5 circle edge
    shift_y = -GRID_SIZE / 2  # -2.5

    box_placed = translate(box_sym, shift_x, shift_y)

    # Combine
    # Note: Terminal Box ports will be shifted.
    # Transducer has no ports.

    combined_elements = ct.elements + box_placed.elements
    combined_ports = box_placed.ports  # Transducer has none

    # The label needs to be passed carefully.
    # box_sym already rendered the label? Yes.
    # terminal_box puts label at (0,0) of box.
    # If we translate box, label moves with it.

    return Symbol(combined_elements, combined_ports, label=label)
