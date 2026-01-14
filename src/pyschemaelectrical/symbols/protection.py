from typing import Dict, List
from pyschemaelectrical.model.core import Point, Vector, Port, Symbol, Style
from pyschemaelectrical.model.primitives import Line, Element, Text
from pyschemaelectrical.model.parts import box, standard_text, standard_style, create_pin_labels, three_pole_factory
from pyschemaelectrical.model.constants import GRID_SIZE, GRID_SUBDIVISION

def thermal_overload_symbol(label: str = "", pins: tuple = ()) -> Symbol:
    """IEC 60617 Thermal Overload Protection.
    
    Geometry: Pulse shape.
    Trace:
    - Half grid down
    - Half grid left
    - Half grid down
    - Half grid right
    - Half grid down
    """
    # Total pulse height = 3 * half_grid = 7.5mm
    # Width = half_grid = 2.5mm (to the left)
    
    # Grid subdiv
    hg = GRID_SUBDIVISION # 2.5
    
    # Vertically centered.
    # Total H = 3 * hg = 7.5
    # Start Y = -3.75 (-1.5 * hg)
    # End Y  = +3.75 (+1.5 * hg)
    
    y_start = -1.5 * hg
    
    # Points
    p0 = Point(0, y_start)
    p1 = Point(0, y_start + hg)          # Down
    p2 = Point(-hg, y_start + hg)        # Left
    p3 = Point(-hg, y_start + 2*hg)      # Down
    p4 = Point(0, y_start + 2*hg)        # Right
    p5 = Point(0, y_start + 3*hg)        # Down (End of pulse)
    
    # Standard spacing is 10mm (-5 to 5).
    # Connect from ports to pulse.
    top_port_y = -GRID_SIZE
    bot_port_y = GRID_SIZE
    
    style = standard_style()
    
    # Lead-in (Top)
    l_in = Line(Point(0, top_port_y), p0, style)
    
    # Pulse path
    # We can use a Path or multiple Lines. Lines for simplicity.
    s1 = Line(p0, p1, style)
    s2 = Line(p1, p2, style)
    s3 = Line(p2, p3, style)
    s4 = Line(p3, p4, style)
    s5 = Line(p4, p5, style)
    
    # Lead-out (Avg)
    l_out = Line(p5, Point(0, bot_port_y), style)
    
    elements = [l_in, s1, s2, s3, s4, s5, l_out]
    
    if label:
        elements.append(standard_text(label, Point(0, 0)))
        
    ports = {
        "1": Port("1", Point(0, top_port_y), Vector(0, -1)),
        "2": Port("2", Point(0, bot_port_y), Vector(0, 1))
    }
    
    if pins:
        elements.extend(create_pin_labels(ports, pins))
        
    return Symbol(elements, ports, label=label)

def three_pole_thermal_overload_symbol(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """IEC 60617 Three Pole Thermal Overload Protection.
    
    Composed of 3 single thermal overload symbols.
    """
    return three_pole_factory(thermal_overload_symbol, label, pins)

def fuse_symbol(label: str = "", pins: tuple = ()) -> Symbol:
    """IEC 60617 Fuse."""
    # Box 5mm x 12.5mm ?
    w = 2 * GRID_SIZE
    h = 5 * GRID_SIZE
    
    body = box(Point(0, 0), w, h)
    style = standard_style()
    
    # Internal continuity line
    line = Line(Point(0, -h/2), Point(0, h/2), style)
    
    elements = [body, line]
    if label:
        elements.append(standard_text(label, Point(0, 0)))
        
    ports = {
        "1": Port("1", Point(0, -h/2), Vector(0, -1)),
        "2": Port("2", Point(0, h/2), Vector(0, 1))
    }
    
    if pins:
        elements.extend(create_pin_labels(ports, pins))

    return Symbol(elements, ports, label)
