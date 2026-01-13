import pytest
from pyschemaelectrical.model.core import Point, Vector, Symbol, Port, Element
from pyschemaelectrical.model.primitives import Text, Circle, Polygon, Line
from pyschemaelectrical.model.parts import standard_text, terminal_circle, box, create_pin_labels, three_pole_factory

class TestPartsUnit:
    def test_standard_text(self):
        t = standard_text("K1", Point(0,0))
        assert t.content == "K1"
        assert t.position.x < 0  # It applies an offset to the left
        assert t.anchor == "end"

    def test_terminal_circle(self):
        c = terminal_circle(Point(10,10), filled=True)
        assert c.center == Point(10,10)
        assert c.style.fill == "black"
        
        c2 = terminal_circle(Point(10,10), filled=False)
        assert c2.style.fill == "none"

    def test_box(self):
        b = box(Point(0,0), 10, 20)
        assert isinstance(b, Polygon)
        assert len(b.points) == 4
        # check dimensions roughly
        xs = [p.x for p in b.points]
        ys = [p.y for p in b.points]
        assert max(xs) - min(xs) == 10
        assert max(ys) - min(ys) == 20

    def test_create_pin_labels(self):
        # Setup ports
        ports = {
            "1": Port("1", Point(0,0), Vector(0,-1)), # UP
            "2": Port("2", Point(0,10), Vector(0,1))  # DOWN
        }
        labels = create_pin_labels(ports, ("13", "14"))
        assert len(labels) == 2
        assert labels[0].content == "13"
        assert labels[0].position.x < 0
        assert labels[1].position.x < 0

    def test_three_pole_factory(self):
        # Mock single pole function
        def mock_pole(label, pins):
            # Returns a symbol with 2 ports and a line
            return Symbol(
                elements=[Line(Point(0,0), Point(0,10))],
                ports={
                    "1": Port("1", Point(0,0), Vector(0,-1)), 
                    "2": Port("2", Point(0,10), Vector(0,1))
                },
                label=label
            )

        sym = three_pole_factory(
            single_pole_func=mock_pole,
            label="-Q1",
            pins=("1", "2", "3", "4", "5", "6"),
            pole_spacing=10.0
        )
        
        assert sym.label == "-Q1"
        assert len(sym.elements) == 3
        
        assert "1" in sym.ports
        assert "3" in sym.ports # Mapped from pole 2 pin 1
        assert "5" in sym.ports # Mapped from pole 3 pin 1
        
        assert sym.ports["1"].position.x == 0
        assert sym.ports["3"].position.x == 10
        assert sym.ports["5"].position.x == 20

    def test_three_pole_factory_validation(self):
        def mock_pole(**kwargs): return Symbol([], {}, "")
        with pytest.raises(ValueError):
            three_pole_factory(mock_pole, pins=("1", "2")) # Invalid len
