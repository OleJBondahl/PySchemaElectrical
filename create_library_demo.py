import importlib
import pkgutil
import inspect
import sys
import os
import math

# Add current directory to path
sys.path.append(os.getcwd())

from iec_lib import library
from iec_lib.core import Symbol, Point, Style
from iec_lib.transform import translate
from iec_lib.renderer import render_to_svg
from iec_lib.primitives import Line, Circle, Text, Element, Group, Path

def get_bbox(element: Element):
    """Returns (min_x, min_y, max_x, max_y)"""
    if isinstance(element, Line):
        return (
            min(element.start.x, element.end.x),
            min(element.start.y, element.end.y),
            max(element.start.x, element.end.x),
            max(element.start.y, element.end.y)
        )
    elif isinstance(element, Circle):
        return (
            element.center.x - element.radius,
            element.center.y - element.radius,
            element.center.x + element.radius,
            element.center.y + element.radius
        )
    elif isinstance(element, Text):
        # Approximation
        return (element.position.x, element.position.y, element.position.x + 5, element.position.y + 5)
    elif isinstance(element, (Group, Symbol)):
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
        if not element.elements:
            return (0, 0, 0, 0)
        for e in element.elements:
            b = get_bbox(e)
            min_x = min(min_x, b[0])
            min_y = min(min_y, b[1])
            max_x = max(max_x, b[2])
            max_y = max(max_y, b[3])
        return (min_x, min_y, max_x, max_y)
    
    return (0, 0, 0, 0)

def discover_symbols():
    symbols = []
    # walk packages
    for loader, module_name, is_pkg in pkgutil.iter_modules(library.__path__):
        full_module_name = f'iec_lib.library.{module_name}'
        module = importlib.import_module(full_module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                if name.startswith('_'): continue
                
                try:
                    sig = inspect.signature(obj)
                    if sig.return_annotation == Symbol or sig.return_annotation == 'Symbol':
                        # Valid symbol generator
                        if 'label' in sig.parameters:
                            sym = obj(label=name)
                        else:
                            sym = obj()
                        
                        # sym.label = name # Ensure label is set for identification -- removed as immutable
                        symbols.append((name, sym))
                except Exception as e:
                    print(f"Skipping {name}: {e}")
    return symbols

def main():
    symbols = discover_symbols()
    print(f"Found {len(symbols)} symbols.")
    
    current_x = 20.0
    current_y = 30.0
    row_height = 0.0
    page_width = 200.0
    spacing = 10.0
    
    placed_elements = []
    
    # Title
    placed_elements.append(Text("IEC Library Symbol Demo", Point(20, 10), anchor="start", font_size=5))
    
    for name, sym in symbols:
        bbox = get_bbox(sym)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        # Ensure minimum size for spacing if bbox is tiny
        if w < 1: w = 5
        if h < 1: h = 5
        
        # Check if we need to wrap
        if current_x + w > page_width:
            current_x = 20.0
            current_y += row_height + spacing + 10 # Extra for labels
            row_height = 0.0
            
        # Place symbol
        # Calculate offset to put the top-left of symbol at current_x, current_y
        offset_x = current_x - bbox[0]
        offset_y = current_y - bbox[1]
        
        placed_sym = translate(sym, offset_x, offset_y)
        placed_elements.append(placed_sym)
        
        # Add label text below the symbol
        # Symbol center x roughly
        center_x = current_x + w/2
        label_y = current_y + h + 5
        
        label_text = Text(name, Point(center_x, label_y), anchor="middle", font_size=3)
        placed_elements.append(label_text)
        
        # Update cursor
        current_x += w + spacing
        row_height = max(row_height, h)
        
    render_to_svg(placed_elements, "library_demo.svg")
    print("Created library_demo.svg")

if __name__ == "__main__":
    main()
