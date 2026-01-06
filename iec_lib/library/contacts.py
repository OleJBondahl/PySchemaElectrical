from dataclasses import replace
from typing import Dict, List, Optional, Tuple
from ..core import Point, Vector, Port, Symbol, Style
from ..primitives import Line, Element, Text
from ..transform import translate
from ..parts import box, standard_text, standard_style, create_pin_labels, three_pole_factory
from ..constants import GRID_SIZE, DEFAULT_POLE_SPACING, TEXT_SIZE_PIN, TEXT_FONT_FAMILY_AUX, COLOR_BLACK

"""
IEC 60617 Contact Symbols.

This module contains functions to generate contact symbols including:
- Normally Open (NO)
- Normally Closed (NC)
- Changeover (SPDT)
"""

def three_pole_normally_open(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """
    Create an IEC 60617 Three Pole Normally Open Contact.
    
    Composed of 3 single NO contacts.
    
    Args:
        label (str): The component tag (e.g. "-K1").
        pins (tuple): A tuple of 6 pin numbers (e.g. ("1","2","3","4","5","6")).
        
    Returns:
        Symbol: The 3-pole symbol.
    """
    return three_pole_factory(normally_open, label, pins)

def normally_open(label: str = "", pins: tuple = ()) -> Symbol:
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
    
def three_pole_normally_closed(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """
    Create an IEC 60617 Three Pole Normally Closed Contact.
    
    Args:
        label (str): The component tag.
        pins (tuple): A tuple of 6 pin numbers.
        
    Returns:
        Symbol: The 3-pole symbol.
    """
    return three_pole_factory(normally_closed, label, pins)

def normally_closed(label: str = "", pins: tuple = ()) -> Symbol:
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

def spdt_contact(label: str = "", pins: tuple = ("1", "2", "4")) -> Symbol:
    """
    Create an IEC 60617 Single Pole Double Throw (SPDT) Contact (Changeover).
    
    Combined NO and NC contact.
    One input (Common) and two outputs (NC, NO).
    Breaker arm rests at the NC contact.
    
    Symbol Layout:
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
        
    Returns:
        Symbol: The symbol.
    """
    
    h_half = GRID_SIZE # 5.0
    top_y = -GRID_SIZE / 2 # -2.5
    bot_y = GRID_SIZE / 2  # 2.5
    
    x_right = GRID_SIZE / 2  # 2.5
    x_left = -GRID_SIZE / 2  # -2.5
    
    style = standard_style()
    
    # Common (Input) - Bottom Right
    # Pivot point at (2.5, 2.5)
    # Vertical lead down to port
    l_com = Line(Point(x_right, bot_y), Point(x_right, h_half), style)
    
    # NO (Output) - Top Right
    # Vertical lead up to port
    l_no = Line(Point(x_right, -h_half), Point(x_right, top_y), style)
    
    # NC (Output) - Top Left
    # Vertical lead up to port
    l_nc = Line(Point(x_left, -h_half), Point(x_left, top_y), style)
    
    # NC Seat (Horizontal)
    # Extends from left vertical line towards the center/right
    # Let's extend it to x=0 to give the blade a target
    nc_seat_end_x = 0
    seat_nc = Line(Point(x_left, top_y), Point(nc_seat_end_x, top_y), style)
    
    # Blade
    # Starts at Common Pivot (Right, Bottom) -> (2.5, 2.5)
    blade_start = Point(x_right, bot_y)
    
    # Target is the end of the NC seat
    target_x = nc_seat_end_x
    target_y = top_y
    
    dx = target_x - blade_start.x
    dy = target_y - blade_start.y
    length = (dx**2 + dy**2)**0.5
    
    extension = GRID_SIZE / 4
    new_length = length + extension
    scale = new_length / length
    
    blade_end = Point(blade_start.x + dx * scale, blade_start.y + dy * scale)
    blade = Line(blade_start, blade_end, style)
    
    elements = [l_com, l_no, l_nc, seat_nc, blade]
    
    if label:
        elements.append(standard_text(label, Point(0, 0)))
        
    ports = {
        "1": Port("1", Point(x_right, h_half), Vector(0, 1)),      # Common (Right)
        "2": Port("2", Point(x_left, -h_half), Vector(0, -1)),     # NC (Left)
        "4": Port("4", Point(x_right, -h_half), Vector(0, -1))     # NO (Right)
    }
    
    if pins:
        # Expected tuple: (Common, NC, NO)
        p_labels = list(pins)
        while len(p_labels) < 3:
            p_labels.append("")
            
        common_pin, nc_pin, no_pin = p_labels[0], p_labels[1], p_labels[2]
        
        offset = 2.0 # mm
        
        if common_pin:
             # Common is at (2.5, 2.5). Port 1 is at (2.5, 5.0).
             # Wait, Port 1 is at (x_right, h_half) = (2.5, 5.0).
             # Label on Right: x + offset
             pos = ports["1"].position
             elements.append(Text(
                content=common_pin,
                position=Point(pos.x + offset, pos.y),
                anchor="start", # Left aligned, grows Right
                font_size=TEXT_SIZE_PIN,
                style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
            ))
            
        if nc_pin:
             # NC is at (-2.5, -5.0). Port 2.
             # Label on Left: x - offset
             pos = ports["2"].position
             elements.append(Text(
                content=nc_pin,
                position=Point(pos.x - offset, pos.y),
                anchor="end", # Right aligned, grows Left
                font_size=TEXT_SIZE_PIN,
                style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
            ))

        if no_pin:
             # NO is at (2.5, -5.0). Port 4.
             # Label on Right: x + offset
             pos = ports["4"].position
             elements.append(Text(
                content=no_pin,
                position=Point(pos.x + offset, pos.y),
                anchor="start", # Left aligned, grows Right
                font_size=TEXT_SIZE_PIN,
                style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
            ))

    return Symbol(elements, ports, label=label)
