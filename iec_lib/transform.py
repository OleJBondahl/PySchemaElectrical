from typing import TypeVar, Union, List
import math
from .core import Point, Vector, Port, Symbol, Element
from .primitives import Line, Circle, Text, Path, Group, Polygon
from dataclasses import replace
from .constants import TEXT_OFFSET_X

T = TypeVar('T', bound=Union[Element, Point, Port, Vector])

def translate(obj: T, dx: float, dy: float) -> T:
    """
    Pure function to translate an object by (dx, dy).
    
    Args:
        obj (T): The object to translate (Element, Point, Port, Symbol).
        dx (float): Shift in x.
        dy (float): Shift in y.
        
    Returns:
        T: A new instance of the object translated.
    """
    if isinstance(obj, Point):
        return Point(obj.x + dx, obj.y + dy)
    
    elif isinstance(obj, Port):
        return replace(obj, position=translate(obj.position, dx, dy))
    
    elif isinstance(obj, Line):
        return replace(obj, 
                       start=translate(obj.start, dx, dy), 
                       end=translate(obj.end, dx, dy))
    
    elif isinstance(obj, Circle):
        return replace(obj, center=translate(obj.center, dx, dy))
        
    elif isinstance(obj, Text):
        return replace(obj, position=translate(obj.position, dx, dy))
        
    elif isinstance(obj, Group):
        return replace(obj, elements=[translate(e, dx, dy) for e in obj.elements])

    elif isinstance(obj, Polygon):
        return replace(obj, points=[translate(p, dx, dy) for p in obj.points])

    elif isinstance(obj, Symbol):
        # Symbol is a subclass of Element, so it can be handled here if T covers Element
        # logic for Symbol
        new_elements = [translate(e, dx, dy) for e in obj.elements]
        new_ports = {k: translate(p, dx, dy) for k, p in obj.ports.items()}
        return replace(obj, elements=new_elements, ports=new_ports)
        
    # TODO: Implement Path translation (requires parsing d string or simple regex shift if assuming absolute coords)
    return obj

def rotate_point(p: Point, angle_deg: float, center: Point = Point(0, 0)) -> Point:
    """
    Rotate a point around a center.
    
    Args:
        p (Point): The point to rotate.
        angle_deg (float): Angle in degrees (clockwise generally in SVG coord system if Y is down).
        center (Point): Center of rotation.
        
    Returns:
        Point: The new rotated point.
    """
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Translate to origin
    tx = p.x - center.x
    ty = p.y - center.y
    
    # Rotate
    rx = tx * cos_a - ty * sin_a
    ry = tx * sin_a + ty * cos_a
    
    # Translate back
    return Point(rx + center.x, ry + center.y)

def rotate_vector(v: Vector, angle_deg: float) -> Vector:
    """
    Rotate a vector.
    
    Args:
        v (Vector): The vector to rotate.
        angle_deg (float): Angle in degrees.
        
    Returns:
        Vector: The new rotated vector.
    """
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return Vector(v.dx * cos_a - v.dy * sin_a, v.dx * sin_a + v.dy * cos_a)

def rotate(obj: T, angle: float, center: Point = Point(0, 0)) -> T:
    """
    Pure function to rotate an object around a center point.
    
    Args:
        obj (T): Object to rotate.
        angle (float): Angle in degrees.
        center (Point): Center of rotation.
        
    Returns:
        T: The rotated object.
    """
    if isinstance(obj, Point):
        return rotate_point(obj, angle, center)
    
    elif isinstance(obj, Port):
        return replace(obj, 
                       position=rotate_point(obj.position, angle, center),
                       direction=rotate_vector(obj.direction, angle))
                       
    elif isinstance(obj, Line):
        return replace(obj,
                       start=rotate_point(obj.start, angle, center),
                       end=rotate_point(obj.end, angle, center))
                       
    elif isinstance(obj, Group):
        return replace(obj, elements=[rotate(e, angle, center) for e in obj.elements])

    elif isinstance(obj, Polygon):
        return replace(obj, points=[rotate_point(p, angle, center) for p in obj.points])

    elif isinstance(obj, Symbol):
        new_elements = []
        for e in obj.elements:
            rotated_e = rotate(e, angle, center)
            
            # Special case: If this is the main label, force it to stick to the Left
            # We identify the main label if it matches the Symbol's label content
            if isinstance(rotated_e, Text) and obj.label and rotated_e.content == obj.label:
                # Force position to Left of center (-TEXT_OFFSET_X usually, but TEXT_OFFSET_X is -5.0)
                # If TEXT_OFFSET_X is -5.0, that means "5mm left".
                # We want it relative to the rotation center (which is usually (0,0) for the symbol).
                # Wait, 'center' passed here is for the rotation. 
                # If rotating a symbol in place, center=(0,0) usually.
                # If rotating a placed symbol, center needs care.
                # Generally we rotate symbols around their own origin (0,0) before translating.
                
                # So relative to the symbol's own origin (which is being rotated around 'center'?)
                # If we assume 'rotate' is called on a symbol at (0,0), then 'center' is (0,0).
                # We reconstruct the 'standard_text' position.
                
                # However, if 'center' is NOT (0,0), we must account for it?
                # Usually we rotate symbol around (0,0) then translate. 
                # Lets assume 'center' is the reference point for the symbol.
                
                # Position = center.x + TEXT_OFFSET_X
                forced_pos = Point(center.x + TEXT_OFFSET_X, center.y)
                
                rotated_e = replace(rotated_e, 
                                    position=forced_pos, 
                                    anchor="end") # Always end-aligned (growing left)

            new_elements.append(rotated_e)
            
        new_ports = {k: rotate(p, angle, center) for k, p in obj.ports.items()}
        return replace(obj, elements=new_elements, ports=new_ports)
        
    # Circle rotation around center implies translating the center
    elif isinstance(obj, Circle):
        return replace(obj, center=rotate_point(obj.center, angle, center))
        
    elif isinstance(obj, Text):
         new_pos = rotate_point(obj.position, angle, center)
         new_anchor = obj.anchor
         
         # Handle 180 degree rotation for text readability/positioning
         # If we keep text upright (don't change rotation), we must flip anchor
         # to prevent text from growing into the symbol.
         norm_angle = angle % 360
         if abs(norm_angle - 180) < 0.1:
             if obj.anchor == "start":
                 new_anchor = "end"
             elif obj.anchor == "end":
                 new_anchor = "start"
                 
         return replace(obj, position=new_pos, anchor=new_anchor)

    return obj

