from pyschemaelectrical.utils.autonumbering import (
    auto_coil_pins,
    auto_contact_pins,
    auto_terminal_pins,
    auto_thermal_pins,
    create_autonumberer,
    format_tag,
    generate_pin_range,
    get_tag_number,
    increment_tag,
    next_tag,
    next_terminal_pins,
)


class TestAutonumberingAdvanced:
    """Additional comprehensive tests for autonumbering module."""

    def test_state_immutability(self):
        """Test that state modifications don't affect original state."""
        state1 = create_autonumberer()
        state2 = increment_tag(state1, "F")

        # Original state should be unchanged
        assert get_tag_number(state1, "F") == 0
        # New state should have incremented value
        assert get_tag_number(state2, "F") == 1

    def test_multiple_prefixes(self):
        """Test handling multiple component prefixes."""
        state = create_autonumberer()

        # Increment different prefixes
        state, f1 = next_tag(state, "F")
        state, q1 = next_tag(state, "Q")
        state, x1 = next_tag(state, "X")
        state, f2 = next_tag(state, "F")
        state, q2 = next_tag(state, "Q")

        assert f1 == "F1"
        assert q1 == "Q1"
        assert x1 == "X1"
        assert f2 == "F2"
        assert q2 == "Q2"

        # Verify state
        assert get_tag_number(state, "F") == 2
        assert get_tag_number(state, "Q") == 2
        assert get_tag_number(state, "X") == 1

    def test_terminal_pins_multiple_tags(self):
        """Test terminal pin generation for multiple different tags."""
        state = create_autonumberer()

        # Generate pins for X1
        state, pins1 = next_terminal_pins(state, "X1", poles=3)
        assert pins1 == ("1", "2", "3")

        # Generate more pins for X1
        state, pins2 = next_terminal_pins(state, "X1", poles=3)
        assert pins2 == ("4", "5", "6")

        # Generate pins for X2 (should start fresh)
        state, pins3 = next_terminal_pins(state, "X2", poles=3)
        assert pins3 == ("1", "2", "3")

        # Generate pins for X10 (single pole)
        state, pins4 = next_terminal_pins(state, "X10", poles=1)
        assert pins4 == ("1",)

        # Another single pole for X10
        state, pins5 = next_terminal_pins(state, "X10", poles=1)
        assert pins5 == ("2",)

        # Verify independent counters
        assert state["terminal_counters"]["X1"] == 6
        assert state["terminal_counters"]["X2"] == 3
        assert state["terminal_counters"]["X10"] == 2

    def test_generate_pin_range_variations(self):
        """Test pin range generation with various parameters."""
        # Standard sequential
        pins = generate_pin_range(1, 4)
        assert pins == ("1", "2", "3", "4")

        # Starting from different number
        pins = generate_pin_range(10, 3)
        assert pins == ("10", "11", "12")

        # Skip odd
        pins = generate_pin_range(1, 8, skip_odd=True)
        assert pins == ("", "2", "", "4", "", "6", "", "8")

        # Skip odd starting from even
        pins = generate_pin_range(2, 4, skip_odd=True)
        assert pins == ("2", "", "4", "")

    def test_auto_functions_variations(self):
        """Test all auto_* helper functions with various parameters."""
        # Terminal pins with different poles
        assert auto_terminal_pins(1, 1) == ("1", "2")
        assert auto_terminal_pins(1, 2) == ("1", "2", "3", "4")
        assert auto_terminal_pins(5, 2) == ("5", "6", "7", "8")

        # Contact pins
        assert auto_contact_pins(1, 1) == ("1", "2")
        assert auto_contact_pins(10, 3) == ("10", "11", "12", "13", "14", "15")

        # Thermal pins (4 poles)
        pins = auto_thermal_pins(2, 4)
        assert len(pins) == 8
        assert pins[1] == "2"
        assert pins[3] == "4"
        assert pins[5] == "6"
        assert pins[7] == "8"
        assert pins[0] == ""
        assert pins[2] == ""

        # Coil pins (always the same)
        assert auto_coil_pins() == ("A1", "A2")

    def test_format_tag_edge_cases(self):
        """Test tag formatting with edge cases."""
        assert format_tag("F", 0) == "F0"
        assert format_tag("Q", 99) == "Q99"
        assert format_tag("X", 1000) == "X1000"
        assert format_tag("", 5) == "5"

    def test_state_structure(self):
        """Test the structure of autonumbering state."""
        state = create_autonumberer()

        # Verify initial state structure
        assert "tags" in state
        assert "terminal_counters" in state

        assert isinstance(state["tags"], dict)
        assert isinstance(state["terminal_counters"], dict)

    def test_zero_poles(self):
        """Test terminal pins with zero poles (edge case)."""
        state = create_autonumberer()
        state, pins = next_terminal_pins(state, "X1", poles=0)

        assert pins == ()
        assert state["terminal_counters"]["X1"] == 0

    def test_large_number_of_poles(self):
        """Test terminal pins with large number of poles."""
        state = create_autonumberer()
        state, pins = next_terminal_pins(state, "X1", poles=10)

        assert len(pins) == 10
        assert pins == ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10")
        assert state["terminal_counters"]["X1"] == 10

    def test_sequential_workflow(self):
        """Test a realistic sequential workflow like in pump_example.py."""
        state = create_autonumberer()

        # Generate component tags
        state, f_tag = next_tag(state, "F")
        state, q_tag = next_tag(state, "Q")
        state, ct_tag = next_tag(state, "CT")

        assert f_tag == "F1"
        assert q_tag == "Q1"
        assert ct_tag == "CT1"

        # Generate terminal pins
        state, main_pins = next_terminal_pins(state, "MAIN_400V", 3)
        state, ext_pins = next_terminal_pins(state, "EXT_AC", 3)
        state, fused_24v_pins = next_terminal_pins(state, "FUSED_24V", 1)
        state, gnd_pins = next_terminal_pins(state, "GND", 1)

        assert main_pins == ("1", "2", "3")
        assert ext_pins == ("1", "2", "3")
        assert fused_24v_pins == ("1",)
        assert gnd_pins == ("1",)

        # Second circuit - tags increment, pins continue per terminal
        state, f_tag2 = next_tag(state, "F")
        state, q_tag2 = next_tag(state, "Q")

        assert f_tag2 == "F2"
        assert q_tag2 == "Q2"

        state, main_pins2 = next_terminal_pins(state, "MAIN_400V", 3)
        state, ext_pins2 = next_terminal_pins(state, "EXT_AC", 3)

        assert main_pins2 == ("4", "5", "6")  # Continues from previous
        assert ext_pins2 == ("4", "5", "6")
