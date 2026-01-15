
import pytest
from pyschemaelectrical.model.core import Point, Style
from pyschemaelectrical.model.primitives import Line
from pyschemaelectrical.system.system import Circuit
from pyschemaelectrical.layout.wire_labels import (
    calculate_wire_label_position,
    format_wire_specification,
    create_wire_label_text,
    create_labeled_wire,
    find_vertical_wires,
    add_wire_labels_to_circuit
)

class TestWireLabels:
    def test_calculate_position(self):
        start = Point(0, 0)
        end = Point(0, 10)
        pos = calculate_wire_label_position(start, end, offset_x=-2.5)
        
        # Midpoint of 0,0 and 0,10 is 0,5
        # Offset x is -2.5 -> -2.5, 5
        assert pos.x == -2.5
        assert pos.y == 5.0
        
    def test_format_wire_spec(self):
        assert format_wire_specification("RD", "1.5mm") == "RD 1.5mm"
        assert format_wire_specification("RD", "") == "RD"
        assert format_wire_specification("", "1.5mm") == "1.5mm"
        assert format_wire_specification("", "") == ""
        
    def test_create_wire_label_text(self):
        pos = Point(10, 10)
        txt = create_wire_label_text("RD", pos)
        assert txt.content == "RD"
        assert txt.position == pos
        assert txt.rotation == 90.0
        assert txt.anchor == "middle"
        
    def test_create_labeled_wire(self):
        start = Point(0, 0)
        end = Point(0, 10)
        elements = create_labeled_wire(start, end, wire_color="RD", wire_size="1mm")
        
        assert len(elements) == 2
        line = elements[0]
        text = elements[1]
        
        assert isinstance(line, Line)
        assert line.start == start
        assert line.end == end
        
        assert text.content == "RD 1mm"
        assert text.position.x == -2.5
        
    def test_find_vertical_wires(self):
        l1 = Line(Point(0,0), Point(0,10)) # Vertical
        l2 = Line(Point(0,0), Point(10,0)) # Horizontal
        l3 = Line(Point(0,0), Point(0.05, 10)) # Vertical within tolerance 0.1
        l4 = Line(Point(0,0), Point(1, 10)) # Not vertical
        
        wires = find_vertical_wires([l1, l2, l3, l4], tolerance=0.1)
        assert len(wires) == 2
        assert l1 in wires
        assert l3 in wires
        
    def test_add_wire_labels_to_circuit(self):
        c = Circuit()
        l1 = Line(Point(0,0), Point(0,10))
        l2 = Line(Point(10,0), Point(10,10))
        c.elements.extend([l1, l2])
        
        labels = ["L1", "L2"]
        add_wire_labels_to_circuit(c, labels)
        
        # Should have added 2 text elements
        assert len(c.elements) == 4
        assert c.elements[2].content == "L1"
        assert c.elements[3].content == "L2"
        
    def test_add_wire_labels_insufficient(self):
        c = Circuit()
        l1 = Line(Point(0,0), Point(0,10))
        l2 = Line(Point(10,0), Point(10,10))
        c.elements.extend([l1, l2])
        
        labels = ["L1"] # Only 1 label for 2 wires
        
        add_wire_labels_to_circuit(c, labels)
        
        # It should cycle or stop? Source says: cycle
        # "wire_labels = list(islice(cycle(wire_labels), len(vertical_wires)))"
        assert len(c.elements) == 4
        assert c.elements[2].content == "L1"
        assert c.elements[3].content == "L1" # Repetition
