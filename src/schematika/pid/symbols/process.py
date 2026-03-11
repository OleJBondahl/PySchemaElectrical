"""
ISO 14617 process equipment symbol factories.
"""

from schematika.core import (
    Circle,
    Line,
    Point,
    Polygon,
    Port,
    Style,
    Symbol,
    Text,
    Vector,
)
from schematika.core.constants import TEXT_FONT_FAMILY, TEXT_SIZE_MAIN
from schematika.pid.constants import PID_EQUIPMENT_STROKE, PID_LINE_WEIGHT

_PIPE_STYLE = Style(stroke="black", stroke_width=PID_LINE_WEIGHT, fill="none")
_BODY_STYLE = Style(stroke="black", stroke_width=PID_EQUIPMENT_STROKE, fill="none")
_FILL_STYLE = Style(stroke="black", stroke_width=PID_EQUIPMENT_STROKE, fill="black")
_TEXT_STYLE = Style(stroke="none", fill="black", font_family=TEXT_FONT_FAMILY)


def centrifugal_pump(label: str = "") -> Symbol:
    """ISO 14617 centrifugal pump symbol.

    A circle (~20mm diameter) with a tangential discharge.
    Inlet on the left (port 'inlet'), outlet exits from the top (port 'outlet').

    Args:
        label: Component label/tag (e.g., "P-001").

    Returns:
        Symbol with ports 'inlet' (left) and 'outlet' (top-right).
    """
    radius = 10.0  # 20mm diameter circle

    # Circle body centered at origin
    body = Circle(center=Point(0.0, 0.0), radius=radius, style=_BODY_STYLE)

    # Inlet stub: horizontal line from left edge toward the circle (port attachment)
    inlet_x = -radius - 5.0
    inlet_line = Line(
        start=Point(inlet_x, 0.0),
        end=Point(-radius, 0.0),
        style=_PIPE_STYLE,
    )

    # Outlet stub: vertical line from top edge upward (tangential discharge)
    outlet_y = -radius - 5.0
    outlet_line = Line(
        start=Point(radius * 0.5, -radius),
        end=Point(radius * 0.5, outlet_y),
        style=_PIPE_STYLE,
    )

    # Small internal arrow/impeller indicator (diagonal line through center)
    impeller = Line(
        start=Point(-radius * 0.5, radius * 0.3),
        end=Point(radius * 0.3, -radius * 0.5),
        style=_BODY_STYLE,
    )

    elements = [body, inlet_line, outlet_line, impeller]

    if label:
        elements.append(
            Text(
                content=label,
                position=Point(0.0, radius + 5.0),
                style=_TEXT_STYLE,
                anchor="middle",
                dominant_baseline="auto",
                font_size=TEXT_SIZE_MAIN,
            )
        )

    ports = {
        "inlet": Port("inlet", Point(inlet_x, 0.0), Vector(-1, 0)),
        "outlet": Port("outlet", Point(radius * 0.5, outlet_y), Vector(0, -1)),
    }

    return Symbol(elements, ports, label=label)


def positive_displacement_pump(label: str = "") -> Symbol:
    """ISO 14617 positive displacement pump.

    Circle (~20mm diameter) with an internal triangular arrow pointing rightward.

    Args:
        label: Component label/tag.

    Returns:
        Symbol with ports 'inlet' (left) and 'outlet' (right).
    """
    radius = 10.0

    body = Circle(center=Point(0.0, 0.0), radius=radius, style=_BODY_STYLE)

    # Inlet stub
    inlet_x = -radius - 5.0
    inlet_line = Line(
        start=Point(inlet_x, 0.0),
        end=Point(-radius, 0.0),
        style=_PIPE_STYLE,
    )

    # Outlet stub
    outlet_x = radius + 5.0
    outlet_line = Line(
        start=Point(radius, 0.0),
        end=Point(outlet_x, 0.0),
        style=_PIPE_STYLE,
    )

    # Internal triangle pointing right (flow direction indicator)
    tri_size = 5.0
    triangle = Polygon(
        points=[
            Point(-tri_size * 0.5, -tri_size * 0.5),
            Point(-tri_size * 0.5, tri_size * 0.5),
            Point(tri_size * 0.5, 0.0),
        ],
        style=_FILL_STYLE,
    )

    elements = [body, inlet_line, outlet_line, triangle]

    if label:
        elements.append(
            Text(
                content=label,
                position=Point(0.0, radius + 5.0),
                style=_TEXT_STYLE,
                anchor="middle",
                dominant_baseline="auto",
                font_size=TEXT_SIZE_MAIN,
            )
        )

    ports = {
        "inlet": Port("inlet", Point(inlet_x, 0.0), Vector(-1, 0)),
        "outlet": Port("outlet", Point(outlet_x, 0.0), Vector(1, 0)),
    }

    return Symbol(elements, ports, label=label)
