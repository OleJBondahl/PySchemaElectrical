import pytest
from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.model.core import Symbol, Port, Point, Vector


# Mock symbol function
def mock_symbol(tag, **kwargs):
    s = Symbol(
        tag,
        ports={
            "1": Port("1", Point(0, -1), Vector(0, -1)),
            "2": Port("2", Point(0, 1), Vector(0, 1)),
        },
        label=tag,
    )
    return s


class TestBuilderUnit:
    def test_builder_initialization(self):
        state = create_autonumberer()
        builder = CircuitBuilder(state)
        assert builder is not None

    def test_add_terminal(self):
        state = create_autonumberer()
        builder = CircuitBuilder(state)
        builder.add_terminal("X99", poles=1)

        # Verify specs are added
        assert len(builder._spec.components) == 1
        spec = builder._spec.components[0]
        assert spec.kind == "terminal"
        assert spec.kwargs["tm_id"] == "X99"

    def test_add_component(self):
        state = create_autonumberer()
        builder = CircuitBuilder(state)
        builder.add_component(mock_symbol, tag_prefix="K")

        assert len(builder._spec.components) == 1
        spec = builder._spec.components[0]
        assert spec.kind == "symbol"
        assert spec.tag_prefix == "K"

    def test_build_single_simple(self):
        state = create_autonumberer()
        builder = CircuitBuilder(state)
        builder.set_layout(0, 0)
        builder.add_component(mock_symbol, tag_prefix="K")

        # In the refactored builder, we expect a BuildResult object
        result = builder.build(count=1)

        assert result.circuit is not None
        assert len(result.circuit.elements) > 0
        assert result.state is not None

    def test_build_validates_connection_indices(self):
        """Invalid connection indices should raise ComponentNotFoundError."""
        from pyschemaelectrical.exceptions import ComponentNotFoundError

        state = create_autonumberer()

        builder = CircuitBuilder(state)
        builder.set_layout(0, 0)
        builder.add_terminal("X1")  # Index 0
        builder.add_connection(0, 0, 5, 0)  # Index 5 doesn't exist

        with pytest.raises(ComponentNotFoundError):
            builder.build()


class TestResolvePinEdgeCases:
    """Tests for _resolve_pin edge cases."""

    def test_terminal_pin_resolution_1_pole(self):
        """1-pole terminal should resolve to ports '1' (in) and '2' (out)."""
        from pyschemaelectrical.builder import _resolve_pin, ComponentSpec

        component_data = {
            "spec": ComponentSpec(func=None, kind="terminal", poles=1),
            "pins": ["42"],  # Terminal number
        }

        assert _resolve_pin(component_data, pole_idx=0, is_input=True) == "1"
        assert _resolve_pin(component_data, pole_idx=0, is_input=False) == "2"

    def test_terminal_pin_resolution_3_pole(self):
        """3-pole terminal poles should map to correct port IDs."""
        from pyschemaelectrical.builder import _resolve_pin, ComponentSpec

        component_data = {
            "spec": ComponentSpec(func=None, kind="terminal", poles=3),
            "pins": ["1", "2", "3"],
        }

        # Pole 0: ports 1, 2
        assert _resolve_pin(component_data, pole_idx=0, is_input=True) == "1"
        assert _resolve_pin(component_data, pole_idx=0, is_input=False) == "2"
        # Pole 1: ports 3, 4
        assert _resolve_pin(component_data, pole_idx=1, is_input=True) == "3"
        assert _resolve_pin(component_data, pole_idx=1, is_input=False) == "4"
        # Pole 2: ports 5, 6
        assert _resolve_pin(component_data, pole_idx=2, is_input=True) == "5"
        assert _resolve_pin(component_data, pole_idx=2, is_input=False) == "6"

    def test_symbol_with_2x_pins(self):
        """Symbol with poles*2 pins should use interleaved indexing."""
        from pyschemaelectrical.builder import _resolve_pin, ComponentSpec

        component_data = {
            "spec": ComponentSpec(func=lambda: None, kind="symbol", poles=2),
            "pins": ["A1", "A2", "B1", "B2"],  # 4 pins = 2 poles * 2
        }

        # Pole 0
        assert _resolve_pin(component_data, pole_idx=0, is_input=True) == "A1"
        assert _resolve_pin(component_data, pole_idx=0, is_input=False) == "A2"
        # Pole 1
        assert _resolve_pin(component_data, pole_idx=1, is_input=True) == "B1"
        assert _resolve_pin(component_data, pole_idx=1, is_input=False) == "B2"

    def test_symbol_with_custom_named_ports(self):
        """Symbol with non-standard pin count should use direct indexing."""
        from pyschemaelectrical.builder import _resolve_pin, ComponentSpec

        component_data = {
            "spec": ComponentSpec(func=lambda: None, kind="symbol", poles=1),
            "pins": ["L", "N", "PE", "24V", "GND"],  # 5 pins, not poles*2
        }

        # Direct indexing
        assert _resolve_pin(component_data, pole_idx=0, is_input=True) == "L"
        assert _resolve_pin(component_data, pole_idx=1, is_input=True) == "N"
        assert _resolve_pin(component_data, pole_idx=2, is_input=True) == "PE"
