"""
ISO 14617 piping primitive symbol factories.
"""

from schematika.core import Line, Point, Port, Style, Symbol, Text, Vector
from schematika.core.constants import TEXT_FONT_FAMILY, TEXT_SIZE_MAIN
from schematika.pid.constants import PID_EQUIPMENT_STROKE, PID_LINE_WEIGHT

_PIPE_STYLE = Style(stroke="black", stroke_width=PID_LINE_WEIGHT, fill="none")
_BODY_STYLE = Style(stroke="black", stroke_width=PID_EQUIPMENT_STROKE, fill="none")
_TEXT_STYLE = Style(stroke="none", fill="black", font_family=TEXT_FONT_FAMILY)


def pipe_segment(length: float = 50.0, label: str = "") -> Symbol:
    """Horizontal pipe segment.

    Args:
        length: Length of the pipe segment in mm. Default 50mm.
        label: Optional label displayed above the pipe.

    Returns:
        Symbol with ports 'in' (left) and 'out' (right).
    """
    half = length / 2.0
    pipe = Line(Point(-half, 0.0), Point(half, 0.0), _PIPE_STYLE)

    elements = [pipe]

    if label:
        elements.append(
            Text(
                content=label,
                position=Point(0.0, -4.0),
                style=_TEXT_STYLE,
                anchor="middle",
                dominant_baseline="auto",
                font_size=TEXT_SIZE_MAIN,
            )
        )

    ports = {
        "in": Port("in", Point(-half, 0.0), Vector(-1, 0)),
        "out": Port("out", Point(half, 0.0), Vector(1, 0)),
    }

    return Symbol(elements, ports, label=label)


def pipe_tee() -> Symbol:
    """T-junction for pipe branching.

    A horizontal pipe with a downward branch at the center.

    Returns:
        Symbol with ports 'in' (left), 'out' (right), 'branch' (bottom).
    """
    half = 10.0
    branch_len = 10.0

    horizontal = Line(Point(-half, 0.0), Point(half, 0.0), _PIPE_STYLE)
    branch = Line(Point(0.0, 0.0), Point(0.0, branch_len), _PIPE_STYLE)

    elements = [horizontal, branch]

    ports = {
        "in": Port("in", Point(-half, 0.0), Vector(-1, 0)),
        "out": Port("out", Point(half, 0.0), Vector(1, 0)),
        "branch": Port("branch", Point(0.0, branch_len), Vector(0, 1)),
    }

    return Symbol(elements, ports, label=None)


def pipe_reducer(label: str = "") -> Symbol:
    """Pipe reducer / concentric reducer.

    Trapezoidal shape: wider on the left (inlet), narrower on the right (outlet).
    Width 20mm, inlet height 10mm, outlet height 5mm.

    Args:
        label: Optional component label.

    Returns:
        Symbol with ports 'in' (left, wider) and 'out' (right, narrower).
    """
    length = 10.0  # horizontal span
    h_in = 5.0  # half-height at inlet side
    h_out = 2.5  # half-height at outlet side

    # Trapezoid outline
    top_line = Line(Point(-length, -h_in), Point(length, -h_out), _BODY_STYLE)
    bot_line = Line(Point(-length, h_in), Point(length, h_out), _BODY_STYLE)
    left_cap = Line(Point(-length, -h_in), Point(-length, h_in), _BODY_STYLE)
    right_cap = Line(Point(length, -h_out), Point(length, h_out), _BODY_STYLE)

    # Pipe stubs
    in_stub = Line(Point(-length - 5.0, 0.0), Point(-length, 0.0), _PIPE_STYLE)
    out_stub = Line(Point(length, 0.0), Point(length + 5.0, 0.0), _PIPE_STYLE)

    elements = [top_line, bot_line, left_cap, right_cap, in_stub, out_stub]

    if label:
        elements.append(
            Text(
                content=label,
                position=Point(0.0, h_in + 4.0),
                style=_TEXT_STYLE,
                anchor="middle",
                dominant_baseline="auto",
                font_size=TEXT_SIZE_MAIN,
            )
        )

    ports = {
        "in": Port("in", Point(-length - 5.0, 0.0), Vector(-1, 0)),
        "out": Port("out", Point(length + 5.0, 0.0), Vector(1, 0)),
    }

    return Symbol(elements, ports, label=label)


def pipe_cap() -> Symbol:
    """Pipe end cap.

    A short stub ending in a perpendicular cap line.

    Returns:
        Symbol with port 'in' (left).
    """
    stub_len = 5.0
    cap_h = 3.0  # half-height of the cap bar

    stub = Line(Point(-stub_len, 0.0), Point(0.0, 0.0), _PIPE_STYLE)
    cap = Line(Point(0.0, -cap_h), Point(0.0, cap_h), _BODY_STYLE)

    elements = [stub, cap]

    ports = {
        "in": Port("in", Point(-stub_len, 0.0), Vector(-1, 0)),
    }

    return Symbol(elements, ports, label=None)
