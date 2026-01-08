import xml.etree.ElementTree as ET
from typing import List, Union
from .core import Symbol, Point, Style
from .primitives import Element, Line, Circle, Text, Path, Group, Polygon
from .constants import COLOR_WHITE, DEFAULT_DOC_WIDTH, DEFAULT_DOC_HEIGHT

def _style_to_str(style: Style) -> str:
    """
    Evaluate style object to SVG style string.
    
    Args:
        style (Style): The style object to convert.
        
    Returns:
        str: The CSS style string.
    """
    items = []
    if style.stroke: items.append(f"stroke:{style.stroke}")
    if style.stroke_width: items.append(f"stroke-width:{style.stroke_width}")
    if style.fill: items.append(f"fill:{style.fill}")
    if style.stroke_dasharray: items.append(f"stroke-dasharray:{style.stroke_dasharray}")
    if style.font_family: items.append(f"font-family:{style.font_family}")
    return ";".join(items)

def _render_element(elem: Element, parent: ET.Element):
    """
    Recursively render elements to the XML tree.
    
    Args:
        elem (Element): The element to render.
        parent (ET.Element): The parent XML element to append to.
    """
    if isinstance(elem, Line):
        e = ET.SubElement(parent, "line")
        e.set("x1", str(elem.start.x))
        e.set("y1", str(elem.start.y))
        e.set("x2", str(elem.end.x))
        e.set("y2", str(elem.end.y))
        e.set("style", _style_to_str(elem.style))
    
    elif isinstance(elem, Circle):
        e = ET.SubElement(parent, "circle")
        e.set("cx", str(elem.center.x))
        e.set("cy", str(elem.center.y))
        e.set("r", str(elem.radius))
        e.set("style", _style_to_str(elem.style))
        
    elif isinstance(elem, Text):
        e = ET.SubElement(parent, "text")
        e.set("x", str(elem.position.x))
        e.set("y", str(elem.position.y))
        e.set("text-anchor", elem.anchor)
        e.set("dominant-baseline", elem.dominant_baseline)
        e.set("font-size", str(elem.font_size))
        if elem.rotation != 0:
            e.set("transform", f"rotate({elem.rotation}, {elem.position.x}, {elem.position.y})")
        e.text = elem.content
        e.set("style", _style_to_str(elem.style)) # Fill usually needed for text
        
    elif isinstance(elem, Path):
        e = ET.SubElement(parent, "path")
        e.set("d", elem.d)
        e.set("style", _style_to_str(elem.style))

    elif isinstance(elem, Group):
        g = ET.SubElement(parent, "g")
        if elem.style:
            g.set("style", _style_to_str(elem.style))
        for child in elem.elements:
            _render_element(child, g)
            
    elif isinstance(elem, Polygon):
        e = ET.SubElement(parent, "polygon")
        points_str = " ".join([f"{p.x},{p.y}" for p in elem.points])
        e.set("points", points_str)
        e.set("style", _style_to_str(elem.style))
            
    elif isinstance(elem, Symbol):
        # Symbol is effectively a group
        g = ET.SubElement(parent, "g")
        g.set("class", "symbol")
        for child in elem.elements:
            _render_element(child, g)
        # We don't render ports visibly usually, maybe for debug?

def to_xml_element(elements: List[Element], width: Union[int, str] = DEFAULT_DOC_WIDTH, height: Union[int, str] = DEFAULT_DOC_HEIGHT) -> ET.Element:
    """
    Convert a list of Elements into an SVG header/root ElementTree Element.
    
    Args:
        elements (List[Element]): List of elements to render.
        width (Union[int, str]): document width.
        height (Union[int, str]): document height.
        
    Returns:
        ET.Element: The root SVG element.
    """
    root = ET.Element("svg")
    root.set("xmlns", "http://www.w3.org/2000/svg")
    root.set("width", str(width))
    root.set("height", str(height))
    
    # Simple viewBox logic
    def _parse_dim(val, default):
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            clean = val.replace("mm", "").strip()
            try:
                return float(clean)
            except ValueError:
                pass
        return default

    vb_w = _parse_dim(width, 210)
    vb_h = _parse_dim(height, 297)
    
    root.set("viewBox", f"0 0 {vb_w} {vb_h}")
    
    # Background for visibility
    bg = ET.SubElement(root, "rect")
    bg.set("width", "100%")
    bg.set("height", "100%")
    bg.set("fill", COLOR_WHITE)
    
    # Main group
    main_g = ET.SubElement(root, "g")
    
    for elem in elements:
        _render_element(elem, main_g)
        
    return root

def save_svg(root: ET.Element, filename: str):
    """
    Save an XML tree to a file.
    
    Args:
        root (ET.Element): The root element.
        filename (str): The destination path.
    """
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def render_to_svg(elements: List[Element], filename: str, width: Union[int, str] = DEFAULT_DOC_WIDTH, height: Union[int, str] = DEFAULT_DOC_HEIGHT):
    """
    High-level function to render elements to an SVG file.
    
    Args:
        elements (List[Element]): Elements to render.
        filename (str): Output filename.
        width (Union[int, str]): Document width.
        height (Union[int, str]): Document height.
    """
    root = to_xml_element(elements, width, height)
    save_svg(root, filename)
