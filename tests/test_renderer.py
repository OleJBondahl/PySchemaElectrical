
import pytest
import xml.etree.ElementTree as ET
from src.core import Point, Style, Symbol
from src.primitives import Line, Circle, Text, Polygon, Group
from src.renderer import to_xml_element, render_to_svg
import os

class TestRenderer:
    def test_rendering_primitives(self):
        l = Line(Point(0,0), Point(10,10))
        c = Circle(Point(5,5), 2)
        t = Text("Hi", Point(0,0))
        
        root = to_xml_element([l, c, t])
        
        # Check root
        assert root.tag == "svg"
        
        # Check children (including background rect)
        # Background rect is first child
        # main group is second child
        main_g = root.find("g") 
        assert main_g is not None
        
        # Check for line
        line_elem = main_g.find("line")
        assert line_elem is not None
        assert line_elem.get("x1") == "0"
        assert line_elem.get("x2") == "10"
        
        # Check for circle
        circle_elem = main_g.find("circle")
        assert circle_elem is not None
        assert circle_elem.get("cx") == "5"
        
         # Check for text
        text_elem = main_g.find("text")
        assert text_elem is not None
        assert text_elem.text == "Hi"

    def test_rendering_symbol(self):
        l = Line(Point(0,0), Point(10,10))
        sym = Symbol(elements=[l], ports={})
        
        root = to_xml_element([sym])
        main_g = root.find("g")
        
        # Symbol is rendered as a group
        sym_g = main_g.find("g")
        assert sym_g is not None
        assert sym_g.get("class") == "symbol"
        
        # Inside symbol group, there should be a line
        line_elem = sym_g.find("line")
        assert line_elem is not None

    def test_render_to_file(self, tmp_path):
        # tmp_path is a pytest fixture providing a temporary directory
        f = tmp_path / "test.svg"
        l = Line(Point(0,0), Point(10,10))
        
        render_to_svg([l], str(f))
        
        assert f.exists()
        content = f.read_text(encoding="utf-8")
        assert "<svg" in content
        assert "<line" in content
