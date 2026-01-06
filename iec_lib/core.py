from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict, Union, Any

@dataclass(frozen=True)
class Vector:
    """
    An immutable vector representing direction and magnitude in 2D space.
    
    Attributes:
        dx (float): The x-component of the vector.
        dy (float): The y-component of the vector.
    """
    dx: float
    dy: float

    def __add__(self, other: 'Vector') -> 'Vector':
        """Add two vectors."""
        if not isinstance(other, Vector):
             return NotImplemented
        return Vector(self.dx + other.dx, self.dy + other.dy)

    def __mul__(self, scalar: float) -> 'Vector':
        """Scale the vector by a scalar."""
        return Vector(self.dx * scalar, self.dy * scalar)

@dataclass(frozen=True)
class Point:
    """
    An immutable point in 2D space.
    
    Attributes:
        x (float): The x-coordinate.
        y (float): The y-coordinate.
    """
    x: float
    y: float

    def __add__(self, other: Union['Point', 'Vector']) -> 'Point':
        """
        Add a Vector to a Point to get a new Point.
        
        Args:
            other (Vector): The vector to add.
            
        Returns:
            Point: The new point.
            
        Raises:
            TypeError: If other is not a Vector.
        """
        if isinstance(other, Vector):
            return Point(self.x + other.dx, self.y + other.dy)
        raise TypeError(f"Can only add Vector to Point, got {type(other)}")

    def __sub__(self, other: 'Point') -> 'Vector':
        """
        Subtract a Point from another Point to get a Vector.
        
        Args:
            other (Point): The point to subtract.
            
        Returns:
            Vector: The vector from other to self.
            
        Raises:
            TypeError: If other is not a Point.
        """
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y)
        raise TypeError(f"Can only subtract Point from Point, got {type(other)}")

@dataclass(frozen=True)
class Style:
    """
    Style attributes for SVG elements.
    
    Attributes:
        stroke (str): Stroke color (CSS color string). Default "black".
        stroke_width (float): Stroke width in user units. Default 1.0.
        fill (str): Fill color (CSS color string). Default "none".
        stroke_dasharray (Optional[str]): Dash array pattern. Default None.
        opacity (float): Opacity value (0.0 to 1.0). Default 1.0.
        font_family (Optional[str]): Font family for text. Default None.
    """
    stroke: str = "black"
    stroke_width: float = 1.0
    fill: str = "none"
    stroke_dasharray: Optional[str] = None
    opacity: float = 1.0
    font_family: Optional[str] = None

@dataclass(frozen=True)
class Element:
    """Base class for all geometric primitives and symbols."""
    pass

@dataclass(frozen=True)
class Port:
    """
    A connection point on a symbol.
    
    Attributes:
        id (str): Unique identifier within the symbol (e.g., "1", "A1", "13").
        position (Point): The absolute position of the port.
        direction (Vector): The direction a wire should leave this port (unit vector ideally).
    """
    id: str
    position: Point
    direction: Vector

@dataclass(frozen=True)
class Symbol(Element):
    """
    A reusable component composed of primitives and ports.
    
    Attributes:
        elements (List[Element]): Geometric primitives making up the symbol.
        ports (Dict[str, Port]): Connection points, keyed by port ID.
        label (Optional[str]): Component label/tag (e.g., "-K1").
    """
    elements: List[Element]
    ports: Dict[str, Port]
    label: Optional[str] = None

