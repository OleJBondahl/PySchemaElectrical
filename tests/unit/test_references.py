from pyschemaelectrical.model.core import Symbol, Point, Vector
from pyschemaelectrical.symbols.references import ref_symbol
from pyschemaelectrical.model.constants import REF_ARROW_LENGTH


class TestReferenceSymbols:
    def test_ref_symbol_creation(self):
        s = ref_symbol(tag="ref1")
        assert isinstance(s, Symbol)

    def test_ref_symbol_up(self):
        """Test reference symbol pointing UP."""
        s = ref_symbol(tag="ref1", direction="up")

        # In new implementation:
        # Origin (0,0) is TIP.
        # Port is at TAIL.
        # Direction UP means Arrow points UP from Tail to Tip.
        # Tail = (0, REF_ARROW_LENGTH)
        # Tip = (0, 0)

        # Check ports
        assert "2" in s.ports
        port = s.ports["2"]

        # Verify port position (Tail)
        # Port x,y are relative to symbol origin (which is Tip (0,0))
        assert abs(port.position.x - 0.0) < 0.001
        assert abs(port.position.y - REF_ARROW_LENGTH) < 0.001  # (0, 10.0)

        # Verify port vector
        assert port.direction.dy == 1  # Connects from below (Down vector)

    def test_ref_symbol_down(self):
        """Test reference symbol pointing DOWN."""
        s = ref_symbol(tag="ref2", direction="down")

        # In new implementation:
        # Origin (0,0) is TIP.
        # Port is at TAIL.
        # Direction DOWN means Arrow points DOWN from Tail to Tip.
        # Tail = (0, -REF_ARROW_LENGTH)
        # Tip = (0, 0)

        # Check ports
        assert "1" in s.ports
        port = s.ports["1"]

        # Verify port position (Tail)
        assert abs(port.position.x - 0.0) < 0.001
        assert abs(port.position.y - (-REF_ARROW_LENGTH)) < 0.001  # (0, -10.0)

        # Verify port vector
        assert port.direction.dy == -1  # Connects from above (Up vector)
