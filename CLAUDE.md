# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PySchemaElectrical is a Python library for programmatically generating IEC 60617-compliant electrical schematic diagrams as SVG files. It has **zero runtime dependencies** and targets Python 3.8+. Current version: 0.1.6 (Alpha).

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

# code formatting and linting
uv run ruff check
uv run ruff format

# Run an example
python examples/example_dol_starter.py
```

## Architecture

### Two-Layer API Design

1. **High-Level API** (`std_circuits/`, `builder.py`): For library consumers. Creates complete circuits with automatic state management, autonumbering, layout, and connections.
2. **Low-Level API** (`model/`, `system/`, `symbols/`): For extending the library with new components. Direct manipulation of Symbols, Ports, and Circuits.

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
- **`layout/layout.py`** — `auto_connect` (wire between adjacent symbols), `create_horizontal_layout`.
- **`utils/autonumbering.py`** — Functional state threading: `create_autonumberer`, `next_tag`, `next_terminal_pins`.
- **`utils/renderer.py`** — SVG rendering from elements.
- **`utils/transform.py`** — `translate`, `rotate` (pure, return new instances).

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

### Source Layout

Source code lives under `src/pyschemaelectrical/` (src layout). The package dir mapping is `{"" = "src"}` in pyproject.toml. Public API is exported from `src/pyschemaelectrical/__init__.py`.
