from typing import Tuple, Dict, Any
from dataclasses import replace
from ..core import Symbol, Point, Style, Element
from ..primitives import Line
from ..transform import translate
from ..constants import DEFAULT_POLE_SPACING, GRID_SIZE, LINE_WIDTH_THIN, LINKAGE_DASH_PATTERN, COLOR_BLACK
from .contacts import three_pole_normally_open
from .coils import coil

def contactor(label: str = "", 
              coil_pins: Tuple[str, str] = ("A1", "A2"), 
              contact_pins: Tuple[str, str, str, str, str, str] = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """
    High-level contactor symbol.
    
    Combines a 3-pole NO contact block and a Coil.
    The coil is placed to the left of the contacts.
    A mechanical linkage (stippled line) connects the coil to the contacts.
    
    Args:
        label (str): The device label (e.g. "-K1").
        coil_pins (Tuple[str, str]): Pins for the coil (A1, A2).
        contact_pins (Tuple[str, ...]): Pins for the 3-pole contact (1..6).
        
    Returns:
        Symbol: The composite contactor symbol.
    """
    
    # 1. Create the contacts
    # The contacts are centered at (0,0), (10,0), (20,0) by default in three_pole_normally_open
    # (assuming DEFAULT_POLE_SPACING is 10mm)
    contacts_sym = three_pole_normally_open(label="", pins=contact_pins)
    
    # 2. Create the coil with label - it handles its own label placement
    coil_offset_x = -DEFAULT_POLE_SPACING*2
    coil_sym = coil(label=label, pins=coil_pins)
    coil_sym = translate(coil_sym, coil_offset_x, 0)
    
    # 3. Create the mechanical linkage (stippled line)
    linkage_start = Point(coil_offset_x+DEFAULT_POLE_SPACING/2, 0)
    linkage_end = Point(DEFAULT_POLE_SPACING * 1.75, 0)
    
    linkage_style = Style(
        stroke=COLOR_BLACK,
        stroke_width=LINE_WIDTH_THIN,
        stroke_dasharray=LINKAGE_DASH_PATTERN
    )
    
    linkage_line = Line(linkage_start, linkage_end, linkage_style)
    
    # 4. Combine everything - coil already has the label
    all_elements = contacts_sym.elements + coil_sym.elements + [linkage_line]
    
    # Merge ports
    all_ports = {**contacts_sym.ports, **coil_sym.ports}
    
    return Symbol(elements=all_elements, ports=all_ports, label=label)
