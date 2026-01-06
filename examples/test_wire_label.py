"""Test wire labeling functionality"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core import Point
from src.wire_labels import create_labeled_wire
from src.renderer import render_to_svg

# Test creating a labeled wire
start = Point(50, 50)
end = Point(50, 100)

elements = create_labeled_wire(start, end, "RD", "2.5mm²")

print(f"Number of elements created: {len(elements)}")
for i, elem in enumerate(elements):
    print(f"Element {i}: {type(elem).__name__}")
    if hasattr(elem, 'content'):
        print(f"  Content: {elem.content}")
        print(f"  Position: {elem.position}")

# Render to test file
render_to_svg(elements, "test_wire_label.svg", width="100mm", height="150mm")
print(f"Test SVG saved to test_wire_label.svg")
