from typing import Dict, List
from ..core import Point, Vector, Port, Symbol, Style
from ..primitives import Element, Text, Line
from ..parts import box, standard_text, create_pin_labels, GRID_SIZE, standard_style
from ..constants import GRID_SUBDIVISION

"""
IEC 60617 Coil Symbols.
"""

def coil(label: str = "", pins: tuple = ()) -> Symbol:
    """
    Create an IEC 60617 Coil symbol (Square).
    
    Symbol Layout:
       |
      [ ]
       |
       
    Dimensions:
        Width: 10mm (2 * GRID_SIZE)
        Height: 10mm (2 * GRID_SIZE)
        
    Args:
        label (str): The component tag (e.g. "-K1").
        pins (tuple): Pin numbers (e.g. ("A1", "A2")).
        
    Returns:
        Symbol: The coil symbol.
    """
    # Size: Width 10mm, Height 10mm.
    # Typically A1 (top) and A2 (bottom).
    width = 2 * GRID_SIZE
    height = GRID_SIZE
    
    body = box(Point(0, 0), width, height)
    style = standard_style()
    
    # Pins
    pin_len = GRID_SUBDIVISION
    top_y_box = -height/2
    bot_y_box = height/2
    
    top_y_port = top_y_box - pin_len
    bot_y_port = bot_y_box + pin_len
    
    l1 = Line(Point(0, top_y_box), Point(0, top_y_port), style)
    l2 = Line(Point(0, bot_y_box), Point(0, bot_y_port), style)
    
    ports = {
        "A1": Port("A1", Point(0, top_y_port), Vector(0, -1)),
        "A2": Port("A2", Point(0, bot_y_port), Vector(0, 1))
    }
    
    elements = [body, l1, l2]
    if label:
        # Place label half grid more to the left because coil is wider than other symbols
        elements.append(standard_text(label, Point(-GRID_SUBDIVISION, 0)))
        
    if pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)
