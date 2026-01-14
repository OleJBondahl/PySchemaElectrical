from typing import Tuple, Optional
import math
from pyschemaelectrical.model.core import Symbol, Point, Style, Element, Vector
from pyschemaelectrical.model.primitives import Line, Polygon
from pyschemaelectrical.model.constants import GRID_SIZE
from pyschemaelectrical.model.parts import standard_style
from pyschemaelectrical.utils.transform import rotate

def emergency_stop_button_symbol(label: str = "", rotation: float = 0.0) -> Symbol:
    """
    Emergency Stop Head (Mushroom).
    
    Geometry (0 deg = Pointing Right):
    - Flat base on Y-axis (x=0).
    - Semi-circle bulging to + x.
    - Diameter: GRID_SIZE / 2 (Radius = GRID_SIZE / 4).
    
    Implemented as a Polygon to ensure compatibility with generic translation/rotation.
    """
    style = standard_style()
    
    # Dimensions
    r = GRID_SIZE / 4  # Radius (2.5mm / 2 = 1.25mm)
    
    # Generate points for semi-circle
    # Angles from -90 (Top) to 90 (Bottom) drawing the arc on the Right (+x)
    points = []
    
    # 1. Top of base
    points.append(Point(0, -r))
    
    # 2. Arc segments
    steps = 10
    for i in range(steps + 1):
        # angle goes from -pi/2 to pi/2
        angle = -math.pi/2 + (math.pi * i / steps)
        px = r * math.cos(angle)
        py = r * math.sin(angle)
        points.append(Point(px, py))
        
    # 3. Bottom of base is effectively included in loop (at pi/2)
    # Polygon auto-closes to start (0, -r)
    
    head = Polygon(points=points, style=style)
    
    sym = Symbol([head], {}, label=label)
    
    # Apply rotation
    if rotation != 0:
        sym = rotate(sym, rotation)
        
    return sym
