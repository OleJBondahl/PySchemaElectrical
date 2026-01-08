from pyschemaelectrical.system import layout_horizontal
from pyschemaelectrical.core import Element, Point
from pyschemaelectrical.autonumbering import create_autonumberer

def mock_circuit_generator(state, x, y):
    # Mock generator that increments a counter in state and returns a dummy element
    count = state.get('count', 0)
    new_state = state.copy()
    new_state['count'] = count + 1
    
    # Return a dummy element with the given position
    element = Point(x, y) # Point is frozen, so it's a valid Element subclass? No, Point is not Element.
    # We need an Element.
    # Let's import Line? Or just a mock class.
    
    return new_state, [element]

def test_layout_horizontal():
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
    
    # Check positions
    # Elements are Points (mocked)
    p1 = elements[0]
    p2 = elements[1]
    p3 = elements[2]
    
    assert p1.x == 0
    assert p2.x == 10
    assert p3.x == 20
