
import pytest
import xml.etree.ElementTree as ET
from pyschemaelectrical.core import Point, Style
from pyschemaelectrical.primitives import Line, Circle, Text, Polygon, Group
from pyschemaelectrical.renderer import to_xml_element, render_to_svg, calculate_bounds


class TestRendererAdvanced:
    """Additional comprehensive tests for renderer module."""
    
    def test_auto_sizing_width(self, tmp_path):
        """Test auto-sizing for width parameter."""
        f = tmp_path / "auto_width.svg"
        l = Line(Point(0,0), Point(100,50))
        
        render_to_svg([l], str(f), width="auto", height=200)
        
        assert f.exists()
        content = f.read_text(encoding="utf-8")
        # Should have a viewBox
        assert "viewBox" in content

    def test_auto_sizing_height(self, tmp_path):
        """Test auto-sizing for height parameter."""
        f = tmp_path / "auto_height.svg"
        l = Line(Point(0,0), Point(100,50))
        
        render_to_svg([l], str(f), width=200, height="auto")
        
        assert f.exists()
        content = f.read_text(encoding="utf-8")
        # Should have a viewBox
        assert "viewBox" in content

    def test_auto_sizing_both(self, tmp_path):
        """Test auto-sizing for both width and height."""
        f = tmp_path / "auto_both.svg"
        elements = [
            Line(Point(10,10), Point(100,100)),
            Circle(Point(50,50), 20)
        ]
        
        render_to_svg(elements, str(f), width="auto", height="auto")
        
        assert f.exists()
        content = f.read_text(encoding="utf-8")
        assert "viewBox" in content
        # Background should be present
        assert "<rect" in content

    def test_polygon_rendering(self):
        """Test that polygons are rendered correctly."""
        points = [Point(0,0), Point(10,0), Point(10,10), Point(0,10)]
        poly = Polygon(points)
        
        root = to_xml_element([poly])
        main_g = root.find("g")
        
        poly_elem = main_g.find("polygon")
        assert poly_elem is not None
        points_str = poly_elem.get("points")
        assert "0,0" in points_str
        assert "10,10" in points_str

    def test_group_rendering(self):
        """Test that groups and nested elements are rendered correctly."""
        l1 = Line(Point(0,0), Point(10,10))
        l2 = Line(Point(10,10), Point(20,20))
        group = Group([l1, l2])
        
        root = to_xml_element([group])
        main_g = root.find("g")
        
        # Group should be rendered as a 'g' element
        nested_g = main_g.find("g")
        assert nested_g is not None
        
        # Should have two lines inside
        lines = nested_g.findall("line")
        assert len(lines) == 2

    def test_style_application(self):
        """Test that styles are properly applied to elements."""
        style = Style(stroke="red", stroke_width=2, fill="blue")
        l = Line(Point(0,0), Point(10,10), style=style)
        
        root = to_xml_element([l])
        main_g = root.find("g")
        line_elem = main_g.find("line")
        
        style_str = line_elem.get("style")
        assert "stroke:red" in style_str
        assert "stroke-width:2" in style_str
        assert "fill:blue" in style_str

    def test_empty_elements_list(self):
        """Test rendering with an empty elements list."""
        root = to_xml_element([])
        assert root.tag == "svg"
        # Should still have background
        bg = root.find("rect")
        assert bg is not None

    def test_calculate_bounds_empty(self):
        """Test bounds calculation with empty list."""
        bounds = calculate_bounds([])
        assert bounds == (0, 0, 100, 100)  # Default bounds

    def test_calculate_bounds_line(self):
        """Test bounds calculation for a line."""
        l = Line(Point(10,20), Point(50,80))
        min_x, min_y, max_x, max_y = calculate_bounds([l])
        
        assert min_x == 10
        assert min_y == 20
        assert max_x == 50
        assert max_y == 80

    def test_calculate_bounds_circle(self):
        """Test bounds calculation for a circle."""
        c = Circle(Point(50,50), 10)
        min_x, min_y, max_x, max_y = calculate_bounds([c])
        
        assert min_x == 40  # center - radius
        assert min_y == 40
        assert max_x == 60  # center + radius
        assert max_y == 60

    def test_calculate_bounds_multiple(self):
        """Test bounds calculation for multiple elements."""
        elements = [
            Line(Point(0,0), Point(50,50)),
            Circle(Point(100,100), 20)
        ]
        min_x, min_y, max_x, max_y = calculate_bounds(elements)
        
        assert min_x == 0
        assert min_y == 0
        assert max_x == 120  # circle center + radius
        assert max_y == 120

    def test_text_rendering_with_rotation(self):
        """Test text element rendering with rotation."""
        t = Text("Test", Point(50,50), rotation=45)
        
        root = to_xml_element([t])
        main_g = root.find("g")
        text_elem = main_g.find("text")
        
        assert text_elem is not None
        assert text_elem.text == "Test"
        transform = text_elem.get("transform")
        assert transform is not None
        assert "rotate(45" in transform

    def test_text_rendering_no_rotation(self):
        """Test text element rendering without rotation."""
        t = Text("NoRotate", Point(50,50))
        
        root = to_xml_element([t])
        main_g = root.find("g")
        text_elem = main_g.find("text")
        
        assert text_elem is not None
        assert text_elem.text == "NoRotate"
        # No transform attribute when rotation is 0
        assert text_elem.get("transform") is None
