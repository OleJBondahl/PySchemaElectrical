import math

from pyschemaelectrical.model.core import Point, Port, Symbol, Vector
from pyschemaelectrical.model.primitives import Line
from pyschemaelectrical.utils.transform import (
    rotate,
    rotate_point,
    rotate_vector,
    translate,
)


class TestTransformUnit:
    def test_translate_point(self):
        p = Point(0, 0)
        p2 = translate(p, 10, 5)
        assert p2.x == 10
        assert p2.y == 5

    def test_translate_line(self):
        l = Line(Point(0,0), Point(1,1))
        l2 = translate(l, 2, 2)
        assert l2.start == Point(2,2)
        assert l2.end == Point(3,3)

    def test_translate_symbol_recursive(self):
        # Symbol containing a Line
        l = Line(Point(0,0), Point(1,1))
        port = Port("1", Point(0,0), Vector(1,0))
        sym = Symbol(elements=[l], ports={"1": port}, label="S1")

        sym2 = translate(sym, 10, 10)

        assert sym2.elements[0].start == Point(10,10)
        assert sym2.ports["1"].position == Point(10,10)

    def test_rotate_point(self):
        # Rotate (1,0) 90 deg around (0,0) -> (0,1)
        p = Point(1, 0)
        p_rot = rotate_point(p, 90, Point(0,0))
        assert math.isclose(p_rot.x, 0, abs_tol=1e-9)
        assert math.isclose(p_rot.y, 1, abs_tol=1e-9)

    def test_rotate_vector(self):
        v = Vector(1, 0)
        v_rot = rotate_vector(v, 90)
        assert math.isclose(v_rot.dx, 0, abs_tol=1e-9)
        assert math.isclose(v_rot.dy, 1, abs_tol=1e-9)

    def test_rotate_symbol_recursive(self):
        # Symbol with line from (0,0) to (1,0)
        l = Line(Point(0,0), Point(1,0))
        sym = Symbol(elements=[l], ports={}, label="S2")

        # Rotate 90 deg around (0,0)
        sym_rot = rotate(sym, 90, Point(0,0))

        l_rot = sym_rot.elements[0]
        assert math.isclose(l_rot.start.x, 0, abs_tol=1e-9)
        assert math.isclose(l_rot.start.y, 0, abs_tol=1e-9)
        assert math.isclose(l_rot.end.x, 0, abs_tol=1e-9)
        assert math.isclose(l_rot.end.y, 1, abs_tol=1e-9)
