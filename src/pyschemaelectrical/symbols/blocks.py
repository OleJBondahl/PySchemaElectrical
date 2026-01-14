from typing import Tuple, List, Optional
from pyschemaelectrical.model.core import Point, Vector, Port, Symbol, Style, Element
from pyschemaelectrical.model.primitives import Text, Line
from pyschemaelectrical.model.parts import box, standard_text, standard_style
from pyschemaelectrical.model.constants import (
    GRID_SIZE, 
    DEFAULT_POLE_SPACING, 
    COLOR_BLACK, 
    TEXT_SIZE_PIN, 
    TEXT_FONT_FAMILY_AUX
)

def terminal_box_symbol(label: str = "", num_pins: int = 1, start_pin_number: int = 1, pin_spacing: float = DEFAULT_POLE_SPACING) -> Symbol:
    """
    Create a Rectangular Terminal Box Symbol.
    
    Dimensions:
        Height: Equalt to pin_spacing (default 10mm / 2 grids).
        Width: Flexible (num_pins - 1) * spacing + 1 Grid (padding 0.5 grid each side).
        Pins: Pointing upwards.
        Pin Numbers: LEFT of the pins.
    
    Args:
        label (str): Component tag.
        num_pins (int): Number of pins/terminals.
        start_pin_number (int): Starting number for pin labels.
        pin_spacing (float): distance between pins.
        
    Returns:
        Symbol: The symbol.
    """
    
    if num_pins < 1:
        num_pins = 1
        
    style = standard_style()
    
    # "box is to short in the height direction, increase to the same as pin spacing"
    # Pin Spacing default is 10.0 (2 Grid).
    box_height = pin_spacing 
    
    # Standard Pin length and alignment
    # Pin points UP from Top of box.
    # Origin (0,0) at Top Edge of Box where first pin starts?
    # Or Origin at First Port?
    # Sticking with: Origin (0,0) is at Box Top Edge, First Pin X.
    # Pin extends Up from 0 to -pin_length.
    
    pin_length = GRID_SIZE / 2 # 2.5mm
    padding = GRID_SIZE / 2 # 2.5mm
    
    span = (num_pins - 1) * pin_spacing
    box_width = span + 2 * padding
    
    # Center of box
    # X: span / 2
    # Y: box_height / 2 (Below 0)
    center_x = span / 2
    center_y = box_height / 2
    
    rect = box(Point(center_x, center_y), box_width, box_height, filled=False)
    
    elements: List[Element] = [rect]
    ports = {}
    
    for i in range(num_pins):
        p_num = start_pin_number + i
        p_str = str(p_num)
        
        px = i * pin_spacing
        
        # Pin Line
        # From box top (0) upwards to (-pin_length)
        l = Line(Point(px, 0), Point(px, -pin_length), style)
        elements.append(l)
        
        # Port at tip
        ports[p_str] = Port(p_str, Point(px, -pin_length), Vector(0, -1))
        
        # Pin Number
        # "always put the pin numbers of the left of the pins"
        # Position: px - offset
        
        text_x = px - 1.0 # 1mm to the LEFT of pin
        text_y = -pin_length / 2 # Middle of the pin line
        
        text = Text(
            content=p_str,
            position=Point(text_x, text_y),
            anchor="end", # Right aligned (End of text touches x)
            dominant_baseline="middle",
            font_size=TEXT_SIZE_PIN,
            style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
        )
        elements.append(text)

    if label:
        elements.append(standard_text(label, Point(0, 0)))

    return Symbol(elements, ports, label=label)


def psu_symbol(label: str = "U1", **kwargs) -> Symbol:
    """
    Create a Power Supply Unit (PSU) symbol.
    
    A specialized dynamic block with:
    - Pins: Top (L, N, PE), Bottom (24V, GND)
    - Visuals: Diagonal line, 'AC' in top-left, 'DC' in bottom-right.
    
    Args:
        label (str): Component tag.
        
    Returns:
        Symbol: The PSU symbol.
    """
    # Define fixed configuration for PSU
    top_pins = ("L", "N", "PE")
    bottom_pins = ("24V", "GND")
    pin_spacing = DEFAULT_POLE_SPACING
    
    # Create the base block
    sym = dynamic_block_symbol(
        label=label,
        top_pins=top_pins,
        bottom_pins=bottom_pins,
        pin_spacing=pin_spacing
    )
    
    # Re-calculate dimensions to place internal elements
    # (Logic matches dynamic_block)
    box_height = 4 * GRID_SIZE  # 20mm
    padding = GRID_SIZE / 2
    
    num_top = len(top_pins)
    num_bottom = len(bottom_pins)
    max_pins = max(num_top, num_bottom)
    
    span = (max_pins - 1) * pin_spacing
    box_width = span + 2 * padding
    
    # Center of box
    center_x = span / 2
    center_y = box_height / 2
    
    # Box edges relative to origin (0,0)
    # Left edge: center_x - box_width / 2
    # Right edge: center_x + box_width / 2
    # Top edge: 0
    # Bottom edge: box_height
    
    left = center_x - box_width / 2
    right = center_x + box_width / 2
    top = 0
    bottom = box_height
    
    style = standard_style()
    
    # Diagonal line (Bottom-Left to Top-Right to separate AC top-left / DC bottom-right)
    # Alternatively: Top-Left AC, Bottom-Right DC often separated by diagonal /
    # Let's draw a line from Bottom-Left to Top-Right
    p1 = Point(left, bottom)
    p2 = Point(right, top)
    sym.elements.append(Line(p1, p2, style))
    
    # Text "AC" in top-left
    # Position: Slightly indented from top-left corner
    ac_pos = Point(left + 2.0, top + 4.0)
    ac_text = Text(
        content="AC",
        position=ac_pos,
        anchor="start",
        dominant_baseline="hanging", # Text hangs below the point
        font_size=3.5,
        style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
    )
    sym.elements.append(ac_text)
    
    # Text "DC" in bottom-right
    # Position: Slightly indented from bottom-right corner
    dc_pos = Point(right - 2.0, bottom - 4.0)
    dc_text = Text(
        content="DC",
        position=dc_pos,
        anchor="end",
        dominant_baseline="baseline", # Text sits on the point
        font_size=3.5,
        style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
    )
    sym.elements.append(dc_text)
    
    return sym


def dynamic_block_symbol(
    label: str = "",
    top_pins: Optional[Tuple[str, ...]] = None,
    bottom_pins: Optional[Tuple[str, ...]] = None,
    pin_spacing: float = DEFAULT_POLE_SPACING
) -> Symbol:
    """
    Create a dynamic block symbol with configurable pins on top and bottom.
    
    The block automatically adjusts its width based on the maximum number of pins
    (top or bottom). The box is half a grid wider than the last pin on either side
    and has a fixed height of 4 grids.
    
    Dimensions:
        Height: 4 grids (20mm).
        Width: (max(len(top_pins), len(bottom_pins)) - 1) * pin_spacing + 1 Grid (0.5 grid padding each side).
        Top Pins: Pointing upwards with pin labels on the left.
        Bottom Pins: Pointing downwards with pin labels on the left.
    
    Args:
        label (str): Component tag.
        top_pins (Tuple[str, ...]): Tuple of pin labels for top pins (e.g., ("L", "N", "PE")).
        bottom_pins (Tuple[str, ...]): Tuple of pin labels for bottom pins (e.g., ("24V", "GND")).
        pin_spacing (float): Distance between pins.
        
    Returns:
        Symbol: The dynamic block symbol.
    """
    # Default to empty tuples if not provided
    if top_pins is None:
        top_pins = ()
    if bottom_pins is None:
        bottom_pins = ()
    style = standard_style()
    
    # Fixed box height of 4 grids
    box_height = 4 * GRID_SIZE  # 20mm
    
    # Pin dimensions
    pin_length = GRID_SIZE / 2  # 2.5mm
    padding = GRID_SIZE / 2  # 2.5mm (half a grid)
    
    
    # Calculate box width based on maximum number of pins
    num_top = len(top_pins)
    num_bottom = len(bottom_pins)
    max_pins = max(num_top, num_bottom)
    if max_pins < 1:
        max_pins = 1
    
    span = (max_pins - 1) * pin_spacing
    box_width = span + 2 * padding
    
    # Center of box
    center_x = span / 2
    center_y = box_height / 2
    
    # Create the rectangle
    rect = box(Point(center_x, center_y), box_width, box_height, filled=False)
    
    elements: List[Element] = [rect]
    ports = {}
    
    # Create top pins (pointing upward)
    for i, pin_label in enumerate(top_pins):
        px = i * pin_spacing
        
        # Pin line from box top (0) upwards to (-pin_length)
        line = Line(Point(px, 0), Point(px, -pin_length), style)
        elements.append(line)
        
        # Port at tip - use the label as the port name
        ports[pin_label] = Port(pin_label, Point(px, -pin_length), Vector(0, -1))
        
        # Pin label to the left of the pin
        text_x = px - 1.0  # 1mm to the LEFT of pin
        text_y = -pin_length / 2  # Middle of the pin line
        
        text = Text(
            content=pin_label,
            position=Point(text_x, text_y),
            anchor="end",
            dominant_baseline="middle",
            font_size=TEXT_SIZE_PIN,
            style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
        )
        elements.append(text)
    
    # Create bottom pins (pointing downward)
    for i, pin_label in enumerate(bottom_pins):
        px = i * pin_spacing
        
        # Pin line from box bottom (box_height) downwards to (box_height + pin_length)
        line = Line(Point(px, box_height), Point(px, box_height + pin_length), style)
        elements.append(line)
        
        # Port at tip - use the label as the port name
        ports[pin_label] = Port(pin_label, Point(px, box_height + pin_length), Vector(0, 1))
        
        # Pin label to the left of the pin, positioned below to avoid collision with box
        text_x = px - 1.0  # 1mm to the LEFT of pin
        text_y = box_height + pin_length  # At the end of the pin line (below box)
        
        text = Text(
            content=pin_label,
            position=Point(text_x, text_y),
            anchor="end",
            dominant_baseline="middle",
            font_size=TEXT_SIZE_PIN,
            style=Style(stroke="none", fill=COLOR_BLACK, font_family=TEXT_FONT_FAMILY_AUX)
        )
        elements.append(text)
    
    # Add label if provided
    # Add label if provided
    if label:
        elements.append(standard_text(label, Point(0, center_y)))

    return Symbol(elements, ports, label=label)
