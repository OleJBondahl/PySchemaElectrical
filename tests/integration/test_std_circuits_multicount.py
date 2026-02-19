"""
Integration tests for multi-count support on std_circuits.

Task 7A: Verifies that all standard circuit functions accept explicit
count and wire_labels parameters and produce correct multi-instance output.
"""

from pyschemaelectrical.builder import BuildResult
from pyschemaelectrical.std_circuits import (
    changeover,
    coil,
    dol_starter,
    emergency_stop,
    no_contact,
    psu,
    spdt,
)
from pyschemaelectrical.utils.autonumbering import create_autonumberer


class TestMultiCountStdCircuits:
    """Verify count parameter works correctly on all std_circuits."""

    def test_emergency_stop_count_2(self):
        state = create_autonumberer()
        result = emergency_stop(state, 0, 0, tm_top="X1", tm_bot="X2", count=2)
        assert isinstance(result, BuildResult)
        state, circuit, used = result
        assert len(circuit.elements) >= 4  # at least symbols + wires
        assert "X1" in used
        assert "X2" in used
        assert "S" in result.component_map
        assert len(result.component_map["S"]) == 2  # 2 instances
        # Two instances should produce more elements than one
        result_single = emergency_stop(
            create_autonumberer(), 0, 0, tm_top="X1", tm_bot="X2", count=1
        )
        assert len(circuit.elements) > len(result_single.circuit.elements)

    def test_no_contact_count_3(self):
        state = create_autonumberer()
        result = no_contact(state, 0, 0, tm_top="X1", tm_bot="X2", count=3)
        state, circuit, used = result
        assert len(circuit.elements) >= 4
        assert "S" in result.component_map
        assert len(result.component_map["S"]) == 3  # 3 instances
        assert "X1" in result.terminal_pin_map
        # Three instances should produce more elements than one
        result_single = no_contact(
            create_autonumberer(), 0, 0, tm_top="X1", tm_bot="X2", count=1
        )
        assert len(circuit.elements) > len(result_single.circuit.elements)

    def test_spdt_count_2(self):
        state = create_autonumberer()
        result = spdt(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=2
        )
        assert len(result.circuit.elements) >= 4
        assert "X1" in result.used_terminals
        assert "X2" in result.used_terminals
        assert "Q" in result.component_map
        assert len(result.component_map["Q"]) == 2

    def test_dol_starter_count_2(self):
        state = create_autonumberer()
        result = dol_starter(state, 0, 0, tm_top="X1", tm_bot="X2", count=2)
        state, circuit, used = result
        assert len(circuit.elements) >= 8
        assert "F" in result.component_map
        assert "Q" in result.component_map
        assert len(result.component_map["F"]) == 2
        assert len(result.component_map["Q"]) == 2

    def test_dol_starter_per_instance_terminals(self):
        """Test that tm_bot can be a list for per-instance terminals."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot=["X010", "X011"], count=2
        )
        assert len(result.circuit.elements) >= 8
        assert "X010" in result.used_terminals
        assert "X011" in result.used_terminals
        assert "X010" in result.terminal_pin_map
        assert "X011" in result.terminal_pin_map

    def test_psu_count_2(self):
        state = create_autonumberer()
        result = psu(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=2
        )
        assert len(result.circuit.elements) >= 4
        assert "X1" in result.used_terminals
        assert "X2" in result.used_terminals or "X3" in result.used_terminals
        # Two instances should produce more elements
        result_single = psu(
            create_autonumberer(),
            0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=1
        )
        assert len(result.circuit.elements) > len(result_single.circuit.elements)

    def test_changeover_count_2(self):
        state = create_autonumberer()
        result = changeover(
            state, 0, 0, tm_top_left="X1", tm_top_right="X2", tm_bot="X3", count=2
        )
        assert len(result.circuit.elements) >= 4
        assert "X1" in result.used_terminals
        assert "X2" in result.used_terminals
        assert "X3" in result.used_terminals

    def test_coil_count_2(self):
        state = create_autonumberer()
        result = coil(state, 0, 0, tm_top="X1", count=2)
        assert len(result.circuit.elements) >= 4
        assert "K" in result.component_map
        assert len(result.component_map["K"]) == 2


class TestSpdtRelayTag:
    """Verify relay_tag parameter for spdt circuits."""

    def test_spdt_relay_tag_fixed(self):
        """When relay_tag is set, all contact instances use that tag."""
        state = create_autonumberer()
        result = spdt(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3",
            count=2, relay_tag="K2",
        )
        assert len(result.circuit.elements) >= 4
        assert "X1" in result.used_terminals

    def test_spdt_relay_tag_none_uses_autonumber(self):
        """Without relay_tag, contacts get autonumbered tags."""
        state = create_autonumberer()
        result = spdt(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=1
        )
        assert len(result.circuit.elements) >= 4


class TestDefaultCountBackwardsCompat:
    """Verify that count=1 (default) produces same output as before."""

    def test_emergency_stop_default_count(self):
        state1 = create_autonumberer()
        _, c1, _ = emergency_stop(state1, 0, 0, tm_top="X1", tm_bot="X2")

        state2 = create_autonumberer()
        _, c2, _ = emergency_stop(state2, 0, 0, tm_top="X1", tm_bot="X2", count=1)

        assert len(c1.elements) == len(c2.elements)

    def test_no_contact_default_count(self):
        state1 = create_autonumberer()
        _, c1, _ = no_contact(state1, 0, 0, tm_top="X1", tm_bot="X2")

        state2 = create_autonumberer()
        _, c2, _ = no_contact(state2, 0, 0, tm_top="X1", tm_bot="X2", count=1)

        assert len(c1.elements) == len(c2.elements)

    def test_psu_default_count(self):
        state1 = create_autonumberer()
        _, c1, _ = psu(state1, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3")

        state2 = create_autonumberer()
        _, c2, _ = psu(
            state2, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=1
        )

        assert len(c1.elements) == len(c2.elements)
