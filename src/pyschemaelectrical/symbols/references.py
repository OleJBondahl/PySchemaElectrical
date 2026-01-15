from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from pyschemaelectrical.model.core import Point, Vector, Port, Symbol, Element
from pyschemaelectrical.model.parts import standard_style, standard_text
from pyschemaelectrical.model.primitives import Line, Polygon

from pyschemaelectrical.model.constants import (
    REF_ARROW_LENGTH, 
    REF_ARROW_HEAD_LENGTH, 
    REF_ARROW_HEAD_WIDTH
)

@dataclass(frozen=True)
class RefSymbol(Symbol):
    pass

def ref_symbol(tag: str = "", label: str = "", pins: Tuple[str, ...] = (), direction: str = "up", **kwargs) -> RefSymbol:
    """
    Reference symbol (arrow) to indicate connection to another circuit element.
    
    Args:
        tag (str): Auto-generated tag (usually ignored if label is present).
        label (str): The text to display (e.g. "F1:1"). If empty, uses tag.
        pins (tuple): Ignored, present for builder compatibility.
        direction (str): "up" (points up, connects from below) or "down" (points down, connects from above).
        **kwargs: Extra arguments for compatibility.
    """
    elements: List[Element] = []
    ports: Dict[str, Port] = {}
    
    text_content = label if label else tag
    
    origin = Point(0, 0)
    
    style = standard_style()
    
    if direction == "up":
        # Arrow pointing UP from origin.
        # Symbol is Placed at (X, Y). Connection port is at (X, Y).
        # The Arrow extends UPWARDS from (X, Y).
        # This symbol acts as a SOURCE/TOP connection point.
        # Components connect to it from BELOW.
        
        end_pt = Point(0, -REF_ARROW_LENGTH)
        
        # Shaft: Line from Origin to Tip
        elements.append(Line(origin, end_pt, style))
        
        # Arrow Head at Tip (pointing UP)
        # ^
        head_base_y = end_pt.y + REF_ARROW_HEAD_LENGTH
        p_left = Point(-REF_ARROW_HEAD_WIDTH/2, head_base_y)
        p_right = Point(REF_ARROW_HEAD_WIDTH/2, head_base_y)
        
        elements.append(Polygon([p_left, end_pt, p_right], style))
        
        # Label: Placed to the right of the middle of the shaft
        # standard_text(pos='right') moves text to x=5, anchor=start.
        mid_y = -REF_ARROW_LENGTH / 2
        elements.append(standard_text(text_content, Point(0, mid_y), label_pos='right'))
        
        # Port: Connects to below (output/down)
        ports["2"] = Port("2", origin, Vector(0, 1))

    else: # down
        # Arrow pointing DOWN from origin.
        # Symbol is Placed at (X, Y). Connection port is at (X, Y).
        # The Arrow extends DOWNWARDS from (X, Y).
        # This symbol acts as a SINK/BOTTOM connection point.
        # Components connect to it from ABOVE.
        
        end_pt = Point(0, REF_ARROW_LENGTH)
        
        # Shaft
        elements.append(Line(origin, end_pt, style))
        
        # Arrow Head at Tip (pointing DOWN)
        # v
        head_base_y = end_pt.y - REF_ARROW_HEAD_LENGTH
        p_left = Point(-REF_ARROW_HEAD_WIDTH/2, head_base_y)
        p_right = Point(REF_ARROW_HEAD_WIDTH/2, head_base_y)
        
        elements.append(Polygon([p_left, end_pt, p_right], style))
        
        # Label
        mid_y = REF_ARROW_LENGTH / 2
        elements.append(standard_text(text_content, Point(0, mid_y), label_pos='right'))
        
        # Port: Connects to above (input/up)
        ports["1"] = Port("1", origin, Vector(0, -1))

    return RefSymbol(elements=elements, ports=ports, label=text_content)
