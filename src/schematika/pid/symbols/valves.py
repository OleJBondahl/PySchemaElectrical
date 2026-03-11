"""
ISO 14617 valve symbol factories.

Valve symbols use a bowtie (two triangles meeting at tips) as the base shape.
Size: ~15mm x 15mm (VALVE_SIZE from constants).
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
from schematika.pid.constants import PID_EQUIPMENT_STROKE, PID_LINE_WEIGHT, VALVE_SIZE

_PIPE_STYLE = Style(stroke="black", stroke_width=PID_LINE_WEIGHT, fill="none")
_BODY_STYLE = Style(stroke="black", stroke_width=PID_EQUIPMENT_STROKE, fill="none")
_FILL_STYLE = Style(stroke="black", stroke_width=PID_EQUIPMENT_STROKE, fill="black")
_TEXT_STYLE = Style(stroke="none", fill="black", font_family=TEXT_FONT_FAMILY)

# Half-size for triangle geometry
_H = VALVE_SIZE / 2  # 7.5mm


def _bowtie_polygons(fill_left: bool = False, fill_right: bool = False):
    """Return the two triangle polygons forming a bowtie valve body."""
    # Left triangle: tip at center (0,0), base at left edge x=-H
    left_tri = Polygon(
        points=[
            Point(-_H, -_H),
            Point(-_H, _H),
            Point(0.0, 0.0),
        ],
        style=_FILL_STYLE if fill_left else _BODY_STYLE,
    )
    # Right triangle: tip at center (0,0), base at right edge x=+H
    right_tri = Polygon(
        points=[
            Point(_H, -_H),
            Point(_H, _H),
            Point(0.0, 0.0),
        ],
        style=_FILL_STYLE if fill_right else _BODY_STYLE,
    )
    return left_tri, right_tri


def _valve_ports():
    """Standard inlet/outlet ports for a horizontal valve."""
    return {
        "in": Port("in", Point(-_H - 5.0, 0.0), Vector(-1, 0)),
        "out": Port("out", Point(_H + 5.0, 0.0), Vector(1, 0)),
    }


def _pipe_stubs():
    """Pipe stubs connecting external ports to valve body edges."""
    left_stub = Line(Point(-_H - 5.0, 0.0), Point(-_H, 0.0), _PIPE_STYLE)
    right_stub = Line(Point(_H, 0.0), Point(_H + 5.0, 0.0), _PIPE_STYLE)
    return left_stub, right_stub


def _label_text(label: str, y_offset: float = _H + 5.0):
    return Text(
        content=label,
        position=Point(0.0, y_offset),
        style=_TEXT_STYLE,
        anchor="middle",
        dominant_baseline="auto",
        font_size=TEXT_SIZE_MAIN,
    )


def gate_valve(label: str = "") -> Symbol:
    """ISO 14617 gate valve.

    Two triangles meeting at their tips (bowtie), open fill.

    Args:
        label: Component label/tag.

    Returns:
        Symbol with ports 'in' (left) and 'out' (right).
    """
    left_tri, right_tri = _bowtie_polygons()
    left_stub, right_stub = _pipe_stubs()

    elements = [left_tri, right_tri, left_stub, right_stub]
    if label:
        elements.append(_label_text(label))

    return Symbol(elements, _valve_ports(), label=label)


def globe_valve(label: str = "") -> Symbol:
    """ISO 14617 globe valve.

    Bowtie shape with a small circle at the center junction.

    Args:
        label: Component label/tag.

    Returns:
        Symbol with ports 'in' (left) and 'out' (right).
    """
    left_tri, right_tri = _bowtie_polygons()
    left_stub, right_stub = _pipe_stubs()

    center_circle = Circle(
        center=Point(0.0, 0.0),
        radius=1.5,
        style=_BODY_STYLE,
    )

    elements = [left_tri, right_tri, left_stub, right_stub, center_circle]
    if label:
        elements.append(_label_text(label))

    return Symbol(elements, _valve_ports(), label=label)


def control_valve(label: str = "") -> Symbol:
    """ISO 14617 control valve.

    Globe valve (bowtie + center circle) with a vertical actuator stem
    and a small triangle actuator symbol on top.

    Args:
        label: Component label/tag.

    Returns:
        Symbol with ports 'in' (left) and 'out' (right).
    """
    left_tri, right_tri = _bowtie_polygons()
    left_stub, right_stub = _pipe_stubs()

    center_circle = Circle(center=Point(0.0, 0.0), radius=1.5, style=_BODY_STYLE)

    # Actuator stem going up
    stem_top_y = -_H - 8.0
    stem = Line(Point(0.0, 0.0), Point(0.0, stem_top_y), _BODY_STYLE)

    # Actuator symbol: small inverted triangle at top of stem
    act_h = 4.0
    actuator = Polygon(
        points=[
            Point(-act_h, stem_top_y - act_h),
            Point(act_h, stem_top_y - act_h),
            Point(0.0, stem_top_y),
        ],
        style=_BODY_STYLE,
    )

    elements = [
        left_tri,
        right_tri,
        left_stub,
        right_stub,
        center_circle,
        stem,
        actuator,
    ]
    if label:
        elements.append(_label_text(label, y_offset=_H + 5.0))

    ports = _valve_ports()
    ports["actuator"] = Port(
        "actuator",
        Point(0.0, stem_top_y - act_h),
        Vector(0, -1),
    )

    return Symbol(elements, ports, label=label)


def check_valve(label: str = "") -> Symbol:
    """ISO 14617 check valve.

    Single triangle pointing in the flow direction (right), with a perpendicular
    seat bar at the tip.

    Args:
        label: Component label/tag.

    Returns:
        Symbol with ports 'in' (left) and 'out' (right).
    """
    # Triangle pointing right
    triangle = Polygon(
        points=[
            Point(-_H, -_H),
            Point(-_H, _H),
            Point(_H, 0.0),
        ],
        style=_BODY_STYLE,
    )

    # Seat: vertical line at right tip
    seat = Line(Point(_H, -_H), Point(_H, _H), _BODY_STYLE)

    left_stub, right_stub = _pipe_stubs()

    elements = [triangle, seat, left_stub, right_stub]
    if label:
        elements.append(_label_text(label))

    return Symbol(elements, _valve_ports(), label=label)


def ball_valve(label: str = "") -> Symbol:
    """ISO 14617 ball valve.

    Bowtie with a filled circle at the center (ball indicator).

    Args:
        label: Component label/tag.

    Returns:
        Symbol with ports 'in' (left) and 'out' (right).
    """
    left_tri, right_tri = _bowtie_polygons()
    left_stub, right_stub = _pipe_stubs()

    ball = Circle(
        center=Point(0.0, 0.0),
        radius=2.5,
        style=_FILL_STYLE,
    )

    elements = [left_tri, right_tri, left_stub, right_stub, ball]
    if label:
        elements.append(_label_text(label))

    return Symbol(elements, _valve_ports(), label=label)


def three_way_valve(label: str = "") -> Symbol:
    """ISO 14617 three-way valve.

    T-junction valve: bowtie on horizontal axis plus a branch port going downward.

    Args:
        label: Component label/tag.

    Returns:
        Symbol with ports 'in' (left), 'out_a' (right), 'out_b' (bottom).
    """
    left_tri, right_tri = _bowtie_polygons()
    left_stub, right_stub = _pipe_stubs()

    # Branch stub going downward
    branch_stub = Line(Point(0.0, 0.0), Point(0.0, _H + 5.0), _PIPE_STYLE)

    center_circle = Circle(center=Point(0.0, 0.0), radius=1.5, style=_BODY_STYLE)

    elements = [left_tri, right_tri, left_stub, right_stub, branch_stub, center_circle]
    if label:
        elements.append(_label_text(label))

    ports = {
        "in": Port("in", Point(-_H - 5.0, 0.0), Vector(-1, 0)),
        "out_a": Port("out_a", Point(_H + 5.0, 0.0), Vector(1, 0)),
        "out_b": Port("out_b", Point(0.0, _H + 5.0), Vector(0, 1)),
    }

    return Symbol(elements, ports, label=label)
