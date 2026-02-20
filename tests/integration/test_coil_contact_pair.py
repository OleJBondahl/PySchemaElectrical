"""
Integration tests for coil_contact_pair() std circuit.

Task 12: Verifies that coil_contact_pair() produces correct paired coil/contact
circuits with proper tag sharing, start_indices support, and terminal_pin_map.
"""

from pyschemaelectrical.builder import BuildResult
from pyschemaelectrical.std_circuits import coil_contact_pair
from pyschemaelectrical.utils.autonumbering import create_autonumberer


class TestCoilContactPair:
    def test_basic_count_1(self):
        """Single coil-contact pair produces correct circuit."""
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC_DO",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=1,
        )
        assert isinstance(result, BuildResult)
        assert result.state is not None
        assert len(result.circuit.elements) > 0
        assert "X_GND" in result.used_terminals
        assert "X_OUT" in result.used_terminals

    def test_count_4_produces_four_pairs(self):
        """count=4 produces 4 coil+contact pairs."""
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=4,
        )
        assert isinstance(result, BuildResult)
        # K1-K4 tags should appear
        tags = result.component_tags("K")
        assert len(tags) == 4

    def test_start_indices(self):
        """start_indices={"K": 2} starts K tags from K3.

        set_tag_counter sets the counter to 2, so next_tag returns K3.
        """
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=2,
            start_indices={"K": 2},
        )
        tags = result.component_tags("K")
        assert "K3" in tags
        assert "K4" in tags

    def test_terminal_pin_map_populated(self):
        """terminal_pin_map from contact side is available on result."""
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=2,
        )
        # terminal_pin_map should have X_OUT pins
        assert "X_OUT" in result.terminal_pin_map
        # Two instances means two pins allocated for X_OUT
        assert len(result.terminal_pin_map["X_OUT"]) == 2

    def test_returns_build_result(self):
        """Return value is a BuildResult supporting tuple unpacking."""
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
        )
        assert isinstance(result, BuildResult)
        # Supports tuple unpacking (state, circuit, used_terminals)
        unpacked_state, circuit, used = result
        assert unpacked_state is not None
        assert len(circuit.elements) > 0

    def test_coil_bot_and_contact_bot_in_used_terminals(self):
        """Both coil bottom and contact bottom terminals appear in used_terminals."""
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=3,
        )
        assert "X_GND" in result.used_terminals
        assert "X_OUT" in result.used_terminals

    def test_count_produces_more_elements_than_single(self):
        """count=3 produces more circuit elements than count=1."""
        state1 = create_autonumberer()
        result_single = coil_contact_pair(
            state=state1,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=1,
        )

        state2 = create_autonumberer()
        result_multi = coil_contact_pair(
            state=state2,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=3,
        )

        assert len(result_multi.circuit.elements) > len(result_single.circuit.elements)

    def test_state_advances_after_build(self):
        """State returned from coil_contact_pair has advanced K counter."""
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=2,
        )
        # Build another circuit after — should start from K3
        from pyschemaelectrical.utils.autonumbering import next_tag

        new_state, tag = next_tag(result.state, "K")
        assert tag == "K3"

    def test_custom_tag_prefix(self):
        """Custom tag_prefix is used instead of default K."""
        state = create_autonumberer()
        result = coil_contact_pair(
            state=state,
            tm_coil_top="X_PLC",
            tm_coil_bot="X_GND",
            tm_contact_top="X_24V",
            tm_contact_bot="X_OUT",
            count=2,
            tag_prefix="KA",
        )
        tags = result.component_tags("KA")
        assert len(tags) == 2
        assert tags[0] == "KA1"
        assert tags[1] == "KA2"
