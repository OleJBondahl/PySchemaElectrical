from pyschemaelectrical.model.constants import GRID_SIZE, GRID_SUBDIVISION
from pyschemaelectrical.model.core import Point, Port, Symbol, Vector
from pyschemaelectrical.model.parts import (
    box,
    create_pin_labels,
    standard_style,
    standard_text,
)
from pyschemaelectrical.model.primitives import Line

"""
IEC 60617 Coil Symbols.
"""


def coil_symbol(
    label: str = "", pins: tuple[str, ...] = (), show_terminals: bool = True
) -> Symbol:
    """
    Create an IEC 60617 Coil symbol (Square).

    Symbol Layout:
       |
      [ ]
       |

    Dimensions:
        Width: 10mm (2 * GRID_SIZE)
        Height: 10mm (2 * GRID_SIZE)

    Args:
        label (str): The component tag (e.g. "-K1").
        pins (tuple): Pin numbers (e.g. ("A1", "A2")).
        show_terminals (bool): Whether to draw leads and ports.

    Returns:
        Symbol: The coil symbol.
    """
    # Size: Width 10mm, Height 10mm.
    # Typically A1 (top) and A2 (bottom).
    width = 2 * GRID_SIZE
    height = GRID_SIZE

    body = box(Point(0, 0), width, height)
    style = standard_style()

    elements = [body]
    ports = {}

    if show_terminals:
        # Pins
        pin_len = GRID_SUBDIVISION
        top_y_box = -height / 2
        bot_y_box = height / 2

        top_y_port = top_y_box - pin_len
        bot_y_port = bot_y_box + pin_len

        l1 = Line(Point(0, top_y_box), Point(0, top_y_port), style)
        l2 = Line(Point(0, bot_y_box), Point(0, bot_y_port), style)

        ports = {
            "A1": Port("A1", Point(0, top_y_port), Vector(0, -1)),
            "A2": Port("A2", Point(0, bot_y_port), Vector(0, 1)),
        }
        elements.extend([l1, l2])

    if label:
        # Place label half grid more to the left because
        # coil is wider than other symbols
        elements.append(standard_text(label, Point(-GRID_SUBDIVISION, 0)))

    if pins and show_terminals:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)
