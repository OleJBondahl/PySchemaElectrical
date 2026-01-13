import pytest
from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.model.core import Symbol, Port, Point, Vector

# Mock symbol function
def mock_symbol(tag, **kwargs):
    s = Symbol(tag, ports={
        "1": Port("1", Point(0, -1), Vector(0, -1)),
        "2": Port("2", Point(0, 1), Vector(0, 1))
    },label=tag)
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
        assert spec.kwargs["terminal_id"] == "X99"

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
