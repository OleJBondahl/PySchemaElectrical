from typing import Callable, Tuple, Any, Dict, List
from .core import Element

def layout_horizontal(
    start_state: Dict[str, Any],
    start_x: float,
    start_y: float,
    spacing: float,
    count: int,
    generate_func: Callable[[Dict[str, Any], float, float], Tuple[Dict[str, Any], List[Element]]]
) -> Tuple[Dict[str, Any], List[Element]]:
    """
    Layout multiple copies of a circuit horizontally, propagating state.
    
    Args:
        start_state: Initial autonumbering state.
        start_x: X position of the first circuit.
        start_y: Y position for all circuits.
        spacing: Horizontal distance between circuits.
        count: Number of copies to create.
        generate_func: Function that takes (state, x, y) and returns (new_state, elements).
                       Expected signature: 
                       f(state: Dict, x: float, y: float) -> (Dict, List[Element])
                       
    Returns:
        Tuple[Dict[str, Any], List[Element]]: Final state and list of all elements.
    """
    current_state = start_state
    all_elements = []
    
    for i in range(count):
        x_pos = start_x + (i * spacing)
        # Pass current_state, receive new state
        current_state, elems = generate_func(current_state, x_pos, start_y)
        all_elements.extend(elems)
        
    return current_state, all_elements
