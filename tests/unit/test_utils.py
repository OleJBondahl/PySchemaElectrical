from pyschemaelectrical.utils.autonumbering import (
    auto_coil_pins,
    auto_contact_pins,
    create_autonumberer,
    generate_pin_range,
    get_tag_number,
    increment_tag,
    next_tag,
    next_terminal_pins,
)


class TestUtils:
    def test_autonumberer_workflow(self):
        state = create_autonumberer()
        assert get_tag_number(state, "K") == 0

        state = increment_tag(state, "K")
        assert get_tag_number(state, "K") == 1

        state, tag = next_tag(state, "K")
        assert tag == "K2"
        assert get_tag_number(state, "K") == 2

    def test_pin_generators(self):
        # Basic range
        assert generate_pin_range(1, 3) == ("1", "2", "3")

        # Skip odd (thermal/contact use case usually)
        # 1->"", 2->2, 3->""
        assert generate_pin_range(1, 3, skip_odd=True) == ("", "2", "")

        # Auto helpers
        assert auto_coil_pins() == ("A1", "A2")
        assert auto_contact_pins(1, 2) == ("1", "2", "3", "4")

    def test_terminal_pins_logic(self):
        state = create_autonumberer()

        # New terminal sequence for X1
        state, pins = next_terminal_pins(state, "X1", poles=3)
        assert pins == ("1", "2", "3")

        # Continuation
        state, pins = next_terminal_pins(state, "X1", poles=3)
        assert pins == ("4", "5", "6")

        # Independent terminal X2
        state, pins = next_terminal_pins(state, "X2", poles=2)
        assert pins == ("1", "2")
