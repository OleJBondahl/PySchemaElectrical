# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PySchemaElectrical is a Python library for programmatically generating IEC 60617-compliant electrical schematic diagrams as SVG files. It has **zero runtime dependencies** and targets Python 3.8+. Current version: 0.1.6 (Alpha).

## Library Philosophy

PySchemaElectrical takes a **data-first, code-as-schematic** approach to electrical documentation. Instead of drawing schematics in a GUI, engineers describe circuits as Python data structures and the library renders standards-compliant output.

The core insight: electrical schematics are **structured data** — components, connections, and layout rules — not freeform drawings. By treating them as data, we gain version control, parameterization, automation, and reproducibility for free.

### Core Principles

1. **Zero runtime dependencies** — The library must never add external dependencies. Everything needed for SVG generation is built-in. This ensures maximum portability and minimal install friction.

2. **Immutability by default** — All core data types (`Symbol`, `Port`, `Point`, `Vector`, `Element`, `Style`) are frozen dataclasses. Transformations always return new instances. The `Terminal` class achieves immutability via `__slots__` + `__setattr__` override on a `str` subclass.

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
def factory(state, x, y, tm_top, tm_bot, ...) -> Tuple[new_state, Circuit, used_terminals]
```

### Key Modules

- **`model/core.py`** — Frozen dataclasses: `Symbol`, `Port`, `Point`, `Vector`, `Element`, `Style`. Symbols are immutable; transformations return new instances.
- **`model/constants.py`** — `GRID_SIZE` (5mm), `StandardSpacing`, `StandardTags`, `StandardPins`, line widths, fonts.
- **`model/parts.py`** — Component part factories: `standard_text`, `box`, `terminal_circle`, `two_pole_factory`, `three_pole_factory`.
- **`symbols/`** — IEC symbol factory functions (terminals, contacts, coils, breakers, protection, motors, blocks, actuators, assemblies, references). Each returns a `Symbol`.
- **`system/system.py`** — `Circuit` container (mutable), `add_symbol`, `auto_connect_circuit`, `render_system`, `merge_circuits`.
- **`system/connection_registry.py`** — Immutable terminal-to-component connection tracking.
- **`std_circuits/`** — High-level circuit factories: `dol_starter`, `psu`, `changeover`, `power_distribution`, `spdt`, `no_contact`, `coil`, `emergency_stop`.
- **`builder.py`** — `CircuitBuilder` fluent API for constructing custom linear circuits.
- **`descriptors.py`** — Lightweight inline descriptors (`ref`, `comp`, `term`) for declarative circuit definition.
- **`terminal.py`** — First-class `Terminal` type (immutable `str` subclass with metadata).
- **`project.py`** — Multi-page project orchestration with title block and PDF compilation.
- **`layout/layout.py`** — `auto_connect` (wire between adjacent symbols), `create_horizontal_layout`.
- **`layout/wire_labels.py`** — Wire specification labels (color, size) on connection lines.
- **`utils/autonumbering.py`** — Functional state threading: `create_autonumberer`, `next_tag`, `next_terminal_pins`.
- **`utils/renderer.py`** — SVG rendering from elements.
- **`utils/transform.py`** — `translate`, `rotate` (pure, return new instances).
- **`rendering/typst/`** — Typst-based PDF compilation (frame generation, SVG-to-Typst conversion).

### Import Order Sensitivity

**WARNING**: The `__init__.py` files in this project have **deliberate import ordering** to avoid circular imports. Do NOT let auto-formatters (like `ruff` with I001) reorder these imports. Key files:

- `src/pyschemaelectrical/__init__.py` — `std_circuits` must be imported last
- `src/pyschemaelectrical/model/__init__.py` — `core` must be imported before `parts`
- `src/pyschemaelectrical/utils/__init__.py` — `utils` must be imported before `autonumbering`

These files use `# noqa: E402` and `# noqa: I001` comments to suppress linter warnings about import order.

### Design Principles to Follow

- **Immutability**: All `Symbol` objects are frozen dataclasses. Never mutate; always return new instances.
- **Functional state threading**: State is an explicit dict passed into and returned from functions. No global mutable state.
- **Pure core**: Functions should be deterministic. Side effects (file I/O) are pushed to boundaries (rendering).
- **Grid-based coordinates**: Base grid is 5mm (`GRID_SIZE`). Origin is top-left (0,0), Y increases downward. All coordinates are in mm.
- **Terminal sharing**: Multiple circuits can share the same terminal tag (e.g., "X1"). State ensures pin numbers auto-increment correctly across circuits.

### Testing

- Tests use **pytest** with **pytest-cov** for coverage.
- SVG **snapshot testing** via the `snapshot_svg` fixture in `tests/conftest.py` — compares generated SVG strings against stored `.svg` files in `tests/snapshots/`.
- Set `PYTEST_UPDATE_SNAPSHOTS=1` to update snapshots when rendering changes are intentional.
- pytest config is in `pyproject.toml` with `--verbose --cov=src --cov-report=term-missing` as default options.

### Type Checking

Run `uv run ty check` for type checking. Known diagnostic categories in the current codebase:

- **`possibly-unbound-attribute`** on `Terminal.__slots__` attributes — a limitation of ty with `str` subclasses using `__slots__` + `object.__setattr__` in `__new__`. These are false positives.
- **`invalid-argument-type`** on `Point` / `Style` used as `Element` — the type hierarchy uses structural compatibility that ty doesn't fully resolve.
- **`unresolved-attribute`** on dynamically resolved attributes — some attributes are set via `object.__setattr__` which ty cannot track.

### Source Layout

Source code lives under `src/pyschemaelectrical/` (src layout). The package dir mapping is `{"" = "src"}` in pyproject.toml. Public API is exported from `src/pyschemaelectrical/__init__.py`.
