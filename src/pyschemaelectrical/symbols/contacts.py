from dataclasses import replace
from typing import Dict, List, Optional, Tuple
from pyschemaelectrical.model.core import Point, Vector, Port, Symbol, Style
from pyschemaelectrical.model.primitives import Line, Element, Text
from pyschemaelectrical.utils.transform import translate
from pyschemaelectrical.model.parts import box, standard_text, standard_style, create_pin_labels, three_pole_factory
from pyschemaelectrical.model.constants import GRID_SIZE, DEFAULT_POLE_SPACING, TEXT_SIZE_PIN, TEXT_FONT_FAMILY_AUX, COLOR_BLACK

"""
IEC 60617 Contact Symbols.

This module contains functions to generate contact symbols including:
- Normally Open (NO)
- Normally Closed (NC)
- Changeover (SPDT)
"""

def three_pole_normally_open_symbol(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """
    Create an IEC 60617 Three Pole Normally Open Contact.
    
    Composed of 3 single NO contacts.
    
    Args:
        label (str): The component tag (e.g. "-K1").
        pins (tuple): A tuple of 6 pin numbers (e.g. ("1","2","3","4","5","6")).
        
    Returns:
        Symbol: The 3-pole symbol.
    """
    return three_pole_factory(normally_open_symbol, label, pins)

def normally_open_symbol(label: str = "", pins: tuple = ()) -> Symbol:
    """
    Create an IEC 60617 Normally Open Contact.
    
    Symbol Layout:
        |
       / 
      |
    
    Dimensions:
        Height: 10mm (2 * GRID_SIZE)
        Width: Compatible with standard grid.
        
    Args:
        label (str): The component tag.
        pins (tuple): A tuple of pin numbers (up to 2).
        
    Returns:
        Symbol: The symbol.
    """
    
    h_half = GRID_SIZE # 5.0
    
    # Gap: -2.5 to 2.5 (5mm gap)
    top_y = -GRID_SIZE / 2
    bot_y = GRID_SIZE / 2
    
    style = standard_style()
    
    # Vertical leads
    l1 = Line(Point(0, -h_half), Point(0, top_y), style)
    l2 = Line(Point(0, bot_y), Point(0, h_half), style)
    
    # Blade
    # Starts at the bottom contact point (0, 2.5)
    # End to the LEFT (-2.5, -2.5)
    blade_start = Point(0, bot_y)
    blade_end = Point(-GRID_SIZE / 2, top_y) 
    
    blade = Line(blade_start, blade_end, style)
    
    elements = [l1, l2, blade]
    if label:
        elements.append(standard_text(label, Point(0, 0)))
        
    ports = {
        "1": Port("1", Point(0, -h_half), Vector(0, -1)),
        "2": Port("2", Point(0, h_half), Vector(0, 1))
    }
    
    if pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)
    
def three_pole_normally_closed_symbol(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """
    Create an IEC 60617 Three Pole Normally Closed Contact.
    
    Args:
        label (str): The component tag.
        pins (tuple): A tuple of 6 pin numbers.
        
    Returns:
        Symbol: The 3-pole symbol.
    """
    return three_pole_factory(normally_closed_symbol, label, pins)

def normally_closed_symbol(label: str = "", pins: tuple = ()) -> Symbol:
    """
    Create an IEC 60617 Normally Closed Contact.
    
    Symbol Layout:
       |
       |--
      /
     |
     
    Args:
        label (str): The component tag.
        pins (tuple): A tuple of pin numbers (up to 2).
        
    Returns:
        Symbol: The symbol.
    """
    
    h_half = GRID_SIZE # 5.0
    top_y = -GRID_SIZE / 2 # -2.5
    bot_y = GRID_SIZE / 2  # 2.5
    
    style = standard_style()
    
    # Vertical lines (Terminals)
    l1 = Line(Point(0, -h_half), Point(0, top_y), style)
    l2 = Line(Point(0, bot_y), Point(0, h_half), style)
    
    # Horizontal Seat (Contact point)
    # Extends from top contact point to the right, to meet the blade
    seat_end_x = GRID_SIZE / 2 # 2.5
    seat = Line(Point(0, top_y), Point(seat_end_x, top_y), style)
    
    # Blade
    # Starts bottom-center, passes through the seat endpoint
    blade_start = Point(0, bot_y)
    
    # Calculate vector to the seat point
    target_x = seat_end_x
    target_y = top_y
    
    dx = target_x - blade_start.x
    dy = target_y - blade_start.y
    length = (dx**2 + dy**2)**0.5
    
    # Extend by 1/4 grid
    extension = GRID_SIZE / 4
    new_length = length + extension
    scale = new_length / length
    
    blade_end = Point(blade_start.x + dx * scale, blade_start.y + dy * scale)
    blade = Line(blade_start, blade_end, style)
    
    elements = [l1, l2, seat, blade]
    
    if label:
        elements.append(standard_text(label, Point(0, 0)))
        
    ports = {
        "1": Port("1", Point(0, -h_half), Vector(0, -1)),
        "2": Port("2", Point(0, h_half), Vector(0, 1))
    }
    
    if pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)

def spdt_contact_symbol(label: str = "", pins: tuple = ("1", "2", "4"), inverted: bool = False) -> Symbol:
    """
    Create an IEC 60617 Single Pole Double Throw (SPDT) Contact (Changeover).
    
    Combined NO and NC contact.
    One input (Common) and two outputs (NC, NO).
    Breaker arm rests at the NC contact.
    
    Symbol Layout (Standard):
       NC      NO
        |__     |
           \    |
            \   |
             \  |
              \ |
               \|
               Com
    
    Alignment:
    - Common and NO are vertically aligned on the right.
    - NC is on the left.
    - Blade spans from Common (Right) to NC (Left).
    
    Args:
        label (str): The component tag.
        pins (tuple): A tuple of 3 pin numbers (Common, NC, NO).
        inverted (bool): If True, Common is at Top, NC/NO at Bottom.
        
    Returns:
        Symbol: The symbol.
    """
    
    h_half = GRID_SIZE # 5.0
    
    # Standard Orientation
    top_y = -GRID_SIZE / 2 # -2.5
    bot_y = GRID_SIZE / 2  # 2.5
    
    x_right = GRID_SIZE / 2  # 2.5
    x_left = -GRID_SIZE / 2  # -2.5
    
    style = standard_style()
    
    elements = []
    
    if not inverted:
        # Standard: Common (Input) - Bottom Right
        l_com = Line(Point(x_right, bot_y), Point(x_right, h_half), style)
        
        # NO (Output) - Top Right
        l_no = Line(Point(x_right, -h_half), Point(x_right, top_y), style)
        
        # NC (Output) - Top Left
        l_nc = Line(Point(x_left, -h_half), Point(x_left, top_y), style)
        
        # NC Seat (Top)
        nc_seat_end_x = 0
        seat_nc = Line(Point(x_left, top_y), Point(nc_seat_end_x, top_y), style)
        
        # Blade: Common (Bot Right) -> NC Seat (Top Center)
        blade_start = Point(x_right, bot_y)
        target_x = nc_seat_end_x
        target_y = top_y
        
        ports = {
            "1": Port("1", Point(x_right, h_half), Vector(0, 1)),      # Common (Bottom)
            "2": Port("2", Point(x_left, -h_half), Vector(0, -1)),     # NC (Top Left)
            "4": Port("4", Point(x_right, -h_half), Vector(0, -1))     # NO (Top Right)
        }
    else:
        # Inverted: Common (Input) - Top Right
        # Common line goes UP from pivot
        l_com = Line(Point(x_right, top_y), Point(x_right, -h_half), style)
        
        # NO (Output) - Bottom Right
        l_no = Line(Point(x_right, bot_y), Point(x_right, h_half), style)
        
        # NC (Output) - Bottom Left
        l_nc = Line(Point(x_left, bot_y), Point(x_left, h_half), style)
        
        # NC Seat (Bottom)
        nc_seat_end_x = 0
        seat_nc = Line(Point(x_left, bot_y), Point(nc_seat_end_x, bot_y), style)
        
        # Blade: Common (Top Right) -> NC Seat (Bottom Center)
        blade_start = Point(x_right, top_y)
        target_x = nc_seat_end_x
        target_y = bot_y
        
        ports = {
            "1": Port("1", Point(x_right, -h_half), Vector(0, -1)),     # Common (Top)
            "2": Port("2", Point(x_left, h_half), Vector(0, 1)),        # NC (Bottom Left)
            "4": Port("4", Point(x_right, h_half), Vector(0, 1))        # NO (Bottom Right)
        }

    # Calculate Blade (Shared Logic)
    dx = target_x - blade_start.x
    dy = target_y - blade_start.y
    length = (dx**2 + dy**2)**0.5
    
    extension = GRID_SIZE / 4
    new_length = length + extension
    scale = new_length / length
    
    blade_end = Point(blade_start.x + dx * scale, blade_start.y + dy * scale)
    blade = Line(blade_start, blade_end, style)
    
    # Assemble standard elements
    if not inverted:
        elements.extend([l_com, l_no, l_nc, seat_nc, blade])
    else:
        # Assuming vars are defined in scope from the block
        elements.extend([l_com, l_no, l_nc, seat_nc, blade])

    if label:
        elements.append(standard_text(label, Point(0, 0)))
        
    if pins:
        # Expected tuple: (Common, NC, NO)
        p_labels = list(pins)
        while len(p_labels) < 3:
            p_labels.append("")
            
        common_pin, nc_pin, no_pin = p_labels[0], p_labels[1], p_labels[2]
        
        offset = 2.0 # mm
        
        if common_pin and "1" in ports:
             pos = ports["1"].position
             # Common aligns Right
             elements.append(Text(
                content=common_pin,
                position=Point(pos.x + offset, pos.y),
                anchor="start",
                font_size=TEXT_SIZE_PIN,
                style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
            ))
            
        if nc_pin and "2" in ports:
             pos = ports["2"].position
             # NC aligns Left
             elements.append(Text(
                content=nc_pin,
                position=Point(pos.x - offset, pos.y),
                anchor="end",
                font_size=TEXT_SIZE_PIN,
                style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
            ))

        if no_pin and "4" in ports:
             pos = ports["4"].position
             # NO aligns Right
             elements.append(Text(
                content=no_pin,
                position=Point(pos.x + offset, pos.y),
                anchor="start", 
                font_size=TEXT_SIZE_PIN,
                style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
            ))

    return Symbol(elements, ports, label=label)

def three_pole_spdt_symbol(label: str = "", pins: tuple = ("11", "12", "14", "21", "22", "24", "31", "32", "34")) -> Symbol:
    """
    Create an IEC 60617 Three Pole SPDT Contact.
    
    Composed of 3 single SPDT contacts.
    
    Args:
        label (str): The component tag.
        pins (tuple): A tuple of 9 pin numbers.
                      Format per pole: (Common, NC, NO).
                      Total: (P1_Com, P1_NC, P1_NO, P2_Com, ..., P3_NO)
        
    Returns:
        Symbol: The 3-pole symbol.
        Ports are keys as: "{pole_index}_{type}"
        - "1_com", "1_nc", "1_no"
        - "2_com", "2_nc", "2_no"
        - "3_com", "3_nc", "3_no"
    """
    if len(pins) < 9:
        # Pad with empty strings if not enough pins provided
        pins = tuple(list(pins) + [""] * (9 - len(pins)))

    # Spacing needs to be wider for SPDT because each pole is wider (has 2 top pins)
    # Standard pole spacing is 10mm (2 grids). SPDT occupies +/- 0.5 grids.
    # To maintain ample clear gap between poles, we use 20mm (4 grids) center-to-center.
    spacing = DEFAULT_POLE_SPACING * 4.0 

    # Pole 1
    p1 = spdt_contact_symbol(label=label, pins=pins[0:3])
    
    # Pole 2
    p2 = spdt_contact_symbol(label="", pins=pins[3:6])
    p2 = translate(p2, spacing, 0)
    
    # Pole 3
    p3 = spdt_contact_symbol(label="", pins=pins[6:9])
    p3 = translate(p3, spacing * 2, 0)
    
    # Combine elements
    all_elements = p1.elements + p2.elements + p3.elements
    
    # Remap ports to unique IDs
    new_ports = {}
    
    poles = [p1, p2, p3]
    for i, p in enumerate(poles):
        pole_id = str(i + 1)
        # spdt_contact ports: "1" (Com), "2" (NC), "4" (NO)
        
        if "1" in p.ports:
            new_key = f"{pole_id}_com"
            new_ports[new_key] = replace(p.ports["1"], id=new_key)
            
        if "2" in p.ports:
            new_key = f"{pole_id}_nc"
            new_ports[new_key] = replace(p.ports["2"], id=new_key)
            
        if "4" in p.ports:
            new_key = f"{pole_id}_no"
            new_ports[new_key] = replace(p.ports["4"], id=new_key)
            
    return Symbol(all_elements, new_ports, label=label)
