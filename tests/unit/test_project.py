"""Tests for the Project class."""

import os
import tempfile

from pyschemaelectrical import Project, Terminal
from pyschemaelectrical.builder import BuildResult


def test_project_creation():
    """Project should initialize with defaults."""
    p = Project()
    assert p.title == ""
    assert p.font == "Times New Roman"
    assert p._state is not None


def test_project_custom_params():
    """Project should accept custom parameters."""
    p = Project(
        title="Test",
        drawing_number="T-001",
        author="Author",
        project="Proj",
        revision="A1",
        font="Arial",
    )
    assert p.title == "Test"
    assert p.drawing_number == "T-001"
    assert p.font == "Arial"


def test_terminal_registration():
    """Terminals should be registered and retrievable."""
    p = Project()
    p.terminals(
        Terminal("X1", "Main Power"),
        Terminal("X2", "AC Input"),
        Terminal("X3", "24V", bridge="all"),
    )
    assert len(p._terminals) == 3
    assert "X1" in p._terminals
    assert p._terminals["X3"].bridge == "all"


def test_set_pin_start():
    """set_pin_start should update terminal counter in state."""
    p = Project()
    p.set_pin_start("X1", 5)
    assert p._state["terminal_counters"]["X1"] == 5


def test_dol_starter_registration():
    """dol_starter should register a circuit definition."""
    p = Project()
    p.dol_starter("motors", count=2, tm_top="X1", tm_bot="X2", tm_bot_right="PE")
    assert len(p._circuit_defs) == 1
    assert p._circuit_defs[0].key == "motors"
    assert p._circuit_defs[0].factory == "dol_starter"
    assert p._circuit_defs[0].count == 2


def test_psu_registration():
    """psu should register a circuit definition."""
    p = Project()
    p.psu("psu1", tm_top="X2", tm_bot_left="X3", tm_bot_right="X4")
    assert len(p._circuit_defs) == 1
    assert p._circuit_defs[0].factory == "psu"


def test_changeover_registration():
    """changeover should register a circuit definition."""
    p = Project()
    p.changeover("co", tm_top_left="X5", tm_top_right="X6", tm_bot="X7")
    assert p._circuit_defs[0].factory == "changeover"


def test_emergency_stop_registration():
    """emergency_stop should register a circuit definition."""
    p = Project()
    p.emergency_stop("estop", tm_top="X3", tm_bot="X20")
    assert p._circuit_defs[0].factory == "emergency_stop"


def test_coil_registration():
    """coil should register a circuit definition."""
    p = Project()
    p.coil("coils", count=3, tm_top="X3")
    assert p._circuit_defs[0].factory == "coil"
    assert p._circuit_defs[0].count == 3


def test_page_registration():
    """Pages should be registered in order."""
    p = Project()
    p.page("Motor Circuits", "motors")
    p.page("PSU", "psu")
    assert len(p._pages) == 2
    assert p._pages[0].title == "Motor Circuits"
    assert p._pages[1].circuit_key == "psu"


def test_terminal_report_registration():
    """terminal_report should add a page definition."""
    p = Project()
    p.terminal_report()
    assert len(p._pages) == 1
    assert p._pages[0].page_type == "terminal_report"


def test_front_page_registration():
    """front_page should add a page definition."""
    p = Project()
    p.front_page("readme.md", notice="Test notice")
    assert p._pages[0].page_type == "front"
    assert p._pages[0].notice == "Test notice"


def test_circuit_descriptor_registration():
    """circuit() with descriptors should register correctly."""
    from pyschemaelectrical import ref, comp, term
    from pyschemaelectrical.symbols.coils import coil_symbol

    p = Project()
    p.circuit(
        "valve_coils",
        components=[
            ref("PLC:DO"),
            comp(coil_symbol, "K", pins=("A1", "A2")),
            term("X4"),
        ],
        count=3,
    )
    assert p._circuit_defs[0].factory == "descriptors"
    assert len(p._circuit_defs[0].components) == 3


def test_build_svgs():
    """build_svgs should generate SVG files for each circuit."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Project()
        p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))
        p.emergency_stop("estop", tm_top="X3", tm_bot="X4")

        output_dir = os.path.join(tmpdir, "output")
        p.build_svgs(output_dir)

        # Check that SVG was generated
        svg_path = os.path.join(output_dir, "estop.svg")
        assert os.path.exists(svg_path), f"SVG not found at {svg_path}"

        # Check that system terminals CSV was generated
        csv_path = os.path.join(output_dir, "system_terminals.csv")
        assert os.path.exists(csv_path), f"CSV not found at {csv_path}"


def test_build_multiple_circuits():
    """build_svgs should handle multiple circuits."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Project()
        p.terminals(
            Terminal("X1", "Power"),
            Terminal("X3", "24V"),
            Terminal("X4", "GND"),
            Terminal("X5", "Supply 1"),
            Terminal("X6", "Supply 2"),
            Terminal("X7", "Output"),
        )

        p.emergency_stop("estop", tm_top="X3", tm_bot="X4")
        p.changeover("co", tm_top_left="X5", tm_top_right="X6", tm_bot="X7")

        output_dir = os.path.join(tmpdir, "output")
        p.build_svgs(output_dir)

        assert os.path.exists(os.path.join(output_dir, "estop.svg"))
        assert os.path.exists(os.path.join(output_dir, "co.svg"))


def test_build_with_descriptors():
    """build_svgs should work with descriptor-based circuits."""
    from pyschemaelectrical import comp, term
    from pyschemaelectrical.symbols.coils import coil_symbol

    with tempfile.TemporaryDirectory() as tmpdir:
        p = Project()
        p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))

        p.circuit(
            "coils",
            components=[
                term("X3"),
                comp(coil_symbol, "K", pins=("A1", "A2")),
                term("X4"),
            ],
            count=2,
        )

        output_dir = os.path.join(tmpdir, "output")
        p.build_svgs(output_dir)

        assert os.path.exists(os.path.join(output_dir, "coils.svg"))


def test_reuse_tags_between_circuits():
    """reuse_tags should resolve circuit dependencies correctly."""
    from pyschemaelectrical import comp, term
    from pyschemaelectrical.symbols.coils import coil_symbol
    from pyschemaelectrical.symbols.contacts import normally_open_symbol

    with tempfile.TemporaryDirectory() as tmpdir:
        p = Project()
        p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))

        # Coils circuit (allocates K tags)
        p.circuit(
            "coils",
            components=[
                term("X3"),
                comp(coil_symbol, "K", pins=("A1", "A2")),
                term("X4"),
            ],
            count=2,
        )

        # Contacts circuit (reuses K tags from coils)
        p.circuit(
            "contacts",
            components=[
                term("X3"),
                comp(normally_open_symbol, "K", pins=("13", "14")),
                term("X4"),
            ],
            count=2,
            reuse_tags={"K": "coils"},
        )

        output_dir = os.path.join(tmpdir, "output")
        p.build_svgs(output_dir)

        assert os.path.exists(os.path.join(output_dir, "coils.svg"))
        assert os.path.exists(os.path.join(output_dir, "contacts.svg"))
