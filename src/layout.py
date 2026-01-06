from typing import List, Optional, Dict, Union
from .core import Symbol, Point, Vector, Element, Port
from .primitives import Line
from .transform import translate
from .parts import standard_style

def get_connection_ports(symbol: Symbol, direction: Vector) -> List[Port]:
    """
    Find all ports in the symbol that match the given direction.
    
    Args:
        symbol (Symbol): The symbol to check.
        direction (Vector): The direction vector to match.
        
    Returns:
        List[Port]: A list of matching ports.
    """
    matches = []
    for p in symbol.ports.values():
        dx = abs(p.direction.dx - direction.dx)
        dy = abs(p.direction.dy - direction.dy)
        if dx < 1e-6 and dy < 1e-6:
            matches.append(p)
    return matches

def auto_connect(sym1: Symbol, sym2: Symbol) -> List[Line]:
    """
    Automatically connects two symbols with Lines.
    
    Finds all downward facing ports in sym1 and upward facing ports in sym2.
    Connects pairs that are horizontally aligned.
    
    Args:
        sym1 (Symbol): The upper symbol (source).
        sym2 (Symbol): The lower symbol (target).
        
    Returns:
        List[Line]: A list of connection lines.
    """
    lines = []
    
    down_ports = get_connection_ports(sym1, Vector(0, 1))
    up_ports = get_connection_ports(sym2, Vector(0, -1))
    
    for dp in down_ports:
        for up in up_ports:
            # Check vertical alignment (same X)
            if abs(dp.position.x - up.position.x) < 0.1: # Strict tolerance
                lines.append(Line(dp.position, up.position, style=standard_style()))
                
    return lines


def auto_connect_labeled(
    sym1: Symbol,
    sym2: Symbol,
    wire_specs: Optional[Union[Dict[str, tuple], List[tuple]]] = None
) -> List[Element]:
    """
    Automatically connects two symbols with labeled wires.
    
    High-level function that creates connections between aligned ports
    and adds wire specification labels (color, size) to each wire.
    
    Finds all downward facing ports in sym1 and upward facing ports in sym2.
    Connects pairs that are horizontally aligned and adds labels based on
    wire specifications.
    
    Args:
        sym1 (Symbol): The upper symbol (source).
        sym2 (Symbol): The lower symbol (target).
        wire_specs: Specification for wire labels.
            - If Dict[str, tuple]: Maps Port ID to (color, size).
            - If List[tuple]: Maps (color, size) to ports by X-position (Left to Right).
            If None or not found, wire is created without label.
        
    Returns:
        List[Element]: List of connection lines and label texts.
    """
    from .wire_labels import create_labeled_wire
    
    elements = []
    wire_specs = wire_specs or {}
    
    # Get ports
    down_ports = get_connection_ports(sym1, Vector(0, 1))
    up_ports = get_connection_ports(sym2, Vector(0, -1))
    
    # Sort downward ports by X position for list-based matching
    down_ports.sort(key=lambda p: p.position.x)
    
    match_count = 0
    for dp in down_ports:
        # Find matching upward port
        matched_up = None
        for up in up_ports:
            if abs(dp.position.x - up.position.x) < 0.1:
                matched_up = up
                break
        
        if matched_up:
            # Determine label spec
            spec = ("", "")
            
            if isinstance(wire_specs, list):
                if match_count < len(wire_specs):
                    spec = wire_specs[match_count]
                match_count += 1
            elif isinstance(wire_specs, dict):
                spec = wire_specs.get(dp.id, ("", ""))
                
            color, size = spec if isinstance(spec, tuple) else ("", "")
            
            # Create labeled wire
            wire_elements = create_labeled_wire(
                dp.position,
                matched_up.position,
                color,
                size
            )
            elements.extend(wire_elements)
                
    return elements

def layout_vertical_chain(symbols: List[Symbol], start: Point, spacing: float) -> List[Element]:
    """
    Arranges a list of symbols in a vertical column and connects them.
    
    Args:
        symbols (List[Symbol]): List of Symbol templates (usually centered at 0,0).
        start (Point): Starting Point (center of the first symbol).
        spacing (float): Vertical distance between centers.
        
    Returns:
        List[Element]: List of Elements (Placed Symbols and Connecting Lines).
    """
    elements = []
    placed_symbols = []
    
    current_x = start.x
    current_y = start.y
    
    for sym in symbols:
        # Place symbol
        # Assuming sym is at (0,0), we translate it.
        # If sym is already placed (not at 0,0), this might be wrong.
        # We assume library returns fresh symbols at 0,0.
        placed = translate(sym, current_x - 0, current_y - 0) # Assuming origin is 0,0
        
        placed_symbols.append(placed)
        elements.append(placed)
        
        current_y += spacing
        
    # Connect them
    for i in range(len(placed_symbols) - 1):
        top = placed_symbols[i]
        bot = placed_symbols[i+1]
        
        lines = auto_connect(top, bot)
        elements.extend(lines)
            
    return elements
