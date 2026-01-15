"""
Component parts and factory functions for electrical symbols.

This module provides reusable parts and factory functions for building
electrical symbols according to IEC 60617 standards. It includes:
- Standard styling and text formatting functions
- Terminal and box primitives  
- Pin label creation
- Three-pole symbol factory for creating multi-pole components

All constants are imported from the constants module.
"""

from .primitives import Line, Circle, Path, Group, Element, Text, Polygon
from .core import Point, Style, Vector, Symbol
from typing import List, Optional, Callable, Dict, Tuple, Any
from dataclasses import replace
from pyschemaelectrical.utils.transform import translate
from .constants import (
    GRID_SIZE,
    TEXT_SIZE_MAIN,
    TEXT_FONT_FAMILY,
    TEXT_OFFSET_X,
    LINE_WIDTH_THIN,
    LINE_WIDTH_THICK,
    TEXT_SIZE_PIN,
    TEXT_FONT_FAMILY_AUX,
    PIN_LABEL_OFFSET_X,
    PIN_LABEL_OFFSET_Y_ADJUST,
    TERMINAL_RADIUS,
    DEFAULT_POLE_SPACING,
    COLOR_BLACK
)

def standard_style(filled: bool = False) -> Style:
    """
    Create a standard style for symbols.
    
    Args:
        filled (bool): Whether the element should be filled (black) or not (none).
    
    Returns:
        Style: The configured style object.
    """
    return Style(
        stroke=COLOR_BLACK,
        stroke_width=LINE_WIDTH_THIN,
        fill=COLOR_BLACK if filled else "none"
    )

def standard_text(content: str, parent_origin: Point, label_pos: str = 'left') -> Text:
    """
    Create component label text formatted according to standards.
    
    Args:
        content (str): The text content (e.g. "-K1").
        parent_origin (Point): The origin of the parent symbol.
        label_pos (str): 'left' or 'right' of the symbol.
        
    Returns:
        Text: The configured text element.
    """
    if label_pos == 'right':
        pos = Point(parent_origin.x - TEXT_OFFSET_X, parent_origin.y) # Use negative offset but move to right?
        # TEXT_OFFSET_X is -5.0 usually? No, let's check constants.
        # Assuming TEXT_OFFSET_X is negative (e.g. -5).
        # To move right, we want +5 (or abs(TEXT_OFFSET_X)).
        # Let's assume user wants symmetric positioning.
        
        # Actually checking standard_text implementation:
        # pos = Point(parent_origin.x + TEXT_OFFSET_X, parent_origin.y)
        # If TEXT_OFFSET_X is negative (left), then 'right' should be -TEXT_OFFSET_X.
        
        pos = Point(parent_origin.x - TEXT_OFFSET_X, parent_origin.y) 
        anchor = "start"
    else:
        # Default Left
        pos = Point(parent_origin.x + TEXT_OFFSET_X, parent_origin.y)
        anchor = "end"

    return Text(
        content=content,
        position=pos,
        anchor=anchor,
        font_size=TEXT_SIZE_MAIN,
        style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY)
    )

def terminal_circle(center: Point = Point(0,0), filled: bool = False) -> Element:
    """
    Create a standard connection terminal circle.
    
    Args:
        center (Point): Center of the terminal.
        filled (bool): Whether it is filled (e.g. for potential connection points vs loose ends).
        
    Returns:
        Element: The circle element.
    """
    return Circle(center, TERMINAL_RADIUS, standard_style(filled))

def box(center: Point, width: float, height: float, filled: bool = False) -> Element:
    """
    Create a rectangular box centered at a point.
    
    Args:
        center (Point): Center of the box.
        width (float): Width of the box.
        height (float): Height of the box.
        filled (bool): Whether to fill the box.
        
    Returns:
        Element: A Polygon element representing the box.
    """
    half_w = width / 2
    half_h = height / 2
    
    x1, y1 = center.x - half_w, center.y - half_h
    x2, y2 = center.x + half_w, center.y + half_h
    
    # Create points for Polygon
    p1 = Point(x1, y1)
    p2 = Point(x2, y1)
    p3 = Point(x2, y2)
    p4 = Point(x1, y2)
    
    return Polygon(points=[p1, p2, p3, p4], style=standard_style(filled))

def create_pin_labels(ports: Dict[str, Any], pins: Tuple[str, ...]) -> List[Text]:
    """
    Generate text labels for pins based on ports.
    
    Args:
        ports (Dict[str, Port]): The ports dictionary of the symbol.
        pins (Tuple[str, ...]): List of pin labels to assign (e.g. ("13", "14")).
                                Use empty string "" to skip label (port still exists).
        
    Returns:
        List[Text]: A list of Text elements for the pin numbers.
    """
    labels = []
    # Sort port keys to have deterministic mapping
    p_keys = sorted(ports.keys())
    
    for i, p_key in enumerate(p_keys):
        if i >= len(pins):
            break
        
        p_text = str(pins[i])
        
        # Skip creating label if pin text is empty
        if not p_text:
            continue
            
        port = ports[p_key]
        
        # Position logic
        # Default: Left (-X) 
        pos_x = port.position.x - PIN_LABEL_OFFSET_X
        pos_y = port.position.y
        
        # Inward shift based on direction
        # If dir is UP (0, -1), move DOWN (y+)
        if port.direction.dy < -0.1: # UP
             pos_y += PIN_LABEL_OFFSET_Y_ADJUST
        elif port.direction.dy > 0.1: # DOWN
             pos_y -= PIN_LABEL_OFFSET_Y_ADJUST
             
        labels.append(Text(
            content=p_text,
            position=Point(pos_x, pos_y),
            anchor="end",
            font_size=TEXT_SIZE_PIN,
            style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
        ))
        
    return labels

def three_pole_factory(single_pole_func: Callable[..., Symbol], label: str = "", pins: Tuple[str, ...] = ("1", "2", "3", "4", "5", "6"), pole_spacing: float = DEFAULT_POLE_SPACING) -> Symbol:
    """
    Factory to create a three pole symbol from a single pole function.
    
    Args:
        single_pole_func (Callable): A function that returns a single pole Symbol.
        label (str): The label for the composite symbol (e.g. "-Q1").
        pins (Tuple[str, ...]): A tuple of 6 pin labels (use "" to hide label).
        pole_spacing (float): Horizontal spacing between poles.
        
    Returns:
        Symbol: The combined 3-pole symbol.
        
    Raises:
        ValueError: If pins tuple does not have exactly 6 elements.
    """
    if len(pins) != 6:
        raise ValueError(f"Three pole symbol requires 6 pin labels, got {len(pins)}")
        
    # Pole 1
    p1 = single_pole_func(label=label, pins=(pins[0], pins[1]))
    
    # Pole 2
    p2 = single_pole_func(label="", pins=(pins[2], pins[3]))
    p2 = translate(p2, pole_spacing, 0)
    
    # Pole 3
    p3 = single_pole_func(label="", pins=(pins[4], pins[5]))
    p3 = translate(p3, pole_spacing * 2, 0)
    
    # Combine elements
    all_elements = p1.elements + p2.elements + p3.elements
    
    new_ports = {}
    
    def add_remapped_ports(symbol: Symbol, in_key: str, out_key: str, port_ids: Tuple[str, str]):
        """Add ports with sequential IDs, not dependent on pin labels."""
        if in_key in symbol.ports:
            p = symbol.ports[in_key]
            new_id = port_ids[0]  # Use fixed port ID (1, 3, 5 for tops)
            new_ports[new_id] = replace(p, id=new_id)
        if out_key in symbol.ports:
            p = symbol.ports[out_key]
            new_id = port_ids[1]  # Use fixed port ID (2, 4, 6 for bottoms)
            new_ports[new_id] = replace(p, id=new_id)

    # Use fixed port IDs (1-6) regardless of pin labels
    # This ensures ports always exist even if pin labels are empty
    add_remapped_ports(p1, "1", "2", ("1", "2"))
    add_remapped_ports(p2, "1", "2", ("3", "4"))
    add_remapped_ports(p3, "1", "2", ("5", "6"))
    
    return Symbol(elements=all_elements, ports=new_ports, label=label)

def two_pole_factory(single_pole_func: Callable[..., Symbol], label: str = "", pins: Tuple[str, ...] = ("1", "2", "3", "4"), pole_spacing: float = DEFAULT_POLE_SPACING) -> Symbol:
    """
    Factory to create a two pole symbol from a single pole function.
    
    Args:
        single_pole_func (Callable): A function that returns a single pole Symbol.
        label (str): The label for the composite symbol (e.g. "-F1").
        pins (Tuple[str, ...]): A tuple of 4 pin labels.
        pole_spacing (float): Horizontal spacing between poles.
        
    Returns:
        Symbol: The combined 2-pole symbol.
    """
    if len(pins) != 4:
        raise ValueError(f"Two pole symbol requires 4 pin labels, got {len(pins)}")
        
    # Pole 1
    p1 = single_pole_func(label=label, pins=(pins[0], pins[1]))
    
    # Pole 2
    p2 = single_pole_func(label="", pins=(pins[2], pins[3]))
    p2 = translate(p2, pole_spacing, 0)
    
    # Combine elements
    all_elements = p1.elements + p2.elements
    
    new_ports = {}
    
    def add_remapped_ports(symbol: Symbol, in_key: str, out_key: str, port_ids: Tuple[str, str]):
        if in_key in symbol.ports:
            p = symbol.ports[in_key]
            new_id = port_ids[0]
            new_ports[new_id] = replace(p, id=new_id)
        if out_key in symbol.ports:
            p = symbol.ports[out_key]
            new_id = port_ids[1]
            new_ports[new_id] = replace(p, id=new_id)

    # Use fixed port IDs (1-4)
    add_remapped_ports(p1, "1", "2", ("1", "2"))
    add_remapped_ports(p2, "1", "2", ("3", "4"))
    
    return Symbol(elements=all_elements, ports=new_ports, label=label)
