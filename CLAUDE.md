# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Knowledge Graph (MCP Memory)

The memory server contains full API signatures for this library (`CircuitBuilder`, `std_circuits.*`, `TypstCompiler`, `BuildResult`, `GenerationState`, `Terminal`, `InternalDevice`, `Descriptors/Project API`, wire labels, export utilities) and the consumer project's config (terminals, devices, PLC rack, circuit functions, field devices). **Search memory before re-reading source files** — e.g. `mcp__memory__search_nodes("CircuitBuilder")` or `mcp__memory__search_nodes("BuildResult")`.

## Project Overview

PySchemaElectrical is a Python library for programmatically generating IEC 60617-compliant electrical schematic diagrams as SVG files. It has **zero runtime dependencies** and targets **Python 3.12+** (`requires-python = ">=3.12"` in `pyproject.toml`). Current version: 0.1.7 (Alpha).

## Library Philosophy

PySchemaElectrical takes a **data-first, code-as-schematic** approach to electrical documentation. Instead of drawing schematics in a GUI, engineers describe circuits as Python data structures and the library renders standards-compliant output.

The core insight: electrical schematics are **structured data** — components, connections, and layout rules — not freeform drawings. By treating them as data, we gain version control, parameterization, automation, and reproducibility for free.

### Core Principles

1. **Zero runtime dependencies** — The library must never add external dependencies. Everything needed for SVG generation is built-in. This ensures maximum portability and minimal install friction.

2. **Immutability by default** — All core data types (`Symbol`, `Port`, `Point`, `Vector`, `Element`, `Style`) are frozen dataclasses. Transformations always return new instances. The `Terminal` class (`terminal.py`) achieves immutability via `__slots__` + `__setattr__` override on a `str` subclass. **Exception:** `Circuit` (`system/system.py`) is intentionally mutable — it is an accumulator that collects symbols and connections during circuit construction.

3. **Functional state threading** — Autonumbering and other stateful operations use an explicit state dict that is passed into and returned from functions. There is no global mutable state. This makes circuits composable and testable in isolation.

4. **Convention over configuration** — Standard electrical conventions (IEC 60617 symbols, 5mm grid, standard spacing) are baked into sensible defaults. Users should be able to create correct schematics without configuring anything.

5. **Composition through factories** — Complex symbols are built by composing simpler factory functions (e.g., `three_pole_factory` composes three single-pole symbols). Circuits are built by composing circuit factories or using the builder pattern.

6. **Standards compliance** — Symbols follow IEC 60617 standards. Coordinate system uses mm with a 5mm grid. Output is valid SVG. Terminal numbering follows industry conventions.

## Build & Development Commands

```bash
# Install dependencies (uses uv)
uv sync

# Install in editable mode
uv pip install -e .

# Run all tests (with coverage)
pytest

# Run a single test file
pytest tests/unit/test_symbols.py

# Run a specific test
pytest tests/unit/test_symbols.py::test_function_name -v

# Update SVG snapshots after intentional rendering changes
$env:PYTEST_UPDATE_SNAPSHOTS="1"; pytest    # PowerShell
PYTEST_UPDATE_SNAPSHOTS=1 pytest            # bash

# Type checking
uv run ty check

# Code formatting and linting
uv run ruff check
uv run ruff format

# Run an example
python examples/example_dol_starter.py
```

## Architecture

### Three-Layer API Design

1. **Project API** (`project.py`): Top-level orchestration. Manages multi-page schematics, title blocks, and PDF compilation.
2. **Circuit API** (`std_circuits/`, `builder.py`, `descriptors.py`): For library consumers. Creates complete circuits with automatic state management, autonumbering, layout, and connections.
3. **Symbol API** (`model/`, `system/`, `symbols/`): For extending the library with new components. Direct manipulation of Symbols, Ports, and Circuits.

### Core Data Flow

```
State (autonumbering) → Symbol factories → Circuit container → Layout/wiring → SVG render
```

All standard circuit factories follow this signature pattern:
```python
def factory(
    state: dict[str, Any],
    x: float,
    y: float,
    tm_top: str,              # Top terminal ID
    tm_bot: str | list[str],  # Bottom terminal ID(s)
    count: int = 1,           # Number of instances
    wire_labels: list[str] | None = None,
    **kwargs,
) -> BuildResult:
```

`BuildResult` is a dataclass (`builder.py`) containing:

- `state` — updated state dict (passed to the next factory)
- `circuit` — the `Circuit` containing all symbols and connections
- `used_terminals` — list of terminal IDs consumed
- `component_map` — `dict[str, list[str]]` mapping tag prefixes to generated tag names (e.g., `{"K": ["K1", "K2"]}`)
- `terminal_pin_map` — `dict[str, list[str]]` mapping terminal IDs to consumed pin numbers

`BuildResult.__iter__` yields `(state, circuit, used_terminals)` for backward-compatible tuple unpacking.

### Key Modules

- **`model/core.py`** — Frozen dataclasses: `Symbol`, `Port`, `Point`, `Vector`, `Element`, `Style`. Symbols are immutable; transformations return new instances.
- **`model/constants.py`** — `GRID_SIZE` (5mm), `StandardSpacing`, `StandardTags`, `StandardPins`, `LayoutDefaults`, line widths, fonts.
- **`model/parts.py`** — Component part factories: `standard_text`, `box`, `terminal_circle`, `two_pole_factory`, `three_pole_factory`, `create_pin_label_text`.
- **`model/primitives.py`** — Geometric primitives: `Line`, `Circle`, `Text`, `Path`, `Group`, `Polygon`. All frozen dataclasses inheriting from `Element`.
- **`model/state.py`** — `GenerationState` dataclass and `create_initial_state()`. Provides typed state management (currently coexists with raw `dict[str, Any]` — see todo.md Q4).
- **`symbols/`** — IEC symbol factory functions (terminals, contacts, coils, breakers, protection, motors, blocks, transducers, assemblies, references). Each returns a `Symbol`.
- **`system/system.py`** — `Circuit` container (**mutable** — see "Intentional Mutable Builders"), `add_symbol`, `auto_connect_circuit`, `render_system`, `merge_circuits`.
- **`system/connection_registry.py`** — `TerminalRegistry` (frozen dataclass) for immutable terminal-to-component connection tracking. `register_connection()` returns a new registry.
- **`std_circuits/`** — High-level circuit factories: `dol_starter`, `psu`, `changeover`, `power_distribution`, `spdt`, `no_contact`, `coil`, `emergency_stop`. All return `BuildResult`.
- **`builder.py`** — `CircuitBuilder` fluent API for constructing custom linear circuits. Also defines `BuildResult`, `ComponentRef`, `PortRef`, `LayoutConfig`, `ComponentSpec`.
- **`descriptors.py`** — Lightweight inline descriptors (`ref`, `comp`, `term`) for declarative circuit definition via `build_from_descriptors()`.
- **`terminal.py`** — First-class `Terminal` type (immutable `str` subclass with metadata: `description`, `bridge`, `reference`, `pin_prefixes`).
- **`wire.py`** — `wire()` helper for creating wire specification label strings (shorthand for `format_wire_specification()`). Also provides `wire.EMPTY`.
- **`exceptions.py`** — Exception hierarchy (see section below).
- **`plc.py`** — `PlcMapper` for declaring PLC modules, sensor types, and generating PLC connection tables.
- **`project.py`** — Multi-page project orchestration with title block and PDF compilation via Typst.
- **`layout/layout.py`** — `auto_connect` (wire between adjacent symbols), `create_horizontal_layout`.
- **`layout/wire_labels.py`** — Wire specification labels (color, size) on connection lines.
- **`utils/autonumbering.py`** — Functional state threading: `create_autonumberer`, `next_tag`, `next_terminal_pins`.
- **`utils/renderer.py`** — SVG rendering from elements.
- **`utils/transform.py`** — `translate`, `rotate` (pure, return new instances).
- **`utils/export_utils.py`** — `export_terminal_list()` for CSV export, `merge_terminal_csv()` for post-processing.
- **`utils/terminal_bridges.py`** — Internal bridge/connection data for terminal blocks.
- **`field_devices.py`** — `PinDef`, `DeviceTemplate`, `generate_field_connections()` for field device wiring declarations.
- **`rendering/typst/`** — Typst-based PDF compilation (frame generation, SVG-to-Typst conversion).

### Import Order Sensitivity

**WARNING**: The `__init__.py` files in this project have **deliberate import ordering** to avoid circular imports. Do NOT let auto-formatters (like `ruff` with I001) reorder these imports. Key files:

- `src/pyschemaelectrical/__init__.py` — `std_circuits` must be imported last
- `src/pyschemaelectrical/model/__init__.py` — `core` must be imported before `parts`
- `src/pyschemaelectrical/utils/__init__.py` — `utils` must be imported before `autonumbering`

These files use `# noqa: E402` and `# noqa: I001` comments to suppress linter warnings about import order.

### Exception Hierarchy

All library exceptions are defined in `exceptions.py`:

```text
Exception
└── CircuitValidationError          — base for all validation errors
    ├── PortNotFoundError            — bad port ID on a component
    ├── ComponentNotFoundError       — component index out of bounds
    ├── TagReuseError                — reuse_tags ran out of source tags
    ├── TerminalReuseError           — reuse_terminals ran out of source pins
    └── WireLabelMismatchError       — wire label count ≠ vertical wire count
```

**Backward compatibility:** The old names (`TagReuseExhausted`, `TerminalReuseExhausted`, `WireLabelCountMismatch`) are kept as aliases in `exceptions.py` and will continue to work in `except` clauses. Prefer the new `*Error` names in new code.

When adding new exceptions, inherit from `CircuitValidationError` and include enough context (component tag, available options) to help users diagnose the issue.

### Name Collision Warning: `Terminal`

Two classes are related to the name `Terminal`:

1. **`terminal.py:Terminal(str)`** — The primary `Terminal` type. An immutable `str` subclass carrying metadata (`description`, `bridge`, `reference`, `pin_prefixes`). This is what users import and use.
2. **`symbols/terminals.py:TerminalSymbol(Symbol)`** — A frozen dataclass representing a rendered terminal *symbol*. Internal to the symbols layer. (Renamed from `Terminal` to `TerminalSymbol` to eliminate the collision. The old name `Terminal` is kept as a deprecated alias in `symbols/terminals.py`.)

The public API exports only (1). The rename to `TerminalSymbol` resolves the previous shadowing issue, but be aware of the deprecated alias if maintaining older code.

### Port ID Conventions

Port IDs on symbols are **not** standardized across the codebase — they follow the relevant IEC convention for each component type:

- **Numeric sequential**: Simple contacts → `"1"`, `"2"`
- **IEC standard non-sequential**: SPDT contacts → `"1"` (common), `"2"` (NC), `"4"` (NO)
- **Semantic**: Motors → `"U"`, `"V"`, `"W"`, `"PE"`; Coils → `"A1"`, `"A2"`
- **Composite (multi-pole)**: Three-pole SPDT → `"1_com"`, `"1_nc"`, `"1_no"`, `"2_com"`, ...

When creating new symbols, choose port IDs that match the IEC designation for that component. Port IDs must be unique within a single symbol.

### Design Principles to Follow

- **Immutability**: All `Symbol` objects are frozen dataclasses. Never mutate; always return new instances. Four top-level builder classes (`Circuit`, `Project`, `CircuitBuilder`, `PlcMapper`) are intentionally mutable — see the "Intentional Mutable Builders" section below.
- **Functional state threading**: State is an explicit `dict[str, Any]` passed into and returned from functions. No global mutable state. (A `GenerationState` dataclass exists for typed access but currently coexists with the dict form — see `todo.md` Q4.)
- **Pure core**: Functions should be deterministic. Side effects (file I/O) are pushed to boundaries (rendering).
- **Grid-based coordinates**: Base grid is 5mm (`GRID_SIZE`). Origin is top-left (0,0), Y increases downward. All coordinates are in mm.
- **Terminal sharing**: Multiple circuits can share the same terminal tag (e.g., "X1"). State ensures pin numbers auto-increment correctly across circuits.

### Intentional Mutable Builders

While the library follows immutable/functional patterns at its core, four top-level classes use mutable builder patterns intentionally:

| Class | Location | Purpose |
| --- | --- | --- |
| `Circuit` | `system/system.py` | Mutable accumulator for symbols and elements during circuit construction |
| `Project` | `project.py` | Mutable builder for multi-page project definitions (pages, title block, metadata) |
| `CircuitBuilder` | `builder.py` | Mutable fluent builder for circuit specifications (components, layout, wiring) |
| `PlcMapper` | `plc.py` | Mutable builder for PLC module/sensor definitions and connection table generation |

These are the highest-level imperative API classes. The rest of the library follows functional/immutable patterns.

**Warning:** Do not share builder instances across multiple build contexts. Each builder accumulates state for a single output (one circuit, one project, one PLC mapping). Create a fresh instance for each independent build.

### Testing

- Tests use **pytest** with **pytest-cov** for coverage.
- SVG **snapshot testing** via the `snapshot_svg` fixture in `tests/conftest.py` — compares generated SVG strings against stored `.svg` files in `tests/snapshots/`.
- Set `PYTEST_UPDATE_SNAPSHOTS=1` to update snapshots when rendering changes are intentional.
- pytest config is in `pyproject.toml` with `--verbose --cov=src --cov-report=term-missing` as default options.
- **Current baseline**: 948 tests, 97% line coverage, all passing.
- When changing symbol rendering or layout, always run `pytest` and check snapshot diffs.

### Type Checking

Run `uv run ty check` for type checking. Known diagnostic categories in the current codebase:

- **`possibly-unbound-attribute`** on `Terminal.__slots__` attributes — a limitation of ty with `str` subclasses using `__slots__` + `object.__setattr__` in `__new__`. These are false positives.
- **`invalid-argument-type`** on `Point` / `Style` used as `Element` — the type hierarchy uses structural compatibility that ty doesn't fully resolve.
- **`unresolved-attribute`** on dynamically resolved attributes — some attributes are set via `object.__setattr__` which ty cannot track.

Current baseline: ~54 diagnostics. When fixing type issues, verify the count decreases.

### Linting

Run `uv run ruff check` for linting (configured in `pyproject.toml`). Key settings:

- Line length: 88 (same as Black)
- Target: Python 3.12
- Selected rules: E, W, F, I, C, B
- `__init__.py` files suppress F401 (unused imports — they are re-exports)
- `rendering/typst/compiler.py` suppresses E501 (inline Typst template strings)

Current baseline with default rules: ~85 issues (61 E501 line-too-long in test/source files, 17 I001 intentional import order in `__init__.py` files, 0 C901 complexity — all suppressed or extracted).

### Source Layout

Source code lives under `src/pyschemaelectrical/` (src layout). The package dir mapping is `{"" = "src"}` in pyproject.toml. Public API is exported from `src/pyschemaelectrical/__init__.py`.

### Consumer Project Reference

The sibling project `auxillary_cabinet_v3` (located at `../auxillary_cabinet_v3/`) is the primary real-world consumer of this library. It contains 14 Python modules generating a complete auxiliary cabinet schematic. Analysis of its usage patterns informed several `todo.md` tasks (Section 11). Key patterns found there:

- `DeviceTemplate` / `PinDef` system for field device connections
- CSV merge/sort post-processing for terminal lists
- PLC module/rack/channel auto-assignment
- String-based tag generators (e.g., `tag_generators={"K": lambda s: (s, "K1")}`)
- Workarounds like `_find_symbol_by_label()` and `hasattr(e, "ports")` iteration (indicating missing API surface)

### Task Tracking

See `todo.md` for the complete audit-driven task list. It contains:

- **Section 0**: Questions requiring maintainer input (blocking some tasks)
- **Sections 1–16**: Active tasks grouped by category with effort estimates
- **Section 17**: Archived completed items
- **Summary table**: Tasks prioritized into Tiers 1–5

### Agent Git Workflow

- After completing each self-contained task, commit using the `commit-commands:commit` skill
- This ensures changes are reversible and the working tree stays clean between tasks
- Use git worktrees (via `superpowers:using-git-worktrees` skill) when starting work that may conflict with another running agent session

### Working with Subagents (Task Tool)

When using the Task tool to launch subagents for research or code work:

- **Subagent results are returned inline** in the tool response when the agent completes, NOT written to the output file. The `output_file` path is only useful for checking progress on *still-running* background agents via `Read` or `tail`. Once the agent finishes, the full result is in the `TaskOutput` response.
- **To retrieve completed results**, use `TaskOutput` with `block=true` to wait for completion. The result text is returned directly.
- **To resume an agent** for follow-up questions, use the `resume` parameter with the agent's ID. The agent retains full context from its previous run.
- **Launch independent agents in parallel** by putting multiple Task tool calls in a single message. This is much faster than sequential launches.
- **Keep prompts self-contained** — each new agent starts with zero context about the codebase. Include file paths, module names, and what specifically to investigate. Reference the project root as `c:\Users\OleJohanBondahl\Documents\GitHub_ZEN\PySchemaElectrical\`.
- **Use the right agent type** for the job:
  - `Explore` — fast read-only codebase searches (Glob, Grep, Read). Best for audits and investigations.
  - `general-purpose` — can run Bash commands (pytest, ruff, etc.) in addition to reading files. Use for tasks that need command output.
  - `Bash` — pure command execution. Use for git operations, running tests, building.
- **Prefer `run_in_background: true`** when launching multiple agents, so they run concurrently. Then collect results with `TaskOutput` afterward.
- **Do NOT edit code in audit/research agents** — if the task is investigation-only, explicitly state "DO NOT edit any files. Only read and search." in the prompt to prevent accidental modifications.
