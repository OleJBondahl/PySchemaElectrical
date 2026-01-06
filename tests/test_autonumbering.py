
import pytest
from iec_lib.autonumbering import (
    create_autonumberer,
    get_tag_number,
    increment_tag,
    format_tag,
    next_tag,
    generate_pin_range,
    next_terminal_pins,
    auto_terminal_pins,
    auto_contact_pins,
    auto_thermal_pins,
    auto_coil_pins
)

class TestAutonumbering:
    def test_basic_tag_workflow(self):
        state = create_autonumberer()
        
        # Initial state should be empty/zero
        assert get_tag_number(state, "K") == 0
        
        # Increment
        state = increment_tag(state, "K")
        assert get_tag_number(state, "K") == 1
        
        # Increment again
        state = increment_tag(state, "K")
        assert get_tag_number(state, "K") == 2
        
        # Different prefix
        assert get_tag_number(state, "Q") == 0
        state = increment_tag(state, "Q")
        assert get_tag_number(state, "Q") == 1
        # Check K is still 2
        assert get_tag_number(state, "K") == 2

    def test_next_tag_helper(self):
        state = create_autonumberer()
        state, tag = next_tag(state, "K")
        assert tag == "K1"
        assert get_tag_number(state, "K") == 1
        
        state, tag = next_tag(state, "K")
        assert tag == "K2"

    def test_format_tag(self):
        assert format_tag("X", 5) == "X5"

    def test_generate_pin_range(self):
        # Normal
        pins = generate_pin_range(1, 3, skip_odd=False)
        assert pins == ("1", "2", "3")
        
        # Skip odd (start counting from 1)
        # 1 (odd) -> "", 2 (even) -> "2", 3 (odd) -> ""
        # The range is 1,2,3.
        pins = generate_pin_range(1, 3, skip_odd=True)
        assert pins == ("", "2", "")
        
        # Thermal specific (usually starts at 1, so 1->"", 2->2... wait logic check)
        # logic: tuple("" if i % 2 == 1 else str(i) for i in range(start, start + count))
        # if start=1, count=6: 1,2,3,4,5,6 -> "", "2", "", "4", "", "6"
        pins = generate_pin_range(1, 6, skip_odd=True)
        assert pins == ("", "2", "", "4", "", "6")

    def test_auto_thermal_pins(self):
        # auto_thermal_pins(base=2, poles=3)
        # calls generate_pin_range(base - 1, poles * 2, skip_odd=True)
        # range(1, 7) -> 1,2,3,4,5,6
        # filters odd -> "", "2", "", "4", "", "6"
        pins = auto_thermal_pins(base=2, poles=3)
        assert pins == ("", "2", "", "4", "", "6")

    def test_next_terminal_pins(self):
        state = create_autonumberer()
        
        # First call (poles=3)
        # Should start at 1.
        # Pins: 1, "", 2, "", 3, ""
        # Counter increments by 3
        state, pins = next_terminal_pins(state, poles=3)
        assert pins == ("1", "", "2", "", "3", "")
        assert state['pin_counter'] == 3
        
        # Second call
        # Start at 4
        # Pins: 4, "", 5, "", 6, ""
        state, pins = next_terminal_pins(state, poles=3)
        assert pins == ("4", "", "5", "", "6", "")
        assert state['pin_counter'] == 6

    def test_auto_functions(self):
        assert auto_coil_pins() == ("A1", "A2")
        assert auto_contact_pins(1, 2) == ("1", "2", "3", "4")
        assert auto_terminal_pins(1, 2) == ("1", "2", "3", "4")
