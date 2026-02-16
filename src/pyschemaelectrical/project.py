"""
Project class — Layer 0 declarative API for PySchemaElectrical.

The Project is the top-level object that owns state, terminal registry,
circuit definitions, page layout, and output configuration. Users interact
with it declaratively to define an entire schematic drawing set and compile
it to a multi-page PDF.
"""

import os
import shutil
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from pyschemaelectrical.builder import BuildResult
from pyschemaelectrical.descriptors import Descriptor, build_from_descriptors
from pyschemaelectrical.system.connection_registry import (
    export_registry_to_csv,
    get_registry,
)
from pyschemaelectrical.system.system import render_system
from pyschemaelectrical.terminal import Terminal
from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.utils.export_utils import export_terminal_list
from pyschemaelectrical.utils.terminal_bridges import (
    update_csv_with_internal_connections,
)

# ---------------------------------------------------------------------------
# Internal data structures
# ---------------------------------------------------------------------------


@dataclass
class _CircuitDef:
    """Internal deferred circuit definition."""

    key: str
    factory: str  # "dol_starter", "psu", "changeover", etc. or "descriptors" / "custom"
    params: Dict[str, Any] = field(default_factory=dict)
    count: int = 1
    wire_labels: Optional[List[str]] = None
    reuse_tags: Optional[Dict[str, str]] = None  # maps prefix -> circuit key
    components: Optional[List[Descriptor]] = None
    builder_fn: Optional[Callable] = None
    start_indices: Optional[Dict[str, int]] = None
    terminal_start_indices: Optional[Dict[str, int]] = None


@dataclass
class _PageDef:
    """Internal page definition."""

    page_type: str  # "schematic", "front", "terminal_report", "plc_report", "custom"
    title: str = ""
    circuit_key: str = ""
    md_path: str = ""
    notice: Optional[str] = None
    csv_path: str = ""
    typst_content: str = ""


# ---------------------------------------------------------------------------
# Project class
# ---------------------------------------------------------------------------


class Project:
    """
    Declarative project definition for electrical schematic drawing sets.

    Example::

        project = Project(
            title="My Schematics",
            drawing_number="DWG-001",
            author="Engineer",
            project="Project Name",
        )
        project.terminals(
            Terminal("X1", "Main Power"),
            Terminal("X3", "Fused 24V", bridge="all"),
            Terminal("X4", "Ground", bridge="all"),
        )
        project.dol_starter("motors", count=3, tm_top="X1",
                            tm_bot=["X10","X11","X12"], tm_bot_right="X4")
        project.page("Motor Circuits", "motors")
        project.terminal_report()
        project.build("output.pdf")

    Args:
        title: Drawing title (appears in title block).
        drawing_number: Drawing number (appears in title block).
        author: Author name.
        project: Project name.
        revision: Revision string (e.g. "00", "A1").
        logo: Path to logo image file (optional).
        font: Font family for all text output.
    """

    def __init__(
        self,
        title: str = "",
        drawing_number: str = "",
        author: str = "",
        project: str = "",
        revision: str = "00",
        logo: Optional[str] = None,
        font: str = "Times New Roman",
    ):
        self.title = title
        self.drawing_number = drawing_number
        self.author = author
        self.project = project
        self.revision = revision
        self.logo = logo
        self.font = font

        self._state = create_autonumberer()
        self._terminals: Dict[str, Terminal] = {}
        self._circuit_defs: List[_CircuitDef] = []
        self._pages: List[_PageDef] = []
        self._results: Dict[str, BuildResult] = {}

    # ------------------------------------------------------------------
    # Terminal registration
    # ------------------------------------------------------------------

    def terminals(self, *terminals: Terminal):
        """
        Register terminal block definitions for this project.

        Terminals carry metadata (description, bridge info, reference flag)
        used for reports and auto-generation.
        """
        for t in terminals:
            self._terminals[str(t)] = t

    def set_pin_start(self, terminal_id: str, pin: int):
        """
        Seed the pin counter for a terminal so auto-allocation starts at *pin*.
        """
        counters = self._state.get("terminal_counters", {})
        counters[terminal_id] = pin
        self._state["terminal_counters"] = counters

    # ------------------------------------------------------------------
    # Standard circuit registration
    # ------------------------------------------------------------------

    def dol_starter(self, key: str, count: int = 1, **kwargs):
        """Register a DOL starter circuit."""
        self._add_std_circuit(key, "dol_starter", count, **kwargs)

    def psu(self, key: str, count: int = 1, **kwargs):
        """Register a PSU circuit."""
        self._add_std_circuit(key, "psu", count, **kwargs)

    def changeover(self, key: str, count: int = 1, **kwargs):
        """Register a changeover circuit."""
        self._add_std_circuit(key, "changeover", count, **kwargs)

    def spdt(self, key: str, count: int = 1, **kwargs):
        """Register an SPDT relay circuit."""
        self._add_std_circuit(key, "spdt", count, **kwargs)

    def coil(self, key: str, count: int = 1, **kwargs):
        """Register a coil circuit."""
        self._add_std_circuit(key, "coil", count, **kwargs)

    def emergency_stop(self, key: str, count: int = 1, **kwargs):
        """Register an emergency stop circuit."""
        self._add_std_circuit(key, "emergency_stop", count, **kwargs)

    def no_contact(self, key: str, count: int = 1, **kwargs):
        """Register a normally-open contact circuit."""
        self._add_std_circuit(key, "no_contact", count, **kwargs)

    # ------------------------------------------------------------------
    # Custom circuit registration
    # ------------------------------------------------------------------

    def circuit(
        self,
        key: str,
        components: List[Descriptor],
        count: int = 1,
        wire_labels: Optional[List[str]] = None,
        reuse_tags: Optional[Dict[str, str]] = None,
        start_indices: Optional[Dict[str, int]] = None,
        terminal_start_indices: Optional[Dict[str, int]] = None,
        **kwargs,
    ):
        """
        Register a custom inline circuit from descriptors.

        Args:
            key: Unique circuit identifier.
            components: List of ref(), comp(), term() descriptors.
            count: Number of instances.
            wire_labels: Wire label strings.
            reuse_tags: Maps tag prefix to source circuit key.
            start_indices: Override tag counters.
            terminal_start_indices: Override terminal pin counters.
        """
        self._circuit_defs.append(
            _CircuitDef(
                key=key,
                factory="descriptors",
                count=count,
                wire_labels=wire_labels,
                reuse_tags=reuse_tags,
                components=components,
                params=kwargs,
                start_indices=start_indices,
                terminal_start_indices=terminal_start_indices,
            )
        )

    def custom(self, key: str, builder_fn: Callable, count: int = 1, **kwargs):
        """
        Register a custom circuit built via a builder function.

        The function receives ``(state, **kwargs)`` and must return
        a ``BuildResult`` (or a tuple ``(state, circuit, used_terminals)``).
        """
        self._circuit_defs.append(
            _CircuitDef(
                key=key,
                factory="custom",
                count=count,
                builder_fn=builder_fn,
                params=kwargs,
            )
        )

    # ------------------------------------------------------------------
    # Page management
    # ------------------------------------------------------------------

    def page(self, title: str, circuit_key: str):
        """Add a schematic page to the PDF output."""
        self._pages.append(
            _PageDef(page_type="schematic", title=title, circuit_key=circuit_key)
        )

    def front_page(self, md_path: str, notice: Optional[str] = None):
        """Add a front page from a Markdown file."""
        self._pages.append(_PageDef(page_type="front", md_path=md_path, notice=notice))

    def terminal_report(self):
        """Add an auto-generated system terminal report page."""
        self._pages.append(_PageDef(page_type="terminal_report"))

    def plc_report(self, csv_path: str = ""):
        """Add a PLC connections report page."""
        self._pages.append(_PageDef(page_type="plc_report", csv_path=csv_path))

    def custom_page(self, title: str, typst_content: str):
        """Add a page with raw Typst content."""
        self._pages.append(
            _PageDef(page_type="custom", title=title, typst_content=typst_content)
        )

    # ------------------------------------------------------------------
    # Build pipeline
    # ------------------------------------------------------------------

    def build(
        self,
        output: str,
        temp_dir: str = "temp",
        keep_temp: bool = False,
    ):
        """
        Build all circuits and compile the PDF.

        Steps:
        1. Build all registered circuits (respecting dependencies).
        2. Generate SVG for each circuit.
        3. Generate per-circuit terminal CSV.
        4. Generate system terminal CSV with bridge info.
        5. Assemble and compile Typst → PDF.

        Args:
            output: Path for the output PDF file.
            temp_dir: Directory for intermediate files.
            keep_temp: If True, keep intermediate files after compilation.
        """
        from pyschemaelectrical.rendering.typst.compiler import (
            TypstCompiler,
            TypstCompilerConfig,
        )

        os.makedirs(temp_dir, exist_ok=True)

        # 1. Build all circuits
        self._build_all_circuits()

        # 2. Generate SVGs and terminal CSVs
        svg_paths = {}
        csv_paths = {}
        all_used_terminals = []

        for key, result in self._results.items():
            svg_path = os.path.join(temp_dir, f"{key}.svg")
            render_system(result.circuit, svg_path)
            svg_paths[key] = svg_path

            if result.used_terminals:
                csv_path = os.path.join(temp_dir, f"{key}_terminals.csv")
                export_terminal_list(csv_path, result.used_terminals)
                csv_paths[key] = csv_path
                all_used_terminals.extend(result.used_terminals)

        # 3. Generate system terminal CSV with bridge info
        system_csv_path = os.path.join(temp_dir, "system_terminals.csv")
        registry = get_registry(self._state)
        export_registry_to_csv(registry, system_csv_path)

        # Add bridge info from registered terminals
        bridge_defs = {}
        for tid, t in self._terminals.items():
            if t.bridge and not t.reference:
                bridge_defs[tid] = t.bridge
        if bridge_defs:
            update_csv_with_internal_connections(system_csv_path, bridge_defs)

        # 4. Assemble Typst document
        # Use CWD as root so all relative paths (SVGs, CSVs) resolve correctly
        root_dir = os.getcwd()
        config = TypstCompilerConfig(
            drawing_name=self.title,
            drawing_number=self.drawing_number,
            author=self.author,
            project=self.project,
            revision=self.revision,
            logo_path=os.path.abspath(self.logo) if self.logo else None,
            font_family=self.font,
            root_dir=root_dir,
            temp_dir=os.path.relpath(os.path.abspath(temp_dir), root_dir),
        )
        compiler = TypstCompiler(config)

        # Add pages
        for page_def in self._pages:
            self._add_page_to_compiler(
                compiler, page_def, svg_paths, csv_paths, system_csv_path
            )

        # 5. Compile
        compiler.compile(output)
        print(f"PDF compiled: {output}")

        # Cleanup
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Build SVGs only (no PDF, no typst dependency)
    # ------------------------------------------------------------------

    def build_svgs(self, output_dir: str = "output"):
        """
        Build all circuits and export SVGs (no PDF compilation).

        Useful when the ``typst`` package is not installed.

        Args:
            output_dir: Directory for output SVG and CSV files.
        """
        os.makedirs(output_dir, exist_ok=True)
        self._build_all_circuits()

        for key, result in self._results.items():
            svg_path = os.path.join(output_dir, f"{key}.svg")
            render_system(result.circuit, svg_path)

            if result.used_terminals:
                csv_path = os.path.join(output_dir, f"{key}_terminals.csv")
                export_terminal_list(csv_path, result.used_terminals)

        # System terminal CSV
        system_csv_path = os.path.join(output_dir, "system_terminals.csv")
        registry = get_registry(self._state)
        export_registry_to_csv(registry, system_csv_path)

        bridge_defs = {}
        for tid, t in self._terminals.items():
            if t.bridge and not t.reference:
                bridge_defs[tid] = t.bridge
        if bridge_defs:
            update_csv_with_internal_connections(system_csv_path, bridge_defs)

        print(f"SVGs and CSVs written to: {output_dir}")

    # ------------------------------------------------------------------
    # Internal: circuit building
    # ------------------------------------------------------------------

    def _build_all_circuits(self):
        """Build all registered circuits in order."""
        self._results = {}
        for cdef in self._circuit_defs:
            result = self._build_one_circuit(cdef)
            self._results[cdef.key] = result
            self._state = result.state

    def _build_one_circuit(self, cdef: _CircuitDef) -> BuildResult:
        """Build a single circuit definition."""
        # Resolve reuse_tags: map circuit key → BuildResult
        resolved_reuse = None
        if cdef.reuse_tags:
            resolved_reuse = {}
            for prefix, source_key in cdef.reuse_tags.items():
                if source_key not in self._results:
                    raise ValueError(
                        f"Circuit '{cdef.key}' references '{source_key}' via "
                        f"reuse_tags, but it hasn't been built yet. "
                        f"Register '{source_key}' before '{cdef.key}'."
                    )
                resolved_reuse[prefix] = self._results[source_key]

        if cdef.factory == "descriptors":
            return self._build_descriptor_circuit(cdef, resolved_reuse)
        elif cdef.factory == "custom":
            return self._build_custom_circuit(cdef)
        else:
            return self._build_std_circuit(cdef, resolved_reuse)

    def _build_std_circuit(
        self, cdef: _CircuitDef, resolved_reuse: Optional[Dict]
    ) -> BuildResult:
        """Build a standard circuit (dol_starter, psu, etc.)."""
        from pyschemaelectrical import std_circuits

        factory_fn = getattr(std_circuits, cdef.factory)

        # Build kwargs from params
        kwargs = dict(cdef.params)
        kwargs["count"] = cdef.count
        if cdef.wire_labels:
            kwargs["wire_labels"] = cdef.wire_labels

        # Standard circuits use positional x, y — default to 0, 0
        x = kwargs.pop("x", 0.0)
        y = kwargs.pop("y", 0.0)

        # Standard circuits need terminal IDs as positional args
        # The caller passes them via kwargs with standard names
        state, circuit, used_terminals = factory_fn(self._state, x, y, **kwargs)

        return BuildResult(
            state=state,
            circuit=circuit,
            used_terminals=used_terminals,
        )

    def _build_descriptor_circuit(
        self, cdef: _CircuitDef, resolved_reuse: Optional[Dict]
    ) -> BuildResult:
        """Build a circuit from inline descriptors."""
        return build_from_descriptors(
            self._state,
            cdef.components,
            x=cdef.params.get("x", 0.0),
            y=cdef.params.get("y", 0.0),
            spacing=cdef.params.get("spacing", 80.0),
            count=cdef.count,
            wire_labels=cdef.wire_labels,
            reuse_tags=resolved_reuse,
            start_indices=cdef.start_indices,
            terminal_start_indices=cdef.terminal_start_indices,
        )

    def _build_custom_circuit(self, cdef: _CircuitDef) -> BuildResult:
        """Build a circuit via user-provided builder function."""
        result = cdef.builder_fn(self._state, **cdef.params)
        if isinstance(result, BuildResult):
            return result
        # Support tuple return: (state, circuit, used_terminals)
        state, circuit, used_terminals = result
        return BuildResult(
            state=state,
            circuit=circuit,
            used_terminals=used_terminals,
        )

    def _add_std_circuit(self, key: str, factory: str, count: int, **kwargs):
        """Register a standard circuit definition."""
        wire_labels = kwargs.pop("wire_labels", None)
        reuse_tags = kwargs.pop("reuse_tags", None)
        self._circuit_defs.append(
            _CircuitDef(
                key=key,
                factory=factory,
                count=count,
                wire_labels=wire_labels,
                reuse_tags=reuse_tags,
                params=kwargs,
            )
        )

    # ------------------------------------------------------------------
    # Internal: page compilation
    # ------------------------------------------------------------------

    def _add_page_to_compiler(
        self,
        compiler: Any,
        page_def: _PageDef,
        svg_paths: Dict[str, str],
        csv_paths: Dict[str, str],
        system_csv_path: str,
    ):
        """Add a page definition to the TypstCompiler."""
        if page_def.page_type == "schematic":
            key = page_def.circuit_key
            svg_path = svg_paths.get(key, "")
            csv_path = csv_paths.get(key)
            if svg_path:
                compiler.add_schematic_page(page_def.title, svg_path, csv_path)
        elif page_def.page_type == "front":
            compiler.add_front_page(page_def.md_path, notice=page_def.notice)
        elif page_def.page_type == "terminal_report":
            descriptions = {
                str(t): t.description
                for t in self._terminals.values()
                if not t.reference
            }
            compiler.add_terminal_report(system_csv_path, descriptions)
        elif page_def.page_type == "plc_report":
            csv_path = page_def.csv_path
            if csv_path:
                compiler.add_plc_report(csv_path)
        elif page_def.page_type == "custom":
            compiler.add_custom_page(page_def.title, page_def.typst_content)
