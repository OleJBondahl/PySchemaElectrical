"""
ISO 14617 vessel and heat exchanger symbol factories.
"""

from schematika.core import Circle, Line, Point, Port, Style, Symbol, Text, Vector
from schematika.core.constants import LINE_WIDTH_THIN, TEXT_FONT_FAMILY, TEXT_SIZE_MAIN
from schematika.pid.constants import PID_LINE_WEIGHT

_PIPE_STYLE = Style(stroke="black", stroke_width=PID_LINE_WEIGHT, fill="none")
_BODY_STYLE = Style(stroke="black", stroke_width=LINE_WIDTH_THIN, fill="none")
_DASH_STYLE = Style(
    stroke="black", stroke_width=LINE_WIDTH_THIN, fill="none", stroke_dasharray="3,2"
)
_TEXT_STYLE = Style(stroke="none", fill="black", font_family=TEXT_FONT_FAMILY)


def tank(label: str = "", kind: str = "open") -> Symbol:
    """ISO 14617 tank/vessel.

    Rectangle 30mm wide x 40mm tall.
    Open top (kind="open") uses a dashed top line.
    Closed top (kind="closed") uses a solid top line.

    Args:
        label: Component label/tag (e.g., "T-001").
        kind: "open" or "closed".

    Returns:
        Symbol with ports 'inlet' (top-left), 'outlet' (bottom-right),
        'drain' (bottom-center), 'vent' (top-center).
    """
    w = 15.0  # half-width = 15mm, total 30mm
    h = 20.0  # half-height = 20mm, total 40mm

    # Body sides and bottom (always solid)
    left = Line(Point(-w, -h), Point(-w, h), _BODY_STYLE)
    right = Line(Point(w, -h), Point(w, h), _BODY_STYLE)
    bottom = Line(Point(-w, h), Point(w, h), _BODY_STYLE)

    # Top line: dashed for open, solid for closed
    top_style = _DASH_STYLE if kind == "open" else _BODY_STYLE
    top = Line(Point(-w, -h), Point(w, -h), top_style)

    # Inlet stub at top-left
    inlet_stub = Line(Point(-w, -h + 5.0), Point(-w - 5.0, -h + 5.0), _PIPE_STYLE)

    # Outlet stub at bottom-right
    outlet_stub = Line(Point(w, h - 5.0), Point(w + 5.0, h - 5.0), _PIPE_STYLE)

    # Drain stub at bottom-center
    drain_stub = Line(Point(0.0, h), Point(0.0, h + 5.0), _PIPE_STYLE)

    # Vent stub at top-center
    vent_stub = Line(Point(0.0, -h), Point(0.0, -h - 5.0), _PIPE_STYLE)

    elements = [
        left,
        right,
        bottom,
        top,
        inlet_stub,
        outlet_stub,
        drain_stub,
        vent_stub,
    ]

    if label:
        elements.append(
            Text(
                content=label,
                position=Point(0.0, 0.0),
                style=_TEXT_STYLE,
                anchor="middle",
                dominant_baseline="middle",
                font_size=TEXT_SIZE_MAIN,
            )
        )

    ports = {
        "inlet": Port("inlet", Point(-w - 5.0, -h + 5.0), Vector(-1, 0)),
        "outlet": Port("outlet", Point(w + 5.0, h - 5.0), Vector(1, 0)),
        "drain": Port("drain", Point(0.0, h + 5.0), Vector(0, 1)),
        "vent": Port("vent", Point(0.0, -h - 5.0), Vector(0, -1)),
    }

    return Symbol(elements, ports, label=label)


def heat_exchanger(label: str = "", kind: str = "shell_tube") -> Symbol:
    """ISO 14617 shell-and-tube heat exchanger.

    Circle (~25mm diameter) with internal lines showing tube passes.

    Args:
        label: Component label/tag (e.g., "HX-001").
        kind: Currently only "shell_tube" is implemented.

    Returns:
        Symbol with ports 'shell_in' (left), 'shell_out' (right),
        'tube_in' (bottom), 'tube_out' (top).
    """
    radius = 12.5  # 25mm diameter

    body = Circle(center=Point(0.0, 0.0), radius=radius, style=_BODY_STYLE)

    # Shell-side: horizontal stubs (left and right)
    shell_in_x = -radius - 5.0
    shell_out_x = radius + 5.0
    shell_in_line = Line(Point(shell_in_x, 0.0), Point(-radius, 0.0), _PIPE_STYLE)
    shell_out_line = Line(Point(radius, 0.0), Point(shell_out_x, 0.0), _PIPE_STYLE)

    # Tube-side: vertical stubs (top and bottom)
    tube_in_y = radius + 5.0
    tube_out_y = -radius - 5.0
    tube_in_line = Line(Point(0.0, radius), Point(0.0, tube_in_y), _PIPE_STYLE)
    tube_out_line = Line(Point(0.0, -radius), Point(0.0, tube_out_y), _PIPE_STYLE)

    # Internal tube pass indicator (two curved lines suggesting U-tube or two-pass)
    # Represented as two horizontal lines offset vertically inside the circle
    inner_offset = 3.5
    inner_len = radius * 0.6
    tube_pass_top = Line(
        Point(-inner_len, -inner_offset),
        Point(inner_len, -inner_offset),
        _BODY_STYLE,
    )
    tube_pass_bot = Line(
        Point(-inner_len, inner_offset),
        Point(inner_len, inner_offset),
        _BODY_STYLE,
    )
    # Connecting line on the right side (U-turn)
    tube_return = Line(
        Point(inner_len, -inner_offset),
        Point(inner_len, inner_offset),
        _BODY_STYLE,
    )

    elements = [
        body,
        shell_in_line,
        shell_out_line,
        tube_in_line,
        tube_out_line,
        tube_pass_top,
        tube_pass_bot,
        tube_return,
    ]

    if label:
        elements.append(
            Text(
                content=label,
                position=Point(0.0, radius + 8.0),
                style=_TEXT_STYLE,
                anchor="middle",
                dominant_baseline="auto",
                font_size=TEXT_SIZE_MAIN,
            )
        )

    ports = {
        "shell_in": Port("shell_in", Point(shell_in_x, 0.0), Vector(-1, 0)),
        "shell_out": Port("shell_out", Point(shell_out_x, 0.0), Vector(1, 0)),
        "tube_in": Port("tube_in", Point(0.0, tube_in_y), Vector(0, 1)),
        "tube_out": Port("tube_out", Point(0.0, tube_out_y), Vector(0, -1)),
    }

    return Symbol(elements, ports, label=label)
