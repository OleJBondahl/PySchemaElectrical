from pyschemaelectrical.utils.autonumbering import (
    create_autonumberer,
    get_tag_number,
    next_tag,
    next_terminal_pins,
)


class TestUtils:
    def test_autonumberer_workflow(self):
        state = create_autonumberer()
        assert get_tag_number(state, "K") == 0

        state, tag = next_tag(state, "K")
        assert tag == "K1"
        assert get_tag_number(state, "K") == 1

        state, tag = next_tag(state, "K")
        assert tag == "K2"
        assert get_tag_number(state, "K") == 2

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
