from dataclasses import dataclass, field
from typing import Callable, Tuple, Any, Dict, List, Union, Optional
from .core import Symbol, Element
from .transform import translate
from .layout import auto_connect
from .renderer import render_to_svg, DEFAULT_DOC_WIDTH, DEFAULT_DOC_HEIGHT

@dataclass
class Circuit:
    """
    A container for electrical symbols and their connections.
    
    Attributes:
        symbols (List[Symbol]): Ordered list of main components.
        elements (List[Element]): All graphical elements (symbols + wires).
    """
    symbols: List[Symbol] = field(default_factory=list)
    elements: List[Element] = field(default_factory=list)

def add_symbol(circuit: Circuit, symbol: Symbol, x: float, y: float) -> Symbol:
    """
    Add a symbol to the circuit at a specified position.
    
    This function handles the translation of the symbol to the given coordinates
    and adds it to the circuit's internal storage.
    
    Args:
        circuit (Circuit): The circuit to add to.
        symbol (Symbol): The symbol instance to add (usually created from symbols library).
        x (float): The x-coordinate.
        y (float): The y-coordinate.
        
    Returns:
        Symbol: The placed (translated) symbol.
    """
    placed_symbol = translate(symbol, x, y)
    circuit.symbols.append(placed_symbol)
    circuit.elements.append(placed_symbol)
    return placed_symbol

def auto_connect_circuit(circuit: Circuit):
    """
    Automatically connect all adjacent symbols in the circuit.
    
    Iterates through the symbols in the order they were added and connects
    each symbol to the next one using auto_connect logic.
    
    Args:
        circuit (Circuit): The circuit to process.
    """
    for i in range(len(circuit.symbols) - 1):
        s1 = circuit.symbols[i]
        s2 = circuit.symbols[i+1]
        lines = auto_connect(s1, s2)
        circuit.elements.extend(lines)

def render_system(
    circuits: Union[Circuit, List[Circuit]], 
    filename: str, 
    width: Union[str, int] = DEFAULT_DOC_WIDTH, 
    height: Union[str, int] = DEFAULT_DOC_HEIGHT
):
    """
    Render one or more circuits to an SVG file.
    
    Args:
        circuits (Union[Circuit, List[Circuit]]): A single Circuit or list of Circuits.
        filename (str): The output file path.
        width (str|int): Document width.
        height (str|int): Document height.
    """
    all_elements = []
    
    # Normalize to list
    circuit_list = circuits if isinstance(circuits, list) else [circuits]
    
    for c in circuit_list:
        all_elements.extend(c.elements)
        
    render_to_svg(all_elements, filename, width=width, height=height)

# --- Legacy / Functional Helpers ---

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
