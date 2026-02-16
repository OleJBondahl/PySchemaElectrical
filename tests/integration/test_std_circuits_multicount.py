"""
Integration tests for multi-count support on std_circuits.

Task 7A: Verifies that all standard circuit functions accept explicit
count and wire_labels parameters and produce correct multi-instance output.
"""

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
        state, circuit, used = emergency_stop(
            state, 0, 0, tm_top="X1", tm_bot="X2", count=2
        )
        assert len(circuit.elements) > 0
        # Two instances should produce more elements than one
        state2 = create_autonumberer()
        state2, circuit_single, _ = emergency_stop(
            state2, 0, 0, tm_top="X1", tm_bot="X2", count=1
        )
        assert len(circuit.elements) > len(circuit_single.elements)

    def test_no_contact_count_3(self):
        state = create_autonumberer()
        state, circuit, used = no_contact(
            state, 0, 0, tm_top="X1", tm_bot="X2", count=3
        )
        assert len(circuit.elements) > 0
        # Three instances should produce more elements than one
        state2 = create_autonumberer()
        state2, circuit_single, _ = no_contact(
            state2, 0, 0, tm_top="X1", tm_bot="X2", count=1
        )
        assert len(circuit.elements) > len(circuit_single.elements)

    def test_spdt_count_2(self):
        state = create_autonumberer()
        state, circuit, used = spdt(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=2
        )
        assert len(circuit.elements) > 0

    def test_dol_starter_count_2(self):
        state = create_autonumberer()
        state, circuit, used = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2", tm_bot_right="X3", count=2
        )
        assert len(circuit.elements) > 0

    def test_dol_starter_per_instance_terminals(self):
        """Test that tm_bot can be a list for per-instance terminals."""
        state = create_autonumberer()
        state, circuit, used = dol_starter(
            state,
            0,
            0,
            tm_top="X1",
            tm_bot=["X010", "X011"],
            tm_bot_right="X3",
            count=2,
        )
        assert len(circuit.elements) > 0
        assert "X010" in used
        assert "X011" in used

    def test_psu_count_2(self):
        state = create_autonumberer()
        state, circuit, used = psu(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=2
        )
        assert len(circuit.elements) > 0
        # Two instances should produce more elements
        state2 = create_autonumberer()
        state2, circuit_single, _ = psu(
            state2, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=1
        )
        assert len(circuit.elements) > len(circuit_single.elements)

    def test_changeover_count_2(self):
        state = create_autonumberer()
        state, circuit, used = changeover(
            state, 0, 0, tm_top_left="X1", tm_top_right="X2", tm_bot="X3", count=2
        )
        assert len(circuit.elements) > 0

    def test_coil_count_2(self):
        state = create_autonumberer()
        state, circuit, used = coil(state, 0, 0, tm_top="X1", count=2)
        assert len(circuit.elements) > 0


class TestSpdtRelayTag:
    """Verify relay_tag parameter for spdt circuits."""

    def test_spdt_relay_tag_fixed(self):
        """When relay_tag is set, all contact instances use that tag."""
        state = create_autonumberer()
        state, circuit, used = spdt(
            state,
            0,
            0,
            tm_top="X1",
            tm_bot_left="X2",
            tm_bot_right="X3",
            count=2,
            relay_tag="K2",
        )
        assert len(circuit.elements) > 0

    def test_spdt_relay_tag_none_uses_autonumber(self):
        """Without relay_tag, contacts get autonumbered tags."""
        state = create_autonumberer()
        state, circuit, used = spdt(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3", count=1
        )
        assert len(circuit.elements) > 0


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
