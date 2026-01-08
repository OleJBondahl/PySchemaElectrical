from typing import Tuple, List, Optional
from ..core import Point, Vector, Port, Symbol, Style, Element
from ..primitives import Text, Line
from ..parts import box, standard_text, standard_style
from ..constants import (
    GRID_SIZE, 
    DEFAULT_POLE_SPACING, 
    COLOR_BLACK, 
    TEXT_SIZE_PIN, 
    TEXT_FONT_FAMILY_AUX
)

def terminal_box(label: str = "", num_pins: int = 1, start_pin_number: int = 1, pin_spacing: float = DEFAULT_POLE_SPACING) -> Symbol:
    """
    Create a Rectangular Terminal Box Symbol.
    
    Dimensions:
        Height: Equalt to pin_spacing (default 10mm / 2 grids).
        Width: Flexible (num_pins - 1) * spacing + 1 Grid (padding 0.5 grid each side).
        Pins: Pointing upwards.
        Pin Numbers: LEFT of the pins.
    
    Args:
        label (str): Component tag.
        num_pins (int): Number of pins/terminals.
        start_pin_number (int): Starting number for pin labels.
        pin_spacing (float): distance between pins.
        
    Returns:
        Symbol: The symbol.
    """
    
    if num_pins < 1:
        num_pins = 1
        
    style = standard_style()
    
    # "box is to short in the height direction, increase to the same as pin spacing"
    # Pin Spacing default is 10.0 (2 Grid).
    box_height = pin_spacing 
    
    # Standard Pin length and alignment
    # Pin points UP from Top of box.
    # Origin (0,0) at Top Edge of Box where first pin starts?
    # Or Origin at First Port?
    # Sticking with: Origin (0,0) is at Box Top Edge, First Pin X.
    # Pin extends Up from 0 to -pin_length.
    
    pin_length = GRID_SIZE / 2 # 2.5mm
    padding = GRID_SIZE / 2 # 2.5mm
    
    span = (num_pins - 1) * pin_spacing
    box_width = span + 2 * padding
    
    # Center of box
    # X: span / 2
    # Y: box_height / 2 (Below 0)
    center_x = span / 2
    center_y = box_height / 2
    
    rect = box(Point(center_x, center_y), box_width, box_height, filled=False)
    
    elements: List[Element] = [rect]
    ports = {}
    
    for i in range(num_pins):
        p_num = start_pin_number + i
        p_str = str(p_num)
        
        px = i * pin_spacing
        
        # Pin Line
        # From box top (0) upwards to (-pin_length)
        l = Line(Point(px, 0), Point(px, -pin_length), style)
        elements.append(l)
        
        # Port at tip
        ports[p_str] = Port(p_str, Point(px, -pin_length), Vector(0, -1))
        
        # Pin Number
        # "always put the pin numbers of the left of the pins"
        # Position: px - offset
        
        text_x = px - 1.0 # 1mm to the LEFT of pin
        text_y = -pin_length / 2 # Middle of the pin line
        
        text = Text(
            content=p_str,
            position=Point(text_x, text_y),
            anchor="end", # Right aligned (End of text touches x)
            dominant_baseline="middle",
            font_size=TEXT_SIZE_PIN,
            style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
        )
        elements.append(text)

    if label:
        elements.append(standard_text(label, Point(0, 0)))

    return Symbol(elements, ports, label=label)
