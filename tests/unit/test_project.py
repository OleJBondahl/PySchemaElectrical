"""Tests for the Project class."""

import os
import tempfile
from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest

from pyschemaelectrical import Project, Terminal
from pyschemaelectrical.builder import BuildResult
from pyschemaelectrical.system.system import Circuit


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
    assert p._state.terminal_counters["X1"] == 5


def test_dol_starter_registration():
    """dol_starter should register a circuit definition."""
    p = Project()
    p.dol_starter("motors", count=2, tm_top="X1", tm_bot="X2")
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
    from pyschemaelectrical import comp, ref, term
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


# =========================================================================
# Additional tests for coverage improvement
# =========================================================================


class TestProjectInit:
    """Tests for Project.__init__() defaults and attributes."""

    def test_defaults_all_attributes(self):
        """All default values should be set correctly."""
        p = Project()
        assert p.title == ""
        assert p.drawing_number == ""
        assert p.author == ""
        assert p.project == ""
        assert p.revision == "00"
        assert p.logo is None
        assert p.font == "Times New Roman"
        assert p._terminals == {}
        assert p._circuit_defs == []
        assert p._pages == []
        assert p._results == {}

    def test_logo_param(self):
        """Project should accept a logo path."""
        p = Project(logo="/path/to/logo.png")
        assert p.logo == "/path/to/logo.png"


class TestTerminalRegistration:
    """Tests for terminal registration edge cases."""

    def test_overwrite_terminal(self):
        """Registering a terminal with same ID should overwrite."""
        p = Project()
        p.terminals(Terminal("X1", "First"))
        p.terminals(Terminal("X1", "Second"))
        assert len(p._terminals) == 1
        assert p._terminals["X1"].description == "Second"

    def test_empty_terminal_registration(self):
        """Calling terminals() with no args should not fail."""
        p = Project()
        p.terminals()
        assert len(p._terminals) == 0

    def test_reference_terminal(self):
        """Reference terminals should store reference=True."""
        p = Project()
        p.terminals(Terminal("PLC:DO", "PLC Output", reference=True))
        assert p._terminals["PLC:DO"].reference is True

    def test_terminal_with_pin_prefixes(self):
        """Terminal with pin_prefixes should be stored correctly."""
        p = Project()
        p.terminals(Terminal("X1", "Power", pin_prefixes=("L1", "L2", "L3")))
        assert p._terminals["X1"].pin_prefixes == ("L1", "L2", "L3")


class TestSetPinStart:
    """Tests for set_pin_start including prefix counter updates."""

    def test_set_pin_start_updates_prefix_counters(self):
        """set_pin_start should update all existing prefix counters for the terminal."""
        p = Project()
        # First, create prefix counters by building a circuit that uses prefixed terminals
        # Manually set up state with prefix counters
        p._state = replace(
            p._state,
            terminal_prefix_counters={
                "X1": {"L1": 2, "L2": 2, "L3": 2},
            },
        )
        p.set_pin_start("X1", 5)
        assert p._state.terminal_counters["X1"] == 5
        # All prefix counters should be updated to 5
        assert p._state.terminal_prefix_counters["X1"]["L1"] == 5
        assert p._state.terminal_prefix_counters["X1"]["L2"] == 5
        assert p._state.terminal_prefix_counters["X1"]["L3"] == 5

    def test_set_pin_start_without_prefix_counters(self):
        """set_pin_start should work when no prefix counters exist."""
        p = Project()
        p.set_pin_start("X2", 10)
        assert p._state.terminal_counters["X2"] == 10
        # prefix_counters should remain unchanged (empty)
        assert "X2" not in p._state.terminal_prefix_counters

    def test_set_pin_start_multiple_terminals(self):
        """set_pin_start for different terminals should not interfere."""
        p = Project()
        p.set_pin_start("X1", 5)
        p.set_pin_start("X2", 10)
        assert p._state.terminal_counters["X1"] == 5
        assert p._state.terminal_counters["X2"] == 10


class TestCircuitRegistration:
    """Tests for all circuit registration methods."""

    def test_spdt_registration(self):
        """spdt should register a circuit definition."""
        p = Project()
        p.spdt("relays", count=2, tm_top="X3", tm_bot_left="X4", tm_bot_right="X5")
        assert len(p._circuit_defs) == 1
        assert p._circuit_defs[0].key == "relays"
        assert p._circuit_defs[0].factory == "spdt"
        assert p._circuit_defs[0].count == 2

    def test_no_contact_registration(self):
        """no_contact should register a circuit definition."""
        p = Project()
        p.no_contact("contacts", count=4, tm_top="X3", tm_bot="X4")
        assert len(p._circuit_defs) == 1
        assert p._circuit_defs[0].key == "contacts"
        assert p._circuit_defs[0].factory == "no_contact"
        assert p._circuit_defs[0].count == 4

    def test_custom_registration(self):
        """custom() should register a custom builder function circuit."""

        def my_builder(state, **kwargs):
            return BuildResult(
                state=state,
                circuit=Circuit(),
                used_terminals=[],
            )

        p = Project()
        p.custom("my_circuit", my_builder, count=2, some_param="value")
        assert len(p._circuit_defs) == 1
        assert p._circuit_defs[0].key == "my_circuit"
        assert p._circuit_defs[0].factory == "custom"
        assert p._circuit_defs[0].count == 2
        assert p._circuit_defs[0].builder_fn is my_builder
        assert p._circuit_defs[0].params == {"some_param": "value"}

    def test_circuit_with_wire_labels(self):
        """Circuit registration should store wire_labels correctly."""
        p = Project()
        p.dol_starter(
            "motors",
            count=2,
            tm_top="X1",
            tm_bot="X2",
            wire_labels=["L1", "L2"],
        )
        assert p._circuit_defs[0].wire_labels == ["L1", "L2"]

    def test_circuit_with_reuse_tags(self):
        """Circuit registration should store reuse_tags correctly."""
        p = Project()
        p.no_contact(
            "contacts",
            count=2,
            tm_top="X3",
            tm_bot="X4",
            reuse_tags={"K": "coils"},
        )
        assert p._circuit_defs[0].reuse_tags == {"K": "coils"}

    def test_circuit_descriptor_with_start_indices(self):
        """circuit() should accept start_indices and terminal_start_indices."""
        from pyschemaelectrical import comp, term
        from pyschemaelectrical.symbols.coils import coil_symbol

        p = Project()
        p.circuit(
            "coils",
            components=[
                term("X3"),
                comp(coil_symbol, "K", pins=("A1", "A2")),
                term("X4"),
            ],
            count=2,
            start_indices={"K": 5},
            terminal_start_indices={"X3": 10},
        )
        assert p._circuit_defs[0].start_indices == {"K": 5}
        assert p._circuit_defs[0].terminal_start_indices == {"X3": 10}

    def test_multiple_circuits_registered_in_order(self):
        """Multiple circuits should be registered in order."""
        p = Project()
        p.emergency_stop("estop", tm_top="X3", tm_bot="X4")
        p.coil("coils", count=2, tm_top="X3")
        p.no_contact("contacts", count=2, tm_top="X3", tm_bot="X4")
        assert len(p._circuit_defs) == 3
        assert p._circuit_defs[0].key == "estop"
        assert p._circuit_defs[1].key == "coils"
        assert p._circuit_defs[2].key == "contacts"


class TestPageRegistration:
    """Tests for all page registration methods."""

    def test_plc_report_registration(self):
        """plc_report should add a page definition."""
        p = Project()
        p.plc_report(csv_path="plc_data.csv")
        assert len(p._pages) == 1
        assert p._pages[0].page_type == "plc_report"
        assert p._pages[0].csv_path == "plc_data.csv"

    def test_plc_report_default_csv(self):
        """plc_report with no csv_path should default to empty string."""
        p = Project()
        p.plc_report()
        assert p._pages[0].csv_path == ""

    def test_custom_page_registration(self):
        """custom_page should add a page with raw Typst content."""
        p = Project()
        p.custom_page("My Custom Page", "#text(size: 20pt)[Hello World]")
        assert len(p._pages) == 1
        assert p._pages[0].page_type == "custom"
        assert p._pages[0].title == "My Custom Page"
        assert p._pages[0].typst_content == "#text(size: 20pt)[Hello World]"

    def test_front_page_without_notice(self):
        """front_page without notice should default to None."""
        p = Project()
        p.front_page("readme.md")
        assert p._pages[0].notice is None

    def test_page_ordering(self):
        """Pages should be appended in registration order."""
        p = Project()
        p.front_page("readme.md")
        p.page("Motors", "motors")
        p.terminal_report()
        p.plc_report()
        p.custom_page("Notes", "content")
        assert len(p._pages) == 5
        assert p._pages[0].page_type == "front"
        assert p._pages[1].page_type == "schematic"
        assert p._pages[2].page_type == "terminal_report"
        assert p._pages[3].page_type == "plc_report"
        assert p._pages[4].page_type == "custom"


class TestBuildOneCircuit:
    """Tests for _build_one_circuit error paths and dispatching."""

    def test_reuse_tags_missing_source_raises(self):
        """Referencing a non-existent circuit via reuse_tags should raise ValueError."""
        from pyschemaelectrical import comp, term
        from pyschemaelectrical.symbols.coils import coil_symbol

        p = Project()
        p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))
        p.circuit(
            "contacts",
            components=[
                term("X3"),
                comp(coil_symbol, "K", pins=("A1", "A2")),
                term("X4"),
            ],
            count=2,
            reuse_tags={"K": "nonexistent"},
        )
        with pytest.raises(ValueError, match="hasn't been built yet"):
            p.build_svgs(tempfile.mkdtemp())

    def test_unknown_factory_raises(self):
        """An unknown factory name should raise ValueError."""
        p = Project()
        # Manually inject an invalid factory name
        from pyschemaelectrical.project import _CircuitDef

        p._circuit_defs.append(
            _CircuitDef(key="bad", factory="nonexistent_factory", params={})
        )
        with pytest.raises(ValueError, match="Unknown circuit factory"):
            p.build_svgs(tempfile.mkdtemp())

    def test_descriptor_circuit_without_components_raises(self):
        """Descriptor circuit with no components should raise ValueError."""
        p = Project()
        from pyschemaelectrical.project import _CircuitDef

        p._circuit_defs.append(
            _CircuitDef(key="bad", factory="descriptors", components=None)
        )
        with pytest.raises(ValueError, match="has no components defined"):
            p.build_svgs(tempfile.mkdtemp())

    def test_custom_circuit_without_builder_fn_raises(self):
        """Custom circuit with no builder_fn should raise ValueError."""
        p = Project()
        from pyschemaelectrical.project import _CircuitDef

        p._circuit_defs.append(
            _CircuitDef(key="bad", factory="custom", builder_fn=None)
        )
        with pytest.raises(ValueError, match="has no builder_fn defined"):
            p.build_svgs(tempfile.mkdtemp())


class TestBuildCustomCircuit:
    """Tests for _build_custom_circuit method."""

    def test_custom_circuit_with_build_result(self):
        """Custom builder returning BuildResult should work."""
        from pyschemaelectrical.utils.autonumbering import create_autonumberer

        state = create_autonumberer()

        def my_builder(state, **kwargs):
            return BuildResult(
                state=state,
                circuit=Circuit(),
                used_terminals=[],
            )

        p = Project()
        p.terminals(Terminal("X3", "24V"))
        p.custom("my_circuit", my_builder)

        with tempfile.TemporaryDirectory() as tmpdir:
            p.build_svgs(tmpdir)
            assert os.path.exists(os.path.join(tmpdir, "my_circuit.svg"))

    def test_custom_circuit_with_tuple_return(self):
        """Custom builder returning a tuple should be wrapped in BuildResult."""

        def my_builder(state, **kwargs):
            return (state, Circuit(), [])

        p = Project()
        p.custom("my_circuit", my_builder)

        with tempfile.TemporaryDirectory() as tmpdir:
            p.build_svgs(tmpdir)
            assert os.path.exists(os.path.join(tmpdir, "my_circuit.svg"))

    def test_custom_circuit_with_kwargs(self):
        """Custom builder should receive extra kwargs from params."""
        received_kwargs = {}

        def my_builder(state, **kwargs):
            received_kwargs.update(kwargs)
            return BuildResult(
                state=state,
                circuit=Circuit(),
                used_terminals=[],
            )

        p = Project()
        p.custom("my_circuit", my_builder, foo="bar", baz=42)

        with tempfile.TemporaryDirectory() as tmpdir:
            p.build_svgs(tmpdir)
        assert received_kwargs == {"foo": "bar", "baz": 42}


class TestBuildSvgs:
    """Tests for build_svgs method."""

    def test_build_svgs_with_bridge_defs(self):
        """build_svgs should apply bridge definitions from non-reference terminals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            p.terminals(
                Terminal("X3", "24V", bridge="all"),
                Terminal("X4", "GND", bridge="all"),
            )
            p.emergency_stop("estop", tm_top="X3", tm_bot="X4")

            output_dir = os.path.join(tmpdir, "output")
            p.build_svgs(output_dir)

            # Check SVG and CSV exist
            assert os.path.exists(os.path.join(output_dir, "estop.svg"))
            assert os.path.exists(os.path.join(output_dir, "system_terminals.csv"))

    def test_build_svgs_reference_terminals_excluded_from_bridges(self):
        """Reference terminals should not contribute bridge definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            p.terminals(
                Terminal("PLC:DO", "PLC Output", reference=True, bridge="all"),
                Terminal("X3", "24V"),
                Terminal("X4", "GND"),
            )
            p.emergency_stop("estop", tm_top="X3", tm_bot="X4")

            output_dir = os.path.join(tmpdir, "output")
            p.build_svgs(output_dir)

            assert os.path.exists(os.path.join(output_dir, "estop.svg"))

    def test_build_svgs_with_no_used_terminals(self):
        """build_svgs should skip per-circuit CSV when used_terminals is empty."""

        def my_builder(state, **kwargs):
            return BuildResult(
                state=state,
                circuit=Circuit(),
                used_terminals=[],
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            p.custom("my_circuit", my_builder)

            p.build_svgs(tmpdir)

            # SVG should exist, but no per-circuit terminals CSV
            assert os.path.exists(os.path.join(tmpdir, "my_circuit.svg"))
            assert not os.path.exists(os.path.join(tmpdir, "my_circuit_terminals.csv"))

    def test_build_svgs_creates_output_dir(self):
        """build_svgs should create the output directory if it does not exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "deep", "nested", "output")
            p = Project()

            def my_builder(state, **kwargs):
                return BuildResult(state=state, circuit=Circuit(), used_terminals=[])

            p.custom("test", my_builder)
            p.build_svgs(output_dir)

            assert os.path.isdir(output_dir)

    def test_build_svgs_with_wire_labels(self):
        """build_svgs should work with wire_labels on std circuits."""
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
                wire_labels=["BKWH1", "BKWH2", "BKWH3", "BKWH4"],
            )

            p.build_svgs(tmpdir)
            assert os.path.exists(os.path.join(tmpdir, "coils.svg"))


class TestAddPageToCompiler:
    """Tests for _add_page_to_compiler with mocked compiler."""

    def _make_project_with_results(self):
        """Helper: create a Project with a mock build result."""
        p = Project()
        p.terminals(
            Terminal("X3", "24V"),
            Terminal("X4", "GND"),
            Terminal("PLC:DO", "PLC Output", reference=True),
        )
        p._results = {
            "estop": BuildResult(
                state=p._state,
                circuit=Circuit(),
                used_terminals=["X3", "X4"],
            ),
        }
        return p

    def test_schematic_page(self):
        """Schematic page should call add_schematic_page on the compiler."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()
        svg_paths = {"estop": "/tmp/estop.svg"}
        csv_paths = {"estop": "/tmp/estop_terminals.csv"}

        page_def = _PageDef(page_type="schematic", title="E-Stop", circuit_key="estop")
        p._add_page_to_compiler(
            compiler, page_def, svg_paths, csv_paths, "/tmp/system.csv"
        )

        compiler.add_schematic_page.assert_called_once_with(
            "E-Stop", "/tmp/estop.svg", "/tmp/estop_terminals.csv"
        )

    def test_schematic_page_without_csv(self):
        """Schematic page without CSV should pass None."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()
        svg_paths = {"estop": "/tmp/estop.svg"}
        csv_paths = {}  # No CSV for this circuit

        page_def = _PageDef(page_type="schematic", title="E-Stop", circuit_key="estop")
        p._add_page_to_compiler(
            compiler, page_def, svg_paths, csv_paths, "/tmp/system.csv"
        )

        compiler.add_schematic_page.assert_called_once_with(
            "E-Stop", "/tmp/estop.svg", None
        )

    def test_schematic_page_missing_key(self):
        """Schematic page with missing circuit key should not call add_schematic_page."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()

        page_def = _PageDef(
            page_type="schematic", title="Missing", circuit_key="missing"
        )
        p._add_page_to_compiler(compiler, page_def, {}, {}, "/tmp/system.csv")

        compiler.add_schematic_page.assert_not_called()

    def test_front_page(self):
        """Front page should call add_front_page on the compiler."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()

        page_def = _PageDef(
            page_type="front", md_path="readme.md", notice="Test notice"
        )
        p._add_page_to_compiler(compiler, page_def, {}, {}, "/tmp/system.csv")

        compiler.add_front_page.assert_called_once_with(
            "readme.md", notice="Test notice"
        )

    def test_terminal_report_page(self):
        """Terminal report should call add_terminal_report with descriptions, excluding references."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()

        page_def = _PageDef(page_type="terminal_report")
        p._add_page_to_compiler(compiler, page_def, {}, {}, "/tmp/system.csv")

        compiler.add_terminal_report.assert_called_once()
        call_args = compiler.add_terminal_report.call_args
        assert call_args[0][0] == "/tmp/system.csv"
        descriptions = call_args[0][1]
        # Reference terminal should be excluded
        assert "PLC:DO" not in descriptions
        assert "X3" in descriptions
        assert "X4" in descriptions

    def test_plc_report_page_with_csv(self):
        """PLC report with a CSV path should call add_plc_report."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()

        page_def = _PageDef(page_type="plc_report", csv_path="/tmp/plc.csv")
        p._add_page_to_compiler(compiler, page_def, {}, {}, "/tmp/system.csv")

        compiler.add_plc_report.assert_called_once_with("/tmp/plc.csv")

    def test_plc_report_page_without_csv(self):
        """PLC report without CSV path should not call add_plc_report."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()

        page_def = _PageDef(page_type="plc_report", csv_path="")
        p._add_page_to_compiler(compiler, page_def, {}, {}, "/tmp/system.csv")

        compiler.add_plc_report.assert_not_called()

    def test_custom_page(self):
        """Custom page should call add_custom_page on the compiler."""
        from pyschemaelectrical.project import _PageDef

        p = self._make_project_with_results()
        compiler = MagicMock()

        page_def = _PageDef(
            page_type="custom",
            title="Notes",
            typst_content="#text[Hello]",
        )
        p._add_page_to_compiler(compiler, page_def, {}, {}, "/tmp/system.csv")

        compiler.add_custom_page.assert_called_once_with("Notes", "#text[Hello]")


class TestBuildMethod:
    """Tests for the build() method (PDF compilation) with mocked Typst."""

    def _mock_build(self, project, output_pdf, temp_dir, keep_temp=True):
        """Helper to run build() with mocked Typst compiler."""
        mock_typst_module = MagicMock()
        mock_compiler_inst = MagicMock()
        mock_typst_module.TypstCompiler.return_value = mock_compiler_inst
        mock_typst_module.TypstCompilerConfig = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "pyschemaelectrical.rendering.typst.compiler": mock_typst_module,
            },
        ):
            project.build(output_pdf, temp_dir=temp_dir, keep_temp=keep_temp)

        return mock_typst_module, mock_compiler_inst

    def test_build_calls_typst_compiler(self):
        """build() should create TypstCompiler, add pages, and compile."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp")

            p = Project(
                title="Test",
                drawing_number="T-001",
                author="Author",
                project="Proj",
                revision="A1",
                font="Arial",
            )
            p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))
            p.emergency_stop("estop", tm_top="X3", tm_bot="X4")
            p.page("Test Page", "estop")

            mock_module, mock_compiler = self._mock_build(
                p, output_pdf, temp_dir, keep_temp=True
            )

            mock_module.TypstCompiler.assert_called_once()
            mock_compiler.compile.assert_called_once_with(output_pdf)

    def test_build_generates_per_circuit_csv(self):
        """build() should generate per-circuit terminal CSV for circuits with used_terminals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp")

            p = Project()
            p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))
            p.emergency_stop("estop", tm_top="X3", tm_bot="X4")

            self._mock_build(p, output_pdf, temp_dir, keep_temp=True)

            # Per-circuit CSV should be generated (estop has used_terminals)
            csv_path = os.path.join(temp_dir, "estop_terminals.csv")
            assert os.path.exists(csv_path)

    def test_build_with_bridge_defs(self):
        """build() should apply bridge definitions from terminals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp")

            p = Project()
            p.terminals(
                Terminal("X3", "24V", bridge="all"),
                Terminal("X4", "GND", bridge="all"),
            )
            p.emergency_stop("estop", tm_top="X3", tm_bot="X4")

            self._mock_build(p, output_pdf, temp_dir, keep_temp=True)

            # System CSV should exist
            system_csv = os.path.join(temp_dir, "system_terminals.csv")
            assert os.path.exists(system_csv)

    def test_build_cleans_temp_dir_by_default(self):
        """build() should remove temp_dir when keep_temp=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp_build")

            def my_builder(state, **kwargs):
                return BuildResult(state=state, circuit=Circuit(), used_terminals=[])

            p = Project()
            p.custom("test_circuit", my_builder)

            self._mock_build(p, output_pdf, temp_dir, keep_temp=False)

            # temp_dir should have been cleaned up
            assert not os.path.exists(temp_dir)

    def test_build_keeps_temp_dir_when_requested(self):
        """build() should keep temp_dir when keep_temp=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp_build")

            def my_builder(state, **kwargs):
                return BuildResult(state=state, circuit=Circuit(), used_terminals=[])

            p = Project()
            p.custom("test_circuit", my_builder)

            self._mock_build(p, output_pdf, temp_dir, keep_temp=True)

            # temp_dir should still exist
            assert os.path.exists(temp_dir)

    def test_build_with_logo(self):
        """build() should handle logo path configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp")
            logo_path = os.path.join(tmpdir, "logo.png")
            # Create a dummy logo file
            with open(logo_path, "w") as f:
                f.write("dummy")

            def my_builder(state, **kwargs):
                return BuildResult(state=state, circuit=Circuit(), used_terminals=[])

            p = Project(logo=logo_path)
            p.custom("test", my_builder)

            self._mock_build(p, output_pdf, temp_dir, keep_temp=True)


class TestBuildAllCircuits:
    """Tests for _build_all_circuits method."""

    def test_state_threading_between_circuits(self):
        """State should be threaded from one circuit to the next."""
        from pyschemaelectrical import comp, term
        from pyschemaelectrical.symbols.coils import coil_symbol

        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))

            # Register two circuits that both use "K" prefix
            p.circuit(
                "coils1",
                components=[
                    term("X3"),
                    comp(coil_symbol, "K", pins=("A1", "A2")),
                    term("X4"),
                ],
                count=2,
            )
            p.circuit(
                "coils2",
                components=[
                    term("X3"),
                    comp(coil_symbol, "K", pins=("A1", "A2")),
                    term("X4"),
                ],
                count=2,
            )

            p.build_svgs(tmpdir)

            # Both circuits should be built
            assert "coils1" in p._results
            assert "coils2" in p._results

            # Second circuit should have K3, K4 (since first used K1, K2)
            assert "K" in p._results["coils2"].component_map
            assert p._results["coils2"].component_map["K"] == ["K3", "K4"]

    def test_results_cleared_on_each_build(self):
        """_build_all_circuits should clear results before building."""

        def my_builder(state, **kwargs):
            return BuildResult(state=state, circuit=Circuit(), used_terminals=[])

        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            p.custom("circuit1", my_builder)

            p.build_svgs(os.path.join(tmpdir, "out1"))
            assert "circuit1" in p._results

            # Build again - results should be re-created, not appended
            p.build_svgs(os.path.join(tmpdir, "out2"))
            assert len(p._results) == 1


class TestBuildStdCircuit:
    """Tests for _build_std_circuit with wire_labels."""

    def test_std_circuit_with_wire_labels(self):
        """Standard circuits should pass wire_labels to the factory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))
            p.emergency_stop(
                "estop",
                tm_top="X3",
                tm_bot="X4",
                wire_labels=["BKWH1", "BKWH2"],
            )

            p.build_svgs(tmpdir)
            assert os.path.exists(os.path.join(tmpdir, "estop.svg"))


class TestEdgeCases:
    """Edge case and integration tests."""

    def test_empty_project_build(self):
        """Building a project with no circuits should succeed (just system CSV)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            p.build_svgs(tmpdir)
            # Only system CSV should be generated
            assert os.path.exists(os.path.join(tmpdir, "system_terminals.csv"))

    def test_circuit_def_dataclass_defaults(self):
        """_CircuitDef should have correct defaults."""
        from pyschemaelectrical.project import _CircuitDef

        cdef = _CircuitDef(key="test", factory="coil")
        assert cdef.count == 1
        assert cdef.wire_labels is None
        assert cdef.reuse_tags is None
        assert cdef.components is None
        assert cdef.builder_fn is None
        assert cdef.start_indices is None
        assert cdef.terminal_start_indices is None
        assert cdef.params == {}

    def test_page_def_dataclass_defaults(self):
        """_PageDef should have correct defaults."""
        from pyschemaelectrical.project import _PageDef

        pdef = _PageDef(page_type="schematic")
        assert pdef.title == ""
        assert pdef.circuit_key == ""
        assert pdef.md_path == ""
        assert pdef.notice is None
        assert pdef.csv_path == ""
        assert pdef.typst_content == ""

    def test_build_svgs_no_bridge_when_no_bridge_defs(self):
        """build_svgs should not call update_csv when no bridge defs exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Project()
            # Terminals without bridge
            p.terminals(Terminal("X3", "24V"), Terminal("X4", "GND"))
            p.emergency_stop("estop", tm_top="X3", tm_bot="X4")
            p.build_svgs(tmpdir)
            # Should succeed without issues
            assert os.path.exists(os.path.join(tmpdir, "system_terminals.csv"))


# =========================================================================
# Tests for plc_rack() and external_connections()
# =========================================================================


class TestPlcRack:
    """Tests for Project.plc_rack() and Project.external_connections()."""

    def _make_di_module(self):
        """Return a simple DI module for testing."""
        from pyschemaelectrical.plc_resolver import PlcModuleType

        return PlcModuleType(
            mpn="750-1405",
            signal_type="DI",
            channels=4,
            pins_per_channel=("",),
        )

    def test_plc_rack_stores_rack(self):
        """plc_rack() stores the rack on the project."""
        di_module = self._make_di_module()
        rack = [("DI1", di_module)]
        p = Project()
        p.plc_rack(rack)
        assert p._plc_rack == rack

    def test_plc_rack_returns_self(self):
        """plc_rack() returns self for method chaining."""
        p = Project()
        result = p.plc_rack([])
        assert result is p

    def test_plc_rack_default_is_none(self):
        """_plc_rack should default to None on a new Project."""
        p = Project()
        assert p._plc_rack is None

    def test_plc_rack_can_be_overwritten(self):
        """Calling plc_rack() twice should replace the previous rack."""
        di_module = self._make_di_module()
        rack1 = [("DI1", di_module)]
        rack2 = [("DI1", di_module), ("DI2", di_module)]
        p = Project()
        p.plc_rack(rack1)
        p.plc_rack(rack2)
        assert p._plc_rack == rack2

    def test_external_connections_stores(self):
        """external_connections() stores the connections."""
        p = Project()
        connections = [("SensorA", "Sig+", "X100", "1", "PLC:DI", "")]
        p.external_connections(connections)
        assert p._external_connections == connections

    def test_external_connections_returns_self(self):
        """external_connections() returns self for method chaining."""
        p = Project()
        result = p.external_connections([])
        assert result is p

    def test_external_connections_default_is_empty(self):
        """_external_connections should default to [] on a new Project."""
        p = Project()
        assert p._external_connections == []

    def test_external_connections_makes_copy(self):
        """external_connections() should copy the input list."""
        p = Project()
        original = [("SensorA", "Sig+", "X100", "1", "PLC:DI", "")]
        p.external_connections(original)
        original.append(("SensorB", "Sig+", "X100", "2", "PLC:DI", ""))
        # The project's list should NOT be affected by the mutation
        assert len(p._external_connections) == 1

    def test_plc_report_without_csv_path_accepted(self):
        """plc_report() with no csv_path is accepted when rack is configured."""
        p = Project()
        p.plc_rack([])
        p.plc_report()
        assert p._pages[-1].page_type == "plc_report"
        assert p._pages[-1].csv_path == ""

    def test_plc_report_returns_self(self):
        """plc_report() returns self for method chaining."""
        p = Project()
        result = p.plc_report()
        assert result is p

    def test_chaining(self):
        """plc_rack(), external_connections(), plc_report() can be chained."""
        di_module = self._make_di_module()
        p = (
            Project()
            .plc_rack([("DI1", di_module)])
            .external_connections([])
            .plc_report()
        )
        assert p._plc_rack is not None
        assert p._external_connections == []
        assert p._pages[-1].page_type == "plc_report"


class TestGeneratePlcCsv:
    """Tests for _generate_plc_csv and build() auto-generation integration."""

    def _make_rack(self):
        """Return a minimal DO rack for testing."""
        from pyschemaelectrical.plc_resolver import PlcModuleType

        do_module = PlcModuleType(
            mpn="750-1504",
            signal_type="DO",
            channels=4,
            pins_per_channel=("",),
        )
        return [("DO1", do_module)]

    def test_generate_plc_csv_creates_file(self):
        """_generate_plc_csv should create a CSV file at the given path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rack = self._make_rack()
            p = Project()
            p.plc_rack(rack)

            csv_path = os.path.join(tmpdir, "plc_connections.csv")
            p._generate_plc_csv(csv_path)

            assert os.path.exists(csv_path)

    def test_generate_plc_csv_has_header(self):
        """Generated PLC CSV should have the expected header row."""
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            rack = self._make_rack()
            p = Project()
            p.plc_rack(rack)

            csv_path = os.path.join(tmpdir, "plc_connections.csv")
            p._generate_plc_csv(csv_path)

            with open(csv_path, newline="") as f:
                reader = csv.reader(f)
                header = next(reader)

            assert header == [
                "Module",
                "MPN",
                "PLC Pin",
                "Component",
                "Pin",
                "Terminal",
            ]

    def test_build_auto_generates_plc_csv_when_rack_set(self):
        """build() should auto-generate plc_connections.csv when rack is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp")

            rack = self._make_rack()
            p = Project()
            p.plc_rack(rack)

            mock_typst_module = MagicMock()
            mock_compiler_inst = MagicMock()
            mock_typst_module.TypstCompiler.return_value = mock_compiler_inst
            mock_typst_module.TypstCompilerConfig = MagicMock()

            with patch.dict(
                "sys.modules",
                {"pyschemaelectrical.rendering.typst.compiler": mock_typst_module},
            ):
                p.build(output_pdf, temp_dir=temp_dir, keep_temp=True)

            plc_csv = os.path.join(temp_dir, "plc_connections.csv")
            assert os.path.exists(plc_csv)

    def test_build_passes_plc_csv_to_compiler_when_no_explicit_path(self):
        """build() should pass auto-generated CSV to add_plc_report when csv_path is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp")

            rack = self._make_rack()
            p = Project()
            p.plc_rack(rack)
            p.plc_report()  # no csv_path

            mock_typst_module = MagicMock()
            mock_compiler_inst = MagicMock()
            mock_typst_module.TypstCompiler.return_value = mock_compiler_inst
            mock_typst_module.TypstCompilerConfig = MagicMock()

            with patch.dict(
                "sys.modules",
                {"pyschemaelectrical.rendering.typst.compiler": mock_typst_module},
            ):
                p.build(output_pdf, temp_dir=temp_dir, keep_temp=True)

            mock_compiler_inst.add_plc_report.assert_called_once()
            call_arg = mock_compiler_inst.add_plc_report.call_args[0][0]
            assert "plc_connections.csv" in call_arg

    def test_build_explicit_csv_path_takes_priority(self):
        """When explicit csv_path is given it should override auto-generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = os.path.join(tmpdir, "output.pdf")
            temp_dir = os.path.join(tmpdir, "temp")

            # Create a dummy explicit CSV
            os.makedirs(temp_dir, exist_ok=True)
            explicit_csv = os.path.join(tmpdir, "explicit_plc.csv")
            with open(explicit_csv, "w") as f:
                f.write("dummy")

            rack = self._make_rack()
            p = Project()
            p.plc_rack(rack)
            p.plc_report(csv_path=explicit_csv)

            mock_typst_module = MagicMock()
            mock_compiler_inst = MagicMock()
            mock_typst_module.TypstCompiler.return_value = mock_compiler_inst
            mock_typst_module.TypstCompilerConfig = MagicMock()

            with patch.dict(
                "sys.modules",
                {"pyschemaelectrical.rendering.typst.compiler": mock_typst_module},
            ):
                p.build(output_pdf, temp_dir=temp_dir, keep_temp=True)

            mock_compiler_inst.add_plc_report.assert_called_once_with(explicit_csv)

    def test_add_page_to_compiler_plc_report_uses_plc_csv_path(self):
        """_add_page_to_compiler should use plc_csv_path when page has no csv_path."""
        from pyschemaelectrical.project import _PageDef

        p = Project()
        compiler = MagicMock()

        page_def = _PageDef(page_type="plc_report", csv_path="")
        p._add_page_to_compiler(
            compiler, page_def, {}, {}, "/tmp/system.csv", "/tmp/plc_auto.csv"
        )

        compiler.add_plc_report.assert_called_once_with("/tmp/plc_auto.csv")

    def test_add_page_to_compiler_plc_report_page_csv_overrides_auto(self):
        """_add_page_to_compiler should prefer page's csv_path over plc_csv_path."""
        from pyschemaelectrical.project import _PageDef

        p = Project()
        compiler = MagicMock()

        page_def = _PageDef(page_type="plc_report", csv_path="/explicit/path.csv")
        p._add_page_to_compiler(
            compiler, page_def, {}, {}, "/tmp/system.csv", "/tmp/plc_auto.csv"
        )

        compiler.add_plc_report.assert_called_once_with("/explicit/path.csv")
