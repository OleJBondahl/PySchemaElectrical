from dataclasses import dataclass
from typing import List, Optional
from .core import Element, Point, Style

@dataclass(frozen=True)
class Line(Element):
    """
    A straight line segment.
    
    Attributes:
        start (Point): Starting point.
        end (Point): Ending point.
        style (Style): Styling attributes.
    """
    start: Point
    end: Point
    style: Style = Style()

@dataclass(frozen=True)
class Circle(Element):
    """
    A circle.
    
    Attributes:
        center (Point): Center point of the circle.
        radius (float): Radius of the circle.
        style (Style): Styling attributes.
    """
    center: Point
    radius: float
    style: Style = Style()

@dataclass(frozen=True)
class Text(Element):
    """
    Text element.
    
    Attributes:
        content (str): The text string to display.
        position (Point): The position coordinates (anchor point).
        style (Style): Styling attributes.
        anchor (str): Text anchor alignment ('start', 'middle', 'end'). Default 'middle'.
        font_size (float): Font size in user units. Default 12.0.
    """
    content: str
    position: Point
    style: Style = Style()
    anchor: str = "middle"
    font_size: float = 12.0

@dataclass(frozen=True)
class Path(Element):
    """
    A generic SVG path.
    
    Attributes:
        d (str): The SVG path data string.
        style (Style): Styling attributes.
    """
    d: str
    style: Style = Style()

@dataclass(frozen=True)
class Group(Element):
    """
    A logical collection of elements.
    
    Attributes:
        elements (List[Element]): List of child elements.
        style (Optional[Style]): Optional style to apply to the group (inherited).
    """
    elements: List[Element]
    style: Optional[Style] = None

@dataclass(frozen=True)
class Polygon(Element):
    """
    A defined polygon from a list of points.
    
    Attributes:
        points (List[Point]): Vertices of the polygon.
        style (Style): Styling attributes.
    """
    points: List[Point]
    style: Style = Style()
