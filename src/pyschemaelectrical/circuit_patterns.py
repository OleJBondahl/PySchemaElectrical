from typing import Dict, Any, Callable, Optional, Tuple, List
from pyschemaelectrical.system import layout_horizontal

def create_horizontal_layout(
    state: Dict[str, Any],
    start_x: float,
    start_y: float,
    count: int,
    spacing: float,
    generator_func_single: Callable[[Dict[str, Any], float, float, Dict[str, Any], Dict[str, Any]], Tuple[Dict[str, Any], Any]],
    default_tag_generators: Dict[str, Callable],
    tag_generators: Optional[Dict[str, Callable]] = None,
    terminal_maps: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], List[Any]]:
    """
    Generic function to create multiple circuits horizontally.
    
    Args:
        state: Autonumbering state.
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        count: Number of circuits to generate.
        spacing: Horizontal spacing between circuits.
        generator_func_single: Function to create a single circuit. 
                               Signature: (state, x, y, tag_generators, terminal_maps) -> (new_state, elements)
        default_tag_generators: Default tag generators for the circuit type.
        tag_generators: Optional user-provided tag generators to override defaults.
        terminal_maps: Optional user-provided terminal maps.
        
    Returns:
        (final_state, all_elements)
    """
    
    tm = terminal_maps or {}
    gens = default_tag_generators.copy()
    if tag_generators:
        gens.update(tag_generators)

    # Wrap the single circuit creator to match layout_horizontal's expected signature
    def generator_func_wrapper(s, x, y):
        # We pass the resolved generators and maps to the single circuit creator
        return generator_func_single(s, x, y, gens, tm)

    return layout_horizontal(
        start_state=state,
        start_x=start_x,
        start_y=start_y,
        spacing=spacing,
        count=count,
        generate_func=generator_func_wrapper
    )
