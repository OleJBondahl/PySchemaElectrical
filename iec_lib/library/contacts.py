from dataclasses import replace
from typing import Dict, List, Optional
from ..core import Point, Vector, Port, Symbol, Style
from ..primitives import Line, Element, Text
from ..transform import translate
from ..parts import box, standard_text, standard_style, create_pin_labels, three_pole_factory
from ..constants import GRID_SIZE, DEFAULT_POLE_SPACING

def three_pole_normally_open(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """IEC 60617 Three Pole Normally Open Contact.
    
    Composed of 3 single NO contacts.
    """
    return three_pole_factory(normally_open, label, pins)

def normally_open(label: str = "", pins: tuple = ()) -> Symbol:
    """IEC 60617 Normally Open Contact.
    
    Symbol:
        |
       / 
      |
    """
    
    # Grid is 5mm.
    # Total height 2 * GRID_SIZE (10mm).
    # Center at (0,0). Top port at (0, -5), Bot port at (0, 5).
    # Align gap and blade to grid (2.5mm / 5.0mm).
    
    h_half = GRID_SIZE # 5.0
    
    # Gap: -2.5 to 2.5 (5mm gap)
    top_y = -GRID_SIZE / 2
    bot_y = GRID_SIZE / 2
    
    style = standard_style()
    
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
    
    if  pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label=label)
    
def three_pole_normally_closed(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """IEC 60617 Three Pole Normally Closed Contact."""
    return three_pole_factory(normally_closed, label, pins)

def normally_closed(label: str = "", pins: tuple = ()) -> Symbol:
    """IEC 60617 Normally Closed Contact.
    
    Symbol:
       |
       |--
      /
     |
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
