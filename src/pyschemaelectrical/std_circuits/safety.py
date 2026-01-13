"""
Standard Safety Circuits.

Note: This module requires terminal IDs to be passed from the calling project.
No terminal constants are hard-coded in the library.
"""

from typing import Any, Tuple, List
from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.symbols.assemblies import emergency_stop_assembly

def create_emergency_stop(
    state: Any, 
    x: float, 
    y: float,
    terminal_1: str = None,
    terminal_2: str = None,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Create an Emergency Stop circuit.
    
    Args:
        terminal_1: Input terminal ID
        terminal_2: Output terminal ID  
    """
    if not all([terminal_1, terminal_2]):
        raise ValueError("terminal_1 and terminal_2 are required parameters")
    
    builder = CircuitBuilder(state)
    builder.set_layout(x, y)
    
    builder.add_terminal(terminal_1, count=1)
    builder.add_component(emergency_stop_assembly, tag_prefix="S")
    builder.add_terminal(terminal_2, count=1)

    
    result = builder.build(count=kwargs.get("count", 1))
    return result.state, result.circuit, result.used_terminals
