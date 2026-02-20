from dataclasses import FrozenInstanceError

import pytest

from pyschemaelectrical.model.core import Point, Port, Style, Symbol, Vector


class TestModelCore:
    def test_vector_creation_and_ops(self):
        v1 = Vector(1.0, 2.0)
        assert v1.dx == 1.0
        assert v1.dy == 2.0

        v2 = Vector(3, 4)
        v3 = v1 + v2
        assert v3.dx == 4
        assert v3.dy == 6

        v4 = v1 * 2
        assert v4.dx == 2
        assert v4.dy == 4

    def test_point_creation_and_ops(self):
        p1 = Point(10.0, 20.0)
        assert p1.x == 10.0
        assert p1.y == 20.0

        v = Vector(5, 5)
        p2 = p1 + v
        assert isinstance(p2, Point)
        assert p2.x == 15
        assert p2.y == 25

        v_res = p2 - p1
        assert isinstance(v_res, Vector)
        assert v_res.dx == 5
        assert v_res.dy == 5

        with pytest.raises(TypeError):
            p1 + p2

        with pytest.raises(TypeError):
            p1 - v

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

    def test_port_and_symbol(self):
        p = Point(0, 0)
        v = Vector(1, 0)
        port = Port(id="1", position=p, direction=v)
        assert port.id == "1"

        sym = Symbol(elements=[], ports={}, label="K1")
        assert sym.label == "K1"


class TestStandardPins:
    """Tests for StandardPins pin set definitions."""

    def test_coil_pins(self):
        from pyschemaelectrical.model.constants import StandardPins

        assert StandardPins.COIL.pins == ("A1", "A2")

    def test_no_contact_pins(self):
        from pyschemaelectrical.model.constants import StandardPins

        assert StandardPins.NO_CONTACT.pins == ("13", "14")

    def test_nc_contact_pins(self):
        from pyschemaelectrical.model.constants import StandardPins

        assert StandardPins.NC_CONTACT.pins == ("11", "12")

    def test_cb_3p_pins(self):
        from pyschemaelectrical.model.constants import StandardPins

        assert StandardPins.CB_3P.pins == ("1", "2", "3", "4", "5", "6")

    def test_cb_2p_pins(self):
        from pyschemaelectrical.model.constants import StandardPins

        assert StandardPins.CB_2P.pins == ("1", "2", "3", "4")

    def test_contactor_3p_same_as_three_pole(self):
        from pyschemaelectrical.model.constants import StandardPins

        assert StandardPins.CONTACTOR_3P.pins == StandardPins.THREE_POLE.pins

    def test_ct_pins(self):
        from pyschemaelectrical.model.constants import StandardPins

        assert StandardPins.CT.pins == ("53", "54", "41", "43")

    def test_all_pin_sets_have_descriptions(self):
        from pyschemaelectrical.model.constants import PinSet, StandardPins

        for name in dir(StandardPins):
            val = getattr(StandardPins, name)
            if isinstance(val, PinSet):
                assert val.description, f"{name} has empty description"
