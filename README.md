# PySchemaElectrical

**PySchemaElectrical** is a Python library for programmatically generating IEC 60617 compliant electrical schematics. It emphasizes specific architectural principles (functional, data-oriented) to create deterministic, reproducible, and beautiful SVG drawings.

> [!NOTE]
> **Status:** Alpha. The API and functionality are subject to change.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [User API (High-Level)](#user-api-high-level)
    - [Terminal](#terminal)
    - [Standard Circuits](#standard-circuits)
    - [BuildResult](#buildresult)
    - [CircuitBuilder](#circuitbuilder)
    - [Descriptors](#descriptors)
    - [wire() Helper](#wire-helper)
    - [Symbols](#symbols)
    - [Project API](#project-api)
    - [PlcMapper](#plcmapper)
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

### Terminal

The `Terminal` class is an immutable `str` subclass that carries metadata about physical terminal blocks. Terminals are the primary way to declare connection points in your project.

```python
from pyschemaelectrical import Terminal

# Basic terminal
X1 = Terminal("X1", description="Main 400V AC")

# Terminal with all pins bridged internally
X3 = Terminal("X3", description="Fused 24V DC", bridge="all")

# Terminal with specific pin ranges bridged
X4 = Terminal("X4", description="Ground Bus", bridge=[(1, 4)])

# Reference terminal (non-physical, excluded from reports)
PLC_DO = Terminal("PLC:DO", description="PLC Digital Output", reference=True)

# Terminal with prefixed pin numbering (e.g., "L1:1", "L2:1", "L3:1")
X5 = Terminal("X5", description="3-Phase Input", pin_prefixes=("L1", "L2", "L3"))
```

Since `Terminal` inherits from `str`, it works anywhere a plain string terminal ID was used before — full backwards compatibility.

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

### BuildResult

All circuit factories and `CircuitBuilder.build()` return a `BuildResult` dataclass:

```python
@dataclass
class BuildResult:
    state: Any              # Updated autonumbering state
    circuit: Circuit        # The generated Circuit object
    used_terminals: list    # Terminal IDs consumed
    component_map: dict     # {"K": ["K1", "K2"], "F": ["F1"]}
    terminal_pin_map: dict  # {"X1": ["1", "2", "3"]}
```

**Tuple unpacking** is supported for backwards compatibility:

```python
# Unpack the three main fields
state, circuit, used_terminals = dol_starter(state, x=0, y=0, tm_top="X1", tm_bot="X2")

# Or use the full result for tag/pin reuse
result = dol_starter(state, x=0, y=0, tm_top="X1", tm_bot="X2")
print(result.component_map)  # {"F": ["F1"], "Q": ["Q1"]}
```

**Tag reuse** lets a second circuit reference the same component tags:

```python
# Motor control circuit reuses contactor tags from the power circuit
result_power = dol_starter(state, x=0, y=0, tm_top="X1", tm_bot="X2")
result_ctrl = builder.build(reuse_tags={"K": result_power})
```

**Terminal pin reuse** lets a second circuit share pins from a first:

```python
result_ctrl = builder.build(reuse_terminals={"X1": result_power})
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

Located in `pyschemaelectrical.builder`, `CircuitBuilder` provides a fluent interface for constructing custom linear circuits. It handles layout, auto-numbering, connections, and multi-instance generation.

```python
from pyschemaelectrical import CircuitBuilder
from pyschemaelectrical.symbols import coil_symbol, normally_open_symbol

state = create_autonumberer()
builder = CircuitBuilder(state)

# Configure layout
builder.set_layout(x=0, y=0, spacing=100, symbol_spacing=60)

# Define the circuit top-to-bottom
builder.add_terminal("X1")                                    # Top terminal
builder.add_component(normally_open_symbol, "S", pins=("1", "2"))  # NO contact
builder.add_component(coil_symbol, "K", pins=("A1", "A2"))        # Relay coil
builder.add_terminal("X2")                                    # Bottom terminal

# Build 3 instances side-by-side with wire labels
result = builder.build(
    count=3,
    wire_labels=["RD 1.5mm2", "BK 1.5mm2"],
)
state = result.state
```

Key methods:

- `add_terminal(id, poles=1, pins=None)` — Add a terminal block
- `add_component(symbol_fn, tag_prefix, pins=None)` — Add a symbol with auto-numbering
- `add_reference(terminal_id)` — Add a reference symbol (non-physical, e.g., PLC)
- `add_connection(from_ref, to_ref, side)` — Add manual connections between components
- `set_layout(x, y, spacing, symbol_spacing)` — Configure positioning
- `build(count, wire_labels, reuse_tags, ...)` — Generate the circuit(s)

### Descriptors

For simple linear circuits, the descriptor API provides a more compact alternative to `CircuitBuilder`:

```python
from pyschemaelectrical import ref, comp, term, build_from_descriptors
from pyschemaelectrical.symbols import coil_symbol

result = build_from_descriptors(
    state,
    [
        ref("PLC:DO"),                              # Reference (PLC output)
        comp(coil_symbol, "K", pins=("A1", "A2")),  # Relay coil
        term("X103"),                                # Physical terminal
    ],
    x=0, y=0,
    count=4,
    wire_labels=["RD 0.5mm2", "BK 0.5mm2"],
)
```

Each descriptor maps to a builder method:

- `ref(terminal_id)` — Reference symbol (non-physical endpoint)
- `comp(symbol_fn, tag_prefix, pins=())` — Component with auto-numbering
- `term(terminal_id, poles=1, pins=None)` — Physical terminal block

### wire() Helper

The `wire()` helper creates wire specification label strings:

```python
from pyschemaelectrical import wire

labels = [
    wire("RD", "2.5mm2"),   # "RD 2.5mm2"
    wire("BK", "1.5mm2"),   # "BK 1.5mm2"
    wire.EMPTY,              # "" (no label for this wire)
]

result = dol_starter(state, x=0, y=0, tm_top="X1", tm_bot="X2",
                     wire_labels=labels)
```

### Project API

The `Project` class orchestrates multi-page schematic drawing sets with automatic PDF compilation via Typst.

```python
from pyschemaelectrical import Project, Terminal

project = Project(
    title="Auxiliary Cabinet",
    drawing_number="DWG-001",
    author="J. Engineer",
    project="Plant Upgrade",
    revision="00",
)

# 1. Declare terminals
project.terminals(
    Terminal("X1", "Main 400V AC"),
    Terminal("X2", "Motor Outputs"),
    Terminal("X3", "Fused 24V DC", bridge="all"),
    Terminal("X4", "Ground Bus", bridge="all"),
)

# 2. Register circuits (state threads automatically between them)
project.dol_starter("motors", count=3, tm_top="X1",
                    tm_bot=["X10", "X11", "X12"])
project.psu("power_supply", tm_top_l="X1", tm_top_n="X1",
            tm_bot_24v="X3", tm_bot_gnd="X4")
project.coil("relays", count=4, tm_top="X3", tm_bot="X4")

# 3. Define pages
project.front_page("cover.md")               # Markdown cover page
project.page("Motor Circuits", "motors")       # Schematic page
project.page("Power Supply", "power_supply")
project.page("Control Relays", "relays")
project.terminal_report()                      # Auto-generated terminal list
project.plc_report("plc_connections.csv")      # PLC connection table

# 4. Build PDF
project.build("output/schematics.pdf")
```

Available circuit registration methods: `dol_starter`, `psu`, `changeover`, `spdt`, `coil`, `no_contact`, `emergency_stop`.

### PlcMapper

`PlcMapper` handles PLC I/O allocation — mapping field sensors to PLC module channels and generating connection tables.

```python
from pyschemaelectrical import PlcMapper

plc = PlcMapper()

# Define module types
plc.module_type("AI_RTD", capacity=2, pin_format="CH{ch}_{pin}")
plc.module_type("DI", capacity=8, pin_format="DI{ch}")

# Define sensor types
plc.sensor_type("RTD", module="AI_RTD", pins=["R+", "RL", "R-"])
plc.sensor_type("Switch", module="DI", pins=["Signal", "GND"],
                polarity={0: "+", 1: "-"})

# Register sensors
plc.sensor("TT-01", type="RTD", cable="W0102", terminal="X007")
plc.sensor("LS-01", type="Switch", cable="W0201", terminal="X008")

# Generate connection objects
connections = plc.generate_connections()

# Or generate as string rows for CSV export
rows = plc.generate_connections_table()
```

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

### Circuit Merging

You can combine multiple circuit objects into one.

```python
from pyschemaelectrical.system.system import merge_circuits

# Merges sub_circuit contents into main_circuit
merge_circuits(main_circuit, sub_circuit) 
```

### Wire Labeling

Utilities exist to find vertical wires and add text labels (e.g., color/size).

```python
from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

# Adds labels to all vertical wires found in the circuit
add_wire_labels_to_circuit(my_circuit, ["RD 2.5mm²", "BK 1.5mm²"])
```

### Terminal Bridge Utilities

Utilities for managing internal terminal connections (bridges). Bridges represent physical jumpers between pins on terminal strips.

```python
from pyschemaelectrical import update_csv_with_internal_connections

# Define project-specific internal connections
# "all" = all pins bridged, or list of (start, end) ranges
internal_connections = {
    "X009": [(1, 2)],       # Pins 1-2 bridged
    "X102": [(1, 2)],       # Power distribution
    "X103": "all",          # All ground pins bridged
}

# Update the system terminals CSV with bridge group info
update_csv_with_internal_connections("terminals.csv", internal_connections)
```

Additional utilities:
- `expand_range_to_pins(start, end)` - Expand range to list of pins
- `get_connection_groups_for_terminal(tag, pins, connections)` - Get bridge groups
- `generate_internal_connections_data(terminal_pins, connections)` - Generate all bridge data
- `parse_terminal_pins_from_csv(csv_path)` - Parse terminal pins from CSV

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
