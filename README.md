# PySchemaElectrical

**PySchemaElectrical** is a Python library for programmatically generating IEC 60617 compliant electrical schematics. It emphasizes specific architectural principles (functional, data-oriented) to create deterministic, reproducible, and beautiful SVG drawings.

> [!NOTE]
> **Status:** Alpha. The API and functionality are subject to change.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [User API (High-Level)](#user-api-high-level)
    - [Standard Circuits](#standard-circuits)
    - [Symbols](#symbols)
    - [CircuitBuilder](#circuitbuilder)
- [Developer API (Low-Level)](#developer-api-low-level)
- [Design Principles](#design-principles)
- [Examples](#examples)

## Installation

This project is managed using [`uv`](https://github.com/astral-sh/uv), a fast Python package installer and resolver.

### Using `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/OleJBondahl/PySchemaElectrical.git
cd PySchemaElectrical

# Create a virtual environment and sync dependencies
uv sync

# Install the project in editable mode
uv pip install -e .
```

### Using standard pip

```bash
pip install -e .
```

## Packaging

To build and publish the package, use `uv`:

1.  **Build**: Creates source distribution and wheel in `dist/`.
    ```bash
    uv build
    ```

2.  **Publish**: Uploads to PyPI (requires API token).
    ```bash
    uv publish
    ```

See [PACKAGING.md](docs/PACKAGING.md) for detailed release instructions.

## Quick Start

The fastest way to generate a schematic is using the **Standard Circuits** library.

```python
from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.std_circuits import dol_starter
from pyschemaelectrical.system import render_system

# 1. Initialize State (for autonumbering)
state = create_autonumberer()

# 2. visual settings
# You should define terminal constants in your project
INPUT_TERM = "X1"
OUTPUT_TERM = "X2"

# 3. Create a DOL Starter Circuit
state, circuit, used_terminals = dol_starter(
    state=state,
    x=0, 
    y=0,
    tm_top=INPUT_TERM,
    tm_bot=OUTPUT_TERM
)

# 4. Render to SVG
# Saves 'output_circuit.svg' in the current directory
render_system(circuit, "output_circuit.svg")
```

## Architecture Overview

The library is split into two primary layers:

1.  **High-Level API (`builder`, `std_circuits`)**: Intended for consumers of the library. Focuses on "what" to build (e.g., "a motor starter at x=0"). Handles state management, layout, and connections automatically.
2.  **Low-Level API (`model`, `system`)**: Intended for library developers or agents creating new components. Focuses on "how" to build (e.g., "place symbol S at 10,10", "connect Port A to Port B").

## User API (High-Level)

### Standard Circuits

Located in `pyschemaelectrical.std_circuits`, these generic factories produce complete, ready-to-use sub-circuits. Standard circuits handle state management, autonumbering, and connections automatically.

| Circuit Type | Function Name | Description | Example File |
| :--- | :--- | :--- | :--- |
| **Motor** | `dol_starter` | Direct-On-Line Motor Starter (Breaker, Contactor, Thermal, Terminals) | `examples/example_dol_starter.py` |
| **Power** | `psu` | AC/DC Power Supply Unit (Input Terminals, PSU Block, Output Terminals) | `examples/example_psu.py` |
| | `changeover` | 3-Pole Manual Changeover Switch (Main/Backup Inputs, Switch, Output) | `examples/example_changeover.py` |
| | `power_distribution` | Complete System: Changeover + Voltage Monitor + PSU | `examples/example_power_distribution.py` |
| **Control** | `spdt` | SPDT Control Circuit (Coil + Inverted Link + Double Output Terminals) | `examples/example_motor_control.py` |
| | `no_contact` | Simple Normally Open Switch Circuit | `examples/example_switch.py` |
| | `coil` | Simple Coil Circuit (used for Relays, Voltage Monitors) | `examples/example_voltage_monitor.py` |
| **Safety** | `emergency_stop` | Single-Pole Emergency Stop Circuit | `examples/example_emergency_stop.py` |

**Usage Pattern:**
```python
from pyschemaelectrical.std_circuits import dol_starter

(next_state, circuit, used_terminals) = dol_starter(
    state=current_state, 
    x=0, y=0, 
    tm_top="X1", 
    tm_bot="X2", 
    ...params
)
```

### Symbols

Located in `pyschemaelectrical.symbols`, these are the fundamental graphical building blocks. They return `Symbol` objects (immutable dataclasses) and are used by `CircuitBuilder` or `std_circuits`.

| Category | Symbol Function | Description |
| :--- | :--- | :--- |
| **Terminals** | `terminal_symbol` | IEC 60617 Single Pole Terminal |
| | `three_pole_terminal_symbol` | 3-Pole Terminal Block |
| **Contacts** | `normally_open_symbol` | Single Pole Normally Open (NO) |
| | `normally_closed_symbol` | Single Pole Normally Closed (NC) |
| | `spdt_contact_symbol` | Single Pole Double Throw (Changeover) |
| | `three_pole_normally_open_symbol` | 3-Pole NO Contactor/Switch |
| | `three_pole_normally_closed_symbol` | 3-Pole NC Contactor/Switch |
| | `three_pole_spdt_symbol` | 3-Pole Changeover Switch |
| **Coils** | `coil_symbol` | IEC 60617 Coil (Square) |
| **Protection** | `circuit_breaker_symbol` | Single Pole Circuit Breaker |
| | `three_pole_circuit_breaker_symbol` | 3-Pole Circuit Breaker |
| | `thermal_overload_symbol` | Single Pole Thermal Overload |
| | `three_pole_thermal_overload_symbol` | 3-Pole Thermal Overload |
| | `fuse_symbol` | Standard Fuse |
| **Assemblies** | `contactor_symbol` | Contactor Assembly (Coil + 3-Pole Contact + Linkage) |
| | `emergency_stop_assembly_symbol`| E-Stop Assembly (NC Contact + Mushroom Button + Linkage) |
| | `current_transducer_assembly_symbol` | Current Transducer on Wire |
| **Blocks** | `psu_symbol` | Power Supply Unit (AC/DC) |
| | `terminal_box_symbol` | Generic Terminal Box |
| | `dynamic_block_symbol` | Dynamic Block with configurable pins |
| **Actuators** | `emergency_stop_button_symbol` | Mushroom Head Button Graphics |

### CircuitBuilder

Located in `pyschemaelectrical.builder`, the `CircuitBuilder` class provides a fluent interface for constructing custom linear circuits using the symbols listed above.

## Developer API (Low-Level)

This API is for agents or developers extending the library or building complex, non-standard layouts.

### Core Models

*   **`Symbol`**: A frozen dataclass representing a graphical component. It contains `Element` primitives (lines, circles) and `Port` connection points.
*   **`Circuit`**: A container for a collection of symbols and connections.
*   **`Port`**: A connection point on a symbol with coordinates and a direction.

### Autonumbering State

The library works on a **functional state-threading** model.
- `state`: A dictionary explicitly passed into and returned from functions.
- **Never modify global state.**
- Use helper functions:
    - `next_tag(state, "K")` -> `(new_state, "K1")`
    - `next_terminal_pins(state, "X1", 3)` -> `(new_state, ("1", "2", "3"))`

### Manual Layout

For precise control, you manipulate the `Circuit` object directly.

```python
from pyschemaelectrical.system.system import Circuit, add_symbol, auto_connect_circuit
from pyschemaelectrical.symbols.contacts import normally_open_symbol

c = Circuit()

# 1. Place Symbols manually
s1 = normally_open_symbol("S1")
add_symbol(c, s1, x=50, y=50)

s2 = normally_open_symbol("S2")
add_symbol(c, s2, x=50, y=100) # 50mm below

# 2. Connect
# Option A: Automatic (connects based on proximity/alignment)
auto_connect_circuit(c)

# Option B: Manual (via registry)
# register_connection(state, "S1", "2", "S2", "3", side="bottom")
```

## Design Principles

1.  **Immutability**: All Symbols are immutable. Transformations (move, rotate) return *new* instances.
2.  **Pure Core**: Functions should be deterministic. Side effects (like I/O) are pushed to the boundary (rendering).
3.  **Coordinate System**:
    - **Grid**: 5mm (`GRID_SIZE`).
    - **Origin**: Top-Left (0,0). Y increases downwards.
4.  **Terminal Sharing**:
    - Terminals are virtual. Multiple circuits can "add" to the same Terminal Tag (e.g., "X1").
    - The `state` ensures pin numbers increment correctly across unconnected circuits (Circuit A uses X1:1,2,3; Circuit B uses X1:4,5,6).

## Examples

Check the `examples/` directory for full working scripts.

To run an example:
```bash
python examples/example_dol_starter.py
```
Outputs are saved to `examples/output/`.
