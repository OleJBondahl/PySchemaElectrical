from pyschemaelectrical.layout.wire_labels import (
    add_wire_labels_to_circuit,
    calculate_wire_label_position,
    create_labeled_wire,
    create_wire_label_text,
    find_vertical_wires,
    format_wire_specification,
)
from pyschemaelectrical.model.core import Point
from pyschemaelectrical.model.primitives import Line
from pyschemaelectrical.system.system import Circuit


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
        l1 = Line(Point(0, 0), Point(0, 10))  # Vertical
        l2 = Line(Point(0, 0), Point(10, 0))  # Horizontal
        l3 = Line(Point(0, 0), Point(0.05, 10))  # Vertical within tolerance 0.1
        l4 = Line(Point(0, 0), Point(1, 10))  # Not vertical

        wires = find_vertical_wires([l1, l2, l3, l4], tolerance=0.1)
        assert len(wires) == 2
        assert l1 in wires
        assert l3 in wires

    def test_add_wire_labels_to_circuit(self):
        c = Circuit()
        l1 = Line(Point(0, 0), Point(0, 10))
        l2 = Line(Point(10, 0), Point(10, 10))
        c.elements.extend([l1, l2])

        labels = ["L1", "L2"]
        c_new = add_wire_labels_to_circuit(c, labels)

        # Original should be unchanged
        assert len(c.elements) == 2

        # New circuit has 2 text elements added
        assert len(c_new.elements) == 4
        assert c_new.elements[2].content == "L1"
        assert c_new.elements[3].content == "L2"

    def test_add_wire_labels_insufficient(self):
        c = Circuit()
        l1 = Line(Point(0, 0), Point(0, 10))
        l2 = Line(Point(10, 0), Point(10, 10))
        c.elements.extend([l1, l2])

        labels = ["L1"]  # Only 1 label for 2 wires

        c_new = add_wire_labels_to_circuit(c, labels)

        # It should cycle
        assert len(c_new.elements) == 4
        assert c_new.elements[2].content == "L1"
        assert c_new.elements[3].content == "L1"  # Repetition

    def test_add_wire_labels_returns_new_circuit(self):
        """add_wire_labels_to_circuit should return new Circuit, not mutate."""
        from pyschemaelectrical.model.parts import standard_style
        from pyschemaelectrical.system.system import Circuit

        # Create circuit with vertical wire
        wire = Line(Point(0, 0), Point(0, 20), standard_style())
        original = Circuit(symbols=[], elements=[wire])
        original_len = len(original.elements)

        result = add_wire_labels_to_circuit(original, ["RD 2.5mm²"])

        # Original unchanged
        assert len(original.elements) == original_len

        # Result has label added
        assert len(result.elements) == original_len + 1
        assert result is not original
