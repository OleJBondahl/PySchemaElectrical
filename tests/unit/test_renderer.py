from pyschemaelectrical.model.core import Point, Style, Symbol
from pyschemaelectrical.model.primitives import Circle, Line, Text
from pyschemaelectrical.utils.renderer import (
    calculate_bounds,
    render_to_svg,
    to_xml_element,
)


class TestRendererUnit:
    def test_primitives_xml_generation(self):
        line = Line(Point(0, 0), Point(10, 10))
        c = Circle(Point(5, 5), 2)
        t = Text("Hi", Point(0, 0))

        root = to_xml_element([line, c, t])
        assert root.tag == "svg"

        main_g = root.find("g")
        assert main_g is not None

        assert main_g.find("line") is not None
        assert main_g.find("circle") is not None
        assert main_g.find("text") is not None

    def test_symbol_rendering(self):
        line = Line(Point(0, 0), Point(10, 10))
        sym = Symbol(elements=[line], ports={})

        root = to_xml_element([sym])
        sym_g = root.find("g").find("g")

        assert sym_g is not None
        assert sym_g.get("class") == "symbol"
        assert sym_g.find("line") is not None

    def test_style_application(self):
        style = Style(stroke="red", stroke_width=2)
        line = Line(Point(0, 0), Point(10, 10), style=style)

        root = to_xml_element([line])
        line_elem = root.find("g").find("line")
        style_str = line_elem.get("style")

        assert "stroke:red" in style_str
        assert "stroke-width:2" in style_str

    def test_calculate_bounds(self):
        line = Line(Point(10, 20), Point(50, 80))
        c = Circle(Point(50, 50), 10)

        # Test line bounds
        assert calculate_bounds([line]) == (10, 20, 50, 80)

        # Test circle bounds (center +/- radius)
        # 50-10=40, 50+10=60
        assert calculate_bounds([c]) == (40, 40, 60, 60)

        # Test combined
        # min_x=10, min_y=20, max_x=60, max_y=80
        assert calculate_bounds([line, c]) == (10, 20, 60, 80)

    def test_render_to_file_output(self, tmp_path):
        f = tmp_path / "test.svg"
        line = Line(Point(0, 0), Point(10, 10))
        render_to_svg([line], str(f), width="auto", height="auto")

        assert f.exists()
        content = f.read_text(encoding="utf-8")
        assert "<svg" in content
        assert "viewBox" in content
