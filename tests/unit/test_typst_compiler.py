"""Tests for the TypstCompiler class."""

import os
import tempfile

from pyschemaelectrical.rendering.typst.compiler import (
    TypstCompiler,
    TypstCompilerConfig,
)


def test_config_defaults():
    """TypstCompilerConfig should have sensible defaults."""
    config = TypstCompilerConfig()
    assert config.drawing_name == ""
    assert config.drawing_number == ""
    assert config.font_family == "Times New Roman"
    assert config.root_dir == "."
    assert config.temp_dir == "temp"
    assert config.logo_path is None


def test_config_custom_values():
    """TypstCompilerConfig should accept custom values."""
    config = TypstCompilerConfig(
        drawing_name="Test Drawing",
        drawing_number="TST-001",
        author="Test Author",
        project="Test Project",
        revision="A1",
        logo_path="/path/to/logo.png",
        font_family="Arial",
    )
    assert config.drawing_name == "Test Drawing"
    assert config.drawing_number == "TST-001"
    assert config.font_family == "Arial"
    assert config.logo_path == "/path/to/logo.png"


def test_compiler_add_schematic_page():
    """Adding a schematic page should be recorded."""
    config = TypstCompilerConfig()
    compiler = TypstCompiler(config)
    compiler.add_schematic_page("Test Page", "test.svg", "test_terminals.csv")
    assert len(compiler._pages) == 1
    assert compiler._pages[0].page_type == "schematic"
    assert compiler._pages[0].title == "Test Page"


def test_compiler_add_front_page():
    """Adding a front page should be recorded."""
    config = TypstCompilerConfig()
    compiler = TypstCompiler(config)
    compiler.add_front_page("test.md")
    assert len(compiler._pages) == 1
    assert compiler._pages[0].page_type == "front"


def test_compiler_add_terminal_report():
    """Adding a terminal report should be recorded."""
    config = TypstCompilerConfig()
    compiler = TypstCompiler(config)
    descriptions = {"X1": "Main Power", "X2": "AC Input"}
    compiler.add_terminal_report("system.csv", descriptions)
    assert len(compiler._pages) == 1
    assert compiler._pages[0].page_type == "terminal_report"
    assert compiler._pages[0].terminal_descriptions == descriptions


def test_compiler_add_plc_report():
    """Adding a PLC report should be recorded."""
    config = TypstCompilerConfig()
    compiler = TypstCompiler(config)
    compiler.add_plc_report("plc.csv")
    assert len(compiler._pages) == 1
    assert compiler._pages[0].page_type == "plc_report"


def test_compiler_add_custom_page():
    """Adding a custom page should be recorded."""
    config = TypstCompilerConfig()
    compiler = TypstCompiler(config)
    compiler.add_custom_page("Custom", "#text[Hello]")
    assert len(compiler._pages) == 1
    assert compiler._pages[0].page_type == "custom"
    assert compiler._pages[0].typst_content == "#text[Hello]"


def test_compiler_multiple_pages():
    """Compiler should handle multiple pages in order."""
    config = TypstCompilerConfig()
    compiler = TypstCompiler(config)
    compiler.add_schematic_page("Page 1", "p1.svg")
    compiler.add_schematic_page("Page 2", "p2.svg", "p2.csv")
    compiler.add_custom_page("Notes", "#text[Notes]")
    assert len(compiler._pages) == 3
    assert compiler._pages[0].title == "Page 1"
    assert compiler._pages[1].title == "Page 2"
    assert compiler._pages[2].title == "Notes"


def test_compiler_build_typst_content():
    """_build_typst_content should generate valid Typst markup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = TypstCompilerConfig(
            drawing_name="Test",
            drawing_number="T-001",
            author="Author",
            project="Project",
            root_dir=tmpdir,
            temp_dir="temp",
        )
        compiler = TypstCompiler(config)
        compiler.add_schematic_page("Motor Circuit", "test.svg")

        # Create temp directory and frame
        temp_dir = os.path.join(tmpdir, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        frame_path = os.path.join(temp_dir, "A3_frame.svg")
        template_path = compiler._get_template_path()

        # Copy template to temp dir
        template_dest = os.path.join(temp_dir, "a3_drawing.typ")
        with open(template_path, "r") as f:
            content = f.read()
        with open(template_dest, "w") as f:
            f.write(content)

        result = compiler._build_typst_content(frame_path, template_dest)

        assert "#import" in result
        assert "a3_drawing" in result
        assert "T-001" in result
        assert "Motor Circuit" in result
        assert 'schematic("test.svg"' in result


def test_template_file_exists():
    """The a3_drawing.typ template should exist in the package."""
    config = TypstCompilerConfig()
    compiler = TypstCompiler(config)
    path = compiler._get_template_path()
    assert os.path.exists(path), f"Template not found at {path}"
