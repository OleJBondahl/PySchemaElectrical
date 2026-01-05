"""
High-level functions for creating wire labels on connections.

This module provides functional abstractions for adding wire specification labels
(color, size, etc.) to connection lines in electrical schematics.
"""

from typing import List, Tuple, Optional
from .core import Point, Element
from .primitives import Line, Text
from .constants import TEXT_SIZE_PIN, TEXT_FONT_FAMILY_AUX


def calculate_wire_label_position(
    start: Point,
    end: Point,
    offset_x: float = -2.0
) -> Point:
    """
    Calculate the position for a wire label along a vertical wire.
    
    Places the label at the midpoint of the wire, offset to the left side.
    
    Args:
        start (Point): Starting point of the wire.
        end (Point): Ending point of the wire.
        offset_x (float): Horizontal offset from wire (negative = left side).
        
    Returns:
        Point: The calculated label position.
    """
    mid_x = (start.x + end.x) / 2.0
    mid_y = (start.y + end.y) / 2.0
    
    return Point(mid_x + offset_x, mid_y)


def create_wire_label_text(
    text_content: str,
    position: Point,
    font_size: float = TEXT_SIZE_PIN
) -> Text:
    """
    Create a text element for a wire label.
    
    Args:
        text_content (str): The label text (e.g., "RD 2.5mm²").
        position (Point): The position for the text.
        font_size (float): Font size for the text.
        
    Returns:
        Text: The configured text element.
    """
    from .core import Style
    
    return Text(
        content=text_content,
        position=position,
        anchor="end",
        font_size=font_size,
        style=Style(stroke="none", fill="black", font_family=TEXT_FONT_FAMILY_AUX)
    )


def format_wire_specification(
    color: str = "",
    size: str = ""
) -> str:
    """
    Format wire color and size into a standardized label string.
    
    Args:
        color (str): Wire color code (e.g., "RD", "BK").
        size (str): Wire size specification (e.g., "2.5mm²", "0.5mm²").
        
    Returns:
        str: Formatted wire specification string.
        
    Examples:
        >>> format_wire_specification("RD", "2.5mm²")
        'RD 2.5mm²'
        >>> format_wire_specification("BK", "")
        'BK'
        >>> format_wire_specification("", "2.5mm²")
        '2.5mm²'
    """
    parts = [p for p in [color, size] if p]
    return " ".join(parts)


def create_labeled_wire(
    start: Point,
    end: Point,
    wire_color: str = "",
    wire_size: str = "",
    label_offset_x: float = -2.0
) -> List[Element]:
    """
    Create a wire connection with an optional label.
    
    High-level function that creates both the wire line and its label text
    if wire specifications are provided.
    
    Args:
        start (Point): Starting point of the wire.
        end (Point): Ending point of the wire.
        wire_color (str): Wire color code (e.g., "RD", "BK").
        wire_size (str): Wire size specification (e.g., "2.5mm²").
        label_offset_x (float): Horizontal offset for label (negative = left).
        
    Returns:
        List[Element]: List containing the wire line and optionally the label text.
    """
    from .parts import standard_style
    
    elements = []
    
    # Create the wire line
    wire_line = Line(start, end, style=standard_style())
    elements.append(wire_line)
    
    # Add label if specifications are provided
    label_text = format_wire_specification(wire_color, wire_size)
    if label_text:
        label_pos = calculate_wire_label_position(start, end, label_offset_x)
        label = create_wire_label_text(label_text, label_pos)
        elements.append(label)
    
    return elements


def create_labeled_connections(
    connection_specs: List[Tuple[Point, Point, str, str]]
) -> List[Element]:
    """
    Create multiple labeled wire connections from specifications.
    
    Functional approach to batch-create wire connections with labels.
    
    Args:
        connection_specs: List of tuples, each containing:
            - start (Point): Wire start point
            - end (Point): Wire end point
            - color (str): Wire color code
            - size (str): Wire size specification
            
    Returns:
        List[Element]: All wire lines and labels as flat list.
        
    Example:
        >>> specs = [
        ...     (Point(0, 0), Point(0, 10), "RD", "2.5mm²"),
        ...     (Point(10, 0), Point(10, 10), "BK", "0.5mm²")
        ... ]
        >>> elements = create_labeled_connections(specs)
    """
    from functools import reduce
    
    all_elements = [
        create_labeled_wire(start, end, color, size)
        for start, end, color, size in connection_specs
    ]
    
    # Flatten the list of lists into a single list
    return reduce(lambda acc, x: acc + x, all_elements, [])
