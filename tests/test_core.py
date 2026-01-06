
import pytest
from dataclasses import FrozenInstanceError
from iec_lib.core import Vector, Point, Style, Element, Port, Symbol

class TestCore:
    def test_vector_creation(self):
        v = Vector(1.0, 2.0)
        assert v.dx == 1.0
        assert v.dy == 2.0

    def test_vector_operations(self):
        v1 = Vector(1, 2)
        v2 = Vector(3, 4)
        
        # Test addition
        v3 = v1 + v2
        assert v3.dx == 4
        assert v3.dy == 6
        
        # Test scalar multiplication
        v4 = v1 * 2
        assert v4.dx == 2
        assert v4.dy == 4

    def test_point_creation(self):
        p = Point(10.0, 20.0)
        assert p.x == 10.0
        assert p.y == 20.0

    def test_point_operations(self):
        p1 = Point(10, 20)
        v = Vector(5, 5)
        
        # Point + Vector -> Point
        p2 = p1 + v
        assert isinstance(p2, Point)
        assert p2.x == 15
        assert p2.y == 25
        
        # Point - Point -> Vector
        v_res = p2 - p1
        assert isinstance(v_res, Vector)
        assert v_res.dx == 5
        assert v_res.dy == 5
        
        # Invalid operations
        with pytest.raises(TypeError):
            p1 + p2  # Point + Point is invalid
            
        with pytest.raises(TypeError):
            p1 - v   # Point - Vector is invalid (not implemented)

    def test_immutability(self):
        v = Vector(1, 1)
        with pytest.raises(FrozenInstanceError):
            v.dx = 2
            
        p = Point(0, 0)
        with pytest.raises(FrozenInstanceError):
            p.x = 1

    def test_style_defaults(self):
        s = Style()
        assert s.stroke == "black"
        assert s.stroke_width == 1.0
        assert s.fill == "none"
        assert s.opacity == 1.0

    def test_port(self):
        p = Point(0, 0)
        v = Vector(1, 0)
        port = Port(id="1", position=p, direction=v)
        assert port.id == "1"
        assert port.position == p
        assert port.direction == v

    def test_symbol(self):
        # Symbol is abstract-ish but can be instantiated as dataclass
        # Technically Element is base, Symbol inherits
        elems = []
        ports = {}
        sym = Symbol(elements=elems, ports=ports, label="K1")
        assert sym.label == "K1"
        assert sym.elements == elems
        assert sym.ports == ports
