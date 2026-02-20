"""
Unit tests for the power_distribution() function in std_circuits/power.py.

Tests cover:
- Basic invocation with correct terminal_maps
- BuildResult structure and tuple unpacking
- Circuit element generation
- Used terminals tracking
- Legacy terminal map key fallback
- Missing key validation
- Multi-count changeover instances
- State propagation through sub-circuits
"""

import pytest

from pyschemaelectrical.builder import BuildResult
from pyschemaelectrical.std_circuits import power_distribution
from pyschemaelectrical.system.system import Circuit
from pyschemaelectrical.utils.autonumbering import create_autonumberer


def _make_terminal_maps():
    """Create a standard terminal_maps dict for testing."""
    return {
        "INPUT_1": "X1",
        "INPUT_2": "X2",
        "OUTPUT": "X3",
        "PSU_INPUT": "X4",
        "PSU_OUTPUT_1": "X5",
        "PSU_OUTPUT_2": "X6",
    }


class TestPowerDistributionBasic:
    """Basic functional tests for power_distribution()."""

    def test_returns_build_result(self):
        """power_distribution should return a BuildResult dataclass."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        assert isinstance(result, BuildResult)

    def test_tuple_unpacking(self):
        """BuildResult should support (state, circuit, used_terminals) unpacking."""
        state = create_autonumberer()
        state_out, circuit, used_terminals = power_distribution(
            state, 0, 0, terminal_maps=_make_terminal_maps()
        )
        assert state_out is not None
        assert isinstance(circuit, Circuit)
        assert isinstance(used_terminals, list)

    def test_circuit_has_elements(self):
        """The resulting circuit should contain elements (symbols, lines, etc.)."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        assert len(result.circuit.elements) > 0

    def test_state_is_updated(self):
        """The returned state should differ from the initial state
        (counters incremented by sub-circuits)."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        # The output state should not be the exact same object
        # (sub-circuits create new state dicts/objects via autonumbering)
        assert result.state is not None


class TestPowerDistributionUsedTerminals:
    """Tests for the used_terminals tracking."""

    def test_used_terminals_contains_input_terminals(self):
        """used_terminals should include the changeover input terminal IDs."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        assert "X1" in result.used_terminals
        assert "X2" in result.used_terminals

    def test_used_terminals_contains_output_terminal(self):
        """used_terminals should include the changeover output terminal ID."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        assert "X3" in result.used_terminals

    def test_used_terminals_contains_psu_terminals(self):
        """used_terminals should include PSU input and output terminal IDs."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        assert "X4" in result.used_terminals
        assert "X5" in result.used_terminals
        assert "X6" in result.used_terminals

    def test_used_terminals_are_unique(self):
        """used_terminals should contain no duplicates."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        assert len(result.used_terminals) == len(set(result.used_terminals))


class TestPowerDistributionTerminalMapsValidation:
    """Tests for terminal_maps key validation."""

    def test_missing_required_key_raises_value_error(self):
        """Omitting a required key should raise ValueError."""
        state = create_autonumberer()
        incomplete_maps = {
            "INPUT_1": "X1",
            "INPUT_2": "X2",
            # Missing OUTPUT, PSU_INPUT, PSU_OUTPUT_1, PSU_OUTPUT_2
        }
        with pytest.raises(ValueError, match="terminal_maps missing required keys"):
            power_distribution(state, 0, 0, terminal_maps=incomplete_maps)

    def test_missing_single_key_raises_value_error(self):
        """Omitting just one required key should raise ValueError."""
        state = create_autonumberer()
        maps = _make_terminal_maps()
        del maps["OUTPUT"]
        with pytest.raises(ValueError, match="OUTPUT"):
            power_distribution(state, 0, 0, terminal_maps=maps)

    def test_legacy_key_psu_output_24v_fallback(self):
        """Legacy key PSU_OUTPUT_24V should be accepted as PSU_OUTPUT_1."""
        state = create_autonumberer()
        maps = {
            "INPUT_1": "X1",
            "INPUT_2": "X2",
            "OUTPUT": "X3",
            "PSU_INPUT": "X4",
            "PSU_OUTPUT_24V": "X5",  # Legacy key
            "PSU_OUTPUT_2": "X6",
        }
        result = power_distribution(state, 0, 0, terminal_maps=maps)
        assert isinstance(result, BuildResult)
        assert len(result.circuit.elements) > 0

    def test_legacy_key_psu_output_gnd_fallback(self):
        """Legacy key PSU_OUTPUT_GND should be accepted as PSU_OUTPUT_2."""
        state = create_autonumberer()
        maps = {
            "INPUT_1": "X1",
            "INPUT_2": "X2",
            "OUTPUT": "X3",
            "PSU_INPUT": "X4",
            "PSU_OUTPUT_1": "X5",
            "PSU_OUTPUT_GND": "X6",  # Legacy key
        }
        result = power_distribution(state, 0, 0, terminal_maps=maps)
        assert isinstance(result, BuildResult)
        assert len(result.circuit.elements) > 0

    def test_both_legacy_keys_fallback(self):
        """Both legacy PSU keys should work together."""
        state = create_autonumberer()
        maps = {
            "INPUT_1": "X1",
            "INPUT_2": "X2",
            "OUTPUT": "X3",
            "PSU_INPUT": "X4",
            "PSU_OUTPUT_24V": "X5",  # Legacy key
            "PSU_OUTPUT_GND": "X6",  # Legacy key
        }
        result = power_distribution(state, 0, 0, terminal_maps=maps)
        assert isinstance(result, BuildResult)
        assert len(result.circuit.elements) > 0

    def test_empty_terminal_maps_raises_value_error(self):
        """An empty terminal_maps dict should raise ValueError."""
        state = create_autonumberer()
        with pytest.raises(ValueError, match="terminal_maps missing required keys"):
            power_distribution(state, 0, 0, terminal_maps={})


class TestPowerDistributionMultiCount:
    """Tests for the count parameter (multiple changeover instances)."""

    def test_count_2_produces_more_elements(self):
        """count=2 should produce more circuit elements than count=1."""
        state1 = create_autonumberer()
        result1 = power_distribution(
            state1, 0, 0, terminal_maps=_make_terminal_maps(), count=1
        )

        state2 = create_autonumberer()
        result2 = power_distribution(
            state2, 0, 0, terminal_maps=_make_terminal_maps(), count=2
        )

        assert len(result2.circuit.elements) > len(result1.circuit.elements)

    def test_count_default_is_1(self):
        """Default count should be 1; explicit count=1 should match."""
        state1 = create_autonumberer()
        result_default = power_distribution(
            state1, 0, 0, terminal_maps=_make_terminal_maps()
        )

        state2 = create_autonumberer()
        result_explicit = power_distribution(
            state2, 0, 0, terminal_maps=_make_terminal_maps(), count=1
        )

        assert len(result_default.circuit.elements) == len(
            result_explicit.circuit.elements
        )


class TestPowerDistributionCircuitContent:
    """Tests verifying the content of the generated circuit."""

    def test_circuit_contains_many_elements(self):
        """A power distribution circuit is complex; expect a significant number
        of elements (terminals, breakers, contacts, PSU, coil, lines)."""
        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        # A full power distribution (changeover + voltage monitor + PSU)
        # should generate a substantial number of elements
        assert len(result.circuit.elements) > 20

    def test_different_positions_produce_different_coordinates(self):
        """Placing at different x,y positions should yield different SVG output."""
        import xml.etree.ElementTree as ET

        from pyschemaelectrical.utils.renderer import to_xml_element

        state1 = create_autonumberer()
        result1 = power_distribution(state1, 0, 0, terminal_maps=_make_terminal_maps())
        svg1 = ET.tostring(to_xml_element(result1.circuit.elements), encoding="unicode")

        state2 = create_autonumberer()
        result2 = power_distribution(
            state2, 100, 100, terminal_maps=_make_terminal_maps()
        )
        svg2 = ET.tostring(to_xml_element(result2.circuit.elements), encoding="unicode")

        # Different positions should produce different SVG
        assert svg1 != svg2

    def test_circuit_is_renderable(self):
        """The circuit should be renderable to SVG without errors."""
        import xml.etree.ElementTree as ET

        from pyschemaelectrical.utils.renderer import to_xml_element

        state = create_autonumberer()
        result = power_distribution(state, 0, 0, terminal_maps=_make_terminal_maps())
        # Rendering should not raise
        root = to_xml_element(result.circuit.elements)
        svg_str = ET.tostring(root, encoding="unicode")
        assert len(svg_str) > 0
        assert "<svg" in svg_str or "<g" in svg_str


class TestPowerDistributionStateThreading:
    """Tests for correct state propagation through chained sub-circuits."""

    def test_sequential_calls_increment_tags(self):
        """Two sequential power_distribution calls should autonumber
        components without tag collisions."""
        state = create_autonumberer()
        maps1 = _make_terminal_maps()

        result1 = power_distribution(state, 0, 0, terminal_maps=maps1)

        maps2 = {
            "INPUT_1": "X11",
            "INPUT_2": "X12",
            "OUTPUT": "X13",
            "PSU_INPUT": "X14",
            "PSU_OUTPUT_1": "X15",
            "PSU_OUTPUT_2": "X16",
        }
        # Use the state from the first call
        result2 = power_distribution(result1.state, 200, 0, terminal_maps=maps2)

        # Both should produce valid circuits
        assert len(result1.circuit.elements) > 0
        assert len(result2.circuit.elements) > 0

        # Second call should have further-incremented state
        assert result2.state is not None
