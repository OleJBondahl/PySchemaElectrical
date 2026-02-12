from pyschemaelectrical.layout.layout import layout_horizontal
from pyschemaelectrical.model.core import Point


def mock_circuit_generator(state, x, y):
    # Mock generator that increments a counter in state and returns a dummy element
    count = state.get('count', 0)
    new_state = state.copy()
    new_state['count'] = count + 1

    # Return a dummy element with the given position
    # Element is abstract, but we can't instantiate it directly if it's strictly abstract (dataclass isn't abc usually)
    # But Point is NOT an Element.
    # Let's return a list containing a Point? No, return type says List[Element].
    # But for the test, as long as it returns *something* compatible with list extension.
    element = Point(x, y)
    return new_state, [element]

class TestLayoutUnit:
    def test_layout_horizontal(self):
        state = {'count': 0}

        final_state, elements = layout_horizontal(
            start_state=state,
            start_x=0,
            start_y=0,
            spacing=10,
            count=3,
            generate_func=mock_circuit_generator
        )

        assert final_state['count'] == 3
        assert len(elements) == 3

        p1 = elements[0]
        p2 = elements[1]
        p3 = elements[2]

        assert p1.x == 0
        assert p2.x == 10
        assert p3.x == 20
