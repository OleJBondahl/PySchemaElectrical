# PySchemaElectrical API Guide

**Version**: 4.0 (Complete Reference)
**Library Version**: 0.1.6 (Alpha)
**Target Audience**: LLM Agents & Advanced Developers

This guide provides a comprehensive understanding of the `PySchemaElectrical` library. It is organized from the highest-level, most commonly used APIs down to the low-level internals. It covers every public function, class, and constant available for building IEC 60617-compliant electrical schematic diagrams.

---

## 1. Core Concepts & Architecture

### The "Pure Core" Philosophy

The library separates **Layout/Logic** from **Rendering**.

1. **State (Immutable)**: The `state` object (created by `create_autonumberer`) holds the current counters for tags (K1, K2...) and terminals (X1:1, X1:2...). It must be threaded through every function call.
2. **Spec (Declarative)**: The `CircuitBuilder` builds a *Specification* (`CircuitSpec`), not the circuit itself immediately.
3. **Build (Functional)**: The `.build()` method executes the spec, mutating the state and generating the `Circuit` object.

### The Coordinate System

- **Grid**: 1 Grid Unit = 5.0mm (`GRID_SIZE`).
- **Standard Spacing**:
  - Terminals are usually 10mm (2 Grids) apart.
  - Component vertical spacing is usually 50mm.
- **Direction**: Y-axis points **DOWN**. (0,0) is top-left.

### Three-Layer API Design

1. **Project API** (`project.py`): Top-level orchestration. Manages multi-page schematics, terminal registries, title blocks, and PDF/SVG compilation. Owns state internally.
2. **Circuit API** (`std_circuits/`, `builder.py`, `descriptors.py`): For library consumers. Creates complete circuits with automatic state management, autonumbering, layout, and connections.
3. **Symbol API** (`model/`, `system/`, `symbols/`): For extending the library with new components. Direct manipulation of Symbols, Ports, and Circuits.

### Core Data Flow

```
State (autonumbering) -> Symbol factories -> Circuit container -> Layout/wiring -> SVG render
```

---

## 2. Project API (Highest Level)

The `Project` class is the top-level entry point for creating complete multi-page schematic drawing sets. It manages state, terminals, circuit definitions, pages, and output configuration internally — no manual state threading required.

### 2.1. Creating a Project

```python
from pyschemaelectrical import Project, Terminal

project = Project(
    title="Motor Control Panel",
    drawing_number="DWG-001",
    author="Engineer",
    project="Project Name",
    revision="00",
    logo="path/to/logo.png",   # Optional
    font="Times New Roman",    # Default font
)
```

### 2.2. Registering Terminals

```python
project.terminals(
    Terminal("X1", description="Main 400V AC"),
    Terminal("X3", description="Fused 24V DC", bridge="all"),
    Terminal("X4", description="Ground", bridge="all"),
    Terminal("PLC:DO", reference=True),  # Excluded from reports
)

# Seed pin counter so auto-allocation starts at a specific pin
project.set_pin_start("X1", 10)  # Next X1 pin will be 10
```

### 2.3. Registering Standard Circuits

Each method registers a circuit definition. Circuits are built lazily when `build()` or `build_svgs()` is called.

```python
# DOL Motor Starter
project.dol_starter("motors", count=3,
    tm_top="X1", tm_bot=["X10", "X11", "X12"],
    tm_aux_1="X3", tm_aux_2="X4")

# Power Supply Unit
project.psu("power_supply",
    tm_top="X1", tm_bot_left="X3", tm_bot_right="X4")

# Changeover Switch
project.changeover("changeover",
    tm_top_left="X1", tm_top_right="X2", tm_bot="X5")

# SPDT Relay Circuit
project.spdt("relays", count=4,
    tm_top="X3", tm_bot_left="X4", tm_bot_right="PLC:DO")

# Coil Circuit
project.coil("voltage_monitor", tm_top="X1")

# Normally Open Contact
project.no_contact("switches", count=2, tm_top="X3", tm_bot="X4")

# Emergency Stop
project.emergency_stop("estop", tm_top="X3", tm_bot="X4")
```

### 2.4. Registering Custom Circuits

#### From Descriptors

```python
from pyschemaelectrical import ref, comp, term
from pyschemaelectrical.symbols import coil_symbol

project.circuit("custom_coils",
    components=[
        ref("PLC:DO"),
        comp(coil_symbol, "K", pins=("A1", "A2")),
        term("X103"),
    ],
    count=3,
    wire_labels=["RD 2.5mm2", "BK 2.5mm2"],
    reuse_tags={"K": "relays"},       # Reuse tags from "relays" circuit
    start_indices={"K": 5},           # Start tag numbering at K5
    terminal_start_indices={"X103": 1},
)
```

#### From Builder Function

```python
def my_circuit(state, **kwargs):
    from pyschemaelectrical import CircuitBuilder
    from pyschemaelectrical.symbols import normally_open_symbol, coil_symbol

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=100, symbol_spacing=50)
    builder.add_terminal("X1")
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder.add_terminal("X2")
    return builder.build()

project.custom("my_custom", builder_fn=my_circuit)
```

### 2.5. Page Management

```python
# Schematic pages (reference a registered circuit key)
project.page("Motor Circuits", "motors")
project.page("Power Supply", "power_supply")

# Front page from Markdown
project.front_page("docs/front_page.md", notice="CONFIDENTIAL")

# Auto-generated terminal report
project.terminal_report()

# PLC connections report
project.plc_report("plc_connections.csv")

# Custom Typst page
project.custom_page("Notes", "= Notes\nCustom content here.")
```

### 2.6. Building Output

```python
# Build multi-page PDF (requires Typst)
project.build("output.pdf", temp_dir="temp", keep_temp=False)

# Build SVGs only (no Typst dependency)
project.build_svgs(output_dir="output")
```

The `build()` pipeline: (1) Build all circuits → (2) Generate SVGs → (3) Generate per-circuit terminal CSVs → (4) Generate system terminal CSV with bridge info → (5) Compile Typst → PDF.

`build_svgs()` performs steps 1-4 only, writing SVG and CSV files to the output directory.

---

## 3. Standard Circuits Library

The functions in `pyschemaelectrical.std_circuits` are pre-built circuit factories. They all share a common signature pattern:

```python
def factory(state, x, y, tm_..., ..., count=1, wire_labels=None, **kwargs) -> Tuple[state, Circuit, used_terminals]
```

### 3.1. `dol_starter` — Direct-On-Line Motor Starter

```python
std_circuits.dol_starter(
    state, x, y,
    # Required terminal IDs
    tm_top="X1",               # N-pole power input terminal
    tm_bot="X2",               # N-pole motor output terminal (or list for per-instance)
    # Layout
    spacing=150.0,             # LayoutDefaults.CIRCUIT_SPACING_MOTOR
    symbol_spacing=50.0,       # LayoutDefaults.SYMBOL_SPACING_DEFAULT
    # Component tag prefixes
    breaker_tag_prefix="F",
    thermal_tag_prefix="FT",
    contactor_tag_prefix="Q",
    ct_tag_prefix="CT",
    # Pin configurations (all have defaults)
    breaker_pins=("1", "2", "3", "4", "5", "6"),
    thermal_pins=("", "T1", "", "T2", "", "T3"),
    contactor_pins=("1", "2", "3", "4", "5", "6"),
    ct_pins=("1", "2", "3", "4"),
    ct_terminals=None,         # Optional tuple of Terminal/str for CT connection points
    tm_top_pins=None,          # None = auto-number
    tm_bot_pins=None,
    # Terminal poles
    poles=3,                   # Number of poles (default 3 for three-phase)
    # Optional auxiliary terminals
    tm_aux_1=None,             # Auxiliary input (e.g., fused 24V)
    tm_aux_2=None,             # Auxiliary output (e.g., GND)
    # Multi-count
    count=1,
    wire_labels=None,
)
```

**Components created**: N-pole circuit breaker, contactor assembly (coil + N-pole contacts), N-pole thermal overload, current transducer assembly, and N-pole input/output terminals.

**Per-instance output terminals**: `tm_bot` can be a list of terminal IDs (one per instance) for per-motor terminal assignments:

```python
std_circuits.dol_starter(state, 0, 0,
    tm_top="X1",
    tm_bot=["X10", "X11", "X12"],  # Each motor gets its own terminal
    count=3,
)
```

**CT terminals**: `ct_terminals` accepts a tuple of terminal IDs or `Terminal` objects. Reference terminals (with `reference=True`) render as arrows; physical terminals render as terminal symbols with auto-numbered pins:

```python
std_circuits.dol_starter(state, 0, 0,
    tm_top="X1", tm_bot="X2",
    ct_terminals=("X5", Terminal("PLC:AI", reference=True), "X5", Terminal("PLC:AI", reference=True)),
)
```

### 3.2. `psu` — Power Supply Unit

```python
std_circuits.psu(
    state, x, y,
    tm_top="X1",               # AC input (3-pole: L, N, PE)
    tm_bot_left="X2",          # DC output 1 (e.g., 24V)
    tm_bot_right="X3",         # DC output 2 (e.g., GND)
    spacing=150.0,             # LayoutDefaults.CIRCUIT_SPACING_POWER
    symbol_spacing=60.0,       # LayoutDefaults.SYMBOL_SPACING_STANDARD
    terminal_offset=15.0,      # LayoutDefaults.PSU_TERMINAL_OFFSET (kept for back-compat, ignored)
    tag_prefix="PSU",          # StandardTags.POWER_SUPPLY
    count=1,
    wire_labels=None,
)
```

**Components created**: 3-pole input terminal, 2-pole circuit breaker (L + N), PSU block (L, N, PE → 24V, GND), and two single-pole output terminals.

### 3.3. `changeover` — Dual-Input Changeover Circuit

```python
std_circuits.changeover(
    state, x, y,
    tm_top_left="X1",          # Input 1 (Main power)
    tm_top_right="X2",         # Input 2 (Emergency power)
    tm_bot="X3",               # Output
    spacing=150.0,             # LayoutDefaults.CIRCUIT_SPACING_POWER
    symbol_spacing=60.0,       # LayoutDefaults.SYMBOL_SPACING_STANDARD
    terminal_offset=20.0,      # LayoutDefaults.CHANGEOVER_TERMINAL_OFFSET
    tag_prefix="K",            # StandardTags.RELAY
    poles=3,                   # Number of SPDT poles
    tm_top_left_pins=None,     # Optional explicit pin tuples
    tm_top_right_pins=None,
    tm_bot_pins=None,
    count=1,
    wire_labels=None,
)
```

**Components created**: Multi-pole SPDT switch with per-pole input terminals (NC for main, NO for emergency) and common output terminals.

### 3.4. `power_distribution` — Complete Power Distribution System

```python
std_circuits.power_distribution(
    state, x, y,
    # Required: terminal map with logical keys
    terminal_maps={
        "INPUT_1": "X1",       # Main power input
        "INPUT_2": "X2",       # Emergency power input
        "OUTPUT": "X5",        # Changeover output
        "PSU_INPUT": "X1",     # PSU AC input
        "PSU_OUTPUT_1": "X3",  # PSU DC output 1 (24V)
        "PSU_OUTPUT_2": "X4",  # PSU DC output 2 (GND)
    },
    spacing=150.0,             # LayoutDefaults.CIRCUIT_SPACING_POWER
    spacing_single_pole=100.0, # LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE
    voltage_monitor_offset=50.0, # LayoutDefaults.VOLTAGE_MONITOR_OFFSET
    psu_offset=25.0,           # LayoutDefaults.PSU_LAYOUT_OFFSET
    count=1,                   # Number of changeover instances
)
```

**Composite circuit**: Changeover switch(es) + Voltage Monitor coil + PSU. All connected via the `terminal_maps` dictionary. Legacy keys `PSU_OUTPUT_24V` and `PSU_OUTPUT_GND` are auto-mapped to `PSU_OUTPUT_1` and `PSU_OUTPUT_2`.

### 3.5. `spdt` — SPDT Control Circuit (Coil + Changeover Contact)

```python
std_circuits.spdt(
    state, x, y,
    tm_top="X1",               # Input terminal
    tm_bot_left="X2",          # NC output terminal
    tm_bot_right="X3",         # NO output (rendered as reference arrow)
    spacing=100.0,             # LayoutDefaults.CIRCUIT_SPACING_CONTROL
    symbol_spacing=50.0,       # LayoutDefaults.SYMBOL_SPACING_DEFAULT
    column_offset=30.0,        # LayoutDefaults.CONTROL_COLUMN_OFFSET (kept for API compat)
    tag_prefix="Q",            # StandardTags.CONTACTOR
    contact_tag_prefix="K",    # StandardTags.RELAY
    coil_pins=("A1", "A2"),
    contact_pins=("1", "2", "4"),  # Dynamic: instance 0→(11,12,14), instance 1→(21,22,24)
    tm_top_pins=None,
    tm_bot_left_pins=None,
    tm_bot_right_pins=None,
    count=1,
    wire_labels=None,
    relay_tag=None,            # Fixed relay tag (e.g., "K2") for all instances
)
```

**Layout**: Top Terminal → Coil → SPDT Contact (inverted) → NC terminal (left) + NO reference arrow (right).

**Dynamic pin numbering**: When `contact_pins=("1", "2", "4")` (default), pins auto-increment per instance: instance 0 gets (11, 12, 14), instance 1 gets (21, 22, 24), etc.

### 3.6. `no_contact` — Normally Open Contact Circuit

```python
std_circuits.no_contact(
    state, x, y,
    tm_top="X1",               # Input terminal
    tm_bot="X2",               # Output terminal
    spacing=100.0,             # LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE
    symbol_spacing=60.0,       # LayoutDefaults.SYMBOL_SPACING_STANDARD
    tag_prefix="S",            # StandardTags.SWITCH
    switch_pins=("3", "4"),    # Pin labels for the NO switch
    tm_top_pins=None,
    tm_bot_pins=None,
    count=1,
    wire_labels=None,
)
```

### 3.7. `coil` — Coil Circuit

Connects a coil between two pins of the **same** terminal strip. Used for voltage monitors and relay coils.

```python
std_circuits.coil(
    state, x, y,
    tm_top="X1",               # Terminal ID (coil connects between two pins of this terminal)
    symbol_spacing=60.0,       # LayoutDefaults.SYMBOL_SPACING_STANDARD
    tag_prefix="K",            # StandardTags.RELAY
    coil_pins=("A1", "A2"),
    tm_top_pins=("1", "2"),    # Specific pins on the terminal strip
)
```

**Layout**: Terminal Pin 1 → Coil → Terminal Pin 2 (same terminal ID).

### 3.8. `emergency_stop` — Emergency Stop Circuit

```python
std_circuits.emergency_stop(
    state, x, y,
    tm_top="X1",               # Input terminal
    tm_bot="X2",               # Output terminal
    spacing=100.0,             # LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE
    symbol_spacing=50.0,       # LayoutDefaults.SYMBOL_SPACING_DEFAULT
    tag_prefix="S",            # StandardTags.SWITCH
    count=1,
    wire_labels=None,
)
```

**Components created**: Input terminal, emergency stop assembly (NC contact + mushroom button), output terminal.

### 3.9. Injection Mechanisms

All standard circuits accept `**kwargs` that can include:

#### The `terminal_maps` Override

Redirect internal logical connections to arbitrary physical terminals.

```python
std_circuits.psu(..., terminal_maps={"INPUT": "X99"})
```

#### The `tag_generators` Override

Force specific naming schemes for components.

```python
def my_motor_gen(state):
    return state, "M_PUMP_1"

std_circuits.dol_starter(..., tag_generators={"M": my_motor_gen})
```

---

## 4. Four Ways to Build Circuits

PySchemaElectrical provides four API levels, from simplest to most flexible:

### 4.1. Project (Simplest — Multi-Page)

See [Section 2](#2-project-api-highest-level). Best for complete drawing sets with PDF output.

### 4.2. Standard Circuits (Pre-Built)

See [Section 3](#3-standard-circuits-library). Best for common industrial circuits.

```python
from pyschemaelectrical import create_autonumberer, render_system, std_circuits

state = create_autonumberer()
state, circuit, used_terminals = std_circuits.dol_starter(
    state, x=0, y=0,
    tm_top="X1", tm_bot="X2",
    count=3,
)
render_system(circuit, "output.svg")
```

### 4.3. Descriptors (Inline Declarative)

For linear circuits with default layout. No builder needed.

```python
from pyschemaelectrical import ref, comp, term, build_from_descriptors, create_autonumberer
from pyschemaelectrical.symbols import coil_symbol

state = create_autonumberer()
result = build_from_descriptors(state, [
    ref("PLC:DO"),
    comp(coil_symbol, "K", pins=("A1", "A2")),
    term("X103"),
], x=0, y=0, count=3)
state, circuit, used_terminals = result  # BuildResult supports tuple unpacking
```

**Descriptor Factories:**

- `ref(terminal_id)` — Reference symbol (PLC, cross-page)
- `comp(symbol_fn, tag_prefix, pins=())` — Any symbol component
- `term(terminal_id, poles=1, pins=None)` — Physical terminal

**`build_from_descriptors` Parameters:**

```python
build_from_descriptors(
    state,                    # Autonumbering state
    descriptors,              # List of ref/comp/term descriptors
    x=0.0, y=0.0,            # Start position
    spacing=80.0,             # Horizontal gap between instances
    count=1,                  # Number of circuit instances
    wire_labels=None,         # Wire label strings
    reuse_tags=None,          # Dict[prefix, BuildResult] for tag reuse
    tag_generators=None,      # Custom tag generators
    start_indices=None,       # Override tag counters
    terminal_start_indices=None,  # Override terminal pin counters
) -> BuildResult
```

### 4.4. CircuitBuilder (Most Flexible)

For custom circuits needing layout control, connections, and horizontal placement.

```python
from pyschemaelectrical import CircuitBuilder, create_autonumberer
from pyschemaelectrical.symbols import normally_open_symbol, coil_symbol

state = create_autonumberer()
builder = CircuitBuilder(state)
builder.set_layout(x=0, y=0, spacing=100, symbol_spacing=50)

tm = builder.add_terminal("X1")
no = builder.add_component(normally_open_symbol, "K", pins=("13", "14"))
coil = builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
builder.add_terminal("X2")

result = builder.build(count=1)
state, circuit, used_terminals = result
```

---

## 5. CircuitBuilder: The Full API

The `CircuitBuilder` is a fluent interface for building custom circuit logic.

### 5.1. Initialization & Layout Control

```python
state = create_autonumberer()
builder = CircuitBuilder(state)
builder.set_layout(
    x=0, y=0,
    spacing=150,        # Horizontal gap between REPEATED instances (count > 1)
    symbol_spacing=50   # Vertical gap between ADDED components (default y_increment)
)
```

### 5.2. Adding Components (`add_component`)

This method is extremely flexible because it passes `**kwargs` directly to the symbol factory.

**Signature:**

```python
builder.add_component(
    symbol_func: Callable,      # e.g., normally_open_symbol
    tag_prefix: str,            # e.g., "K" -> "K1"
    poles: int = 1,
    pins: Tuple[str] = None,    # Explicit pins
    x_offset: float = 0.0,      # Shift X relative to current column center
    y_increment: float = None,  # Override default vertical spacing (can be 0!)
    auto_connect_next: bool = True, # Draw line to the NEXT component added?
    **kwargs                    # <--- PASSED TO symbol_func (Crucial!)
) -> ComponentRef
```

**Advanced Usage:**

- **Invisible Vertical Steps**: Set `y_increment=0` to overlay components or place them horizontally adjacent (using `x_offset`).
- **Hidden Terminals**: Pass specific kwargs supported by symbols, e.g., `builder.add_component(coil_symbol, ..., show_terminals=False)`.

### 5.3. Adding Terminals (`add_terminal`)

Terminals interact with the connection registry to create netlists.

**Signature:**

```python
builder.add_terminal(
    tm_id: str,                 # Physical Strip ID (e.g., "X1")
    poles: int = 1,
    pins: List[str] = None,     # Specific pin numbers (["1", "2"])
    logical_name: str = None,   # LOGICAL alias for mapping (e.g., "INPUT_A")
    label_pos: str = None,      # Visual label placement ("left" or "right")
    x_offset: float = 0.0,
    y_increment: float = None,
    auto_connect_next: bool = True,
    **kwargs
) -> ComponentRef
```

**Power Feature: Logical Names**
Assign a `logical_name="MAIN_PWR"` to a terminal. Later, when using `standard_circuits`, you can map "MAIN_PWR" to any physical terminal ID (e.g., "X100") using `terminal_maps`.

### 5.4. Adding References (`add_reference`)

Reference symbols (PLC, cross-page) always use their ID as the tag (not auto-numbered).

```python
builder.add_reference(
    ref_id: str,                # e.g., "PLC:DO", "PLC:AI"
    x_offset: float = 0.0,
    y_increment: float = None,
    auto_connect_next: bool = True,
    **kwargs
) -> ComponentRef
```

### 5.5. Placing Components Horizontally (`place_right`)

Place a component to the right of an existing one at the same Y position. Does NOT advance the vertical stack pointer.

```python
coil_ref = builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
contactor_ref = builder.place_right(
    ref=coil_ref,                     # ComponentRef of the component to place next to
    symbol_func=three_pole_normally_open_symbol,
    tag_prefix="K",
    pins=("1", "2", "3", "4", "5", "6"),
    spacing=40.0,                     # Horizontal distance from ref component
    poles=3,
    auto_connect_next=False,
) -> ComponentRef
```

### 5.6. Connection Methods

#### Pin-Based Connections (`connect`)

The preferred modern connection API using `ComponentRef` and `PortRef`.

```python
builder.connect(
    a: PortRef,                 # Source: tm.pin("1") or cb.pole(0)
    b: PortRef,                 # Target: cb.pin("1") or psu.pin("L")
    side_a: str = None,         # "top" or "bottom" (inferred if None)
    side_b: str = None,
) -> CircuitBuilder
```

**Example:**

```python
tm = builder.add_terminal("X1", pins=("1",))
cb = builder.add_component(circuit_breaker_symbol, "F", pins=("1", "2"))
builder.connect(tm.pin("1"), cb.pin("1"))
```

#### Index-Based Connections (`add_connection`)

Legacy index-based API. Still useful for complex wiring by component order.

```python
builder.add_connection(
    comp_idx_a: int,    # Index in builder order (0, 1, 2...)
    pole_idx_a: int,    # 0-indexed pole
    comp_idx_b: int,
    pole_idx_b: int,
    side_a: str = "bottom",
    side_b: str = "top"
) -> CircuitBuilder
```

#### Horizontal Matching Connections (`connect_matching`)

Connect two components horizontally on pins that share the same name.

```python
builder.connect_matching(
    ref_a: ComponentRef,        # First component
    ref_b: ComponentRef,        # Second component
    pins: List[str] = None,     # Pin filter (None = all matching)
    side_a: str = "right",
    side_b: str = "left",
) -> CircuitBuilder
```

### 5.7. Building (`build`)

```python
result = builder.build(
    count: int = 1,                        # Number of circuit instances
    start_indices: Dict[str, int] = None,  # Override tag counters: {"K": 3}
    terminal_start_indices: Dict[str, int] = None,  # Override terminal pin counters
    tag_generators: Dict[str, Callable] = None,      # Custom tag generators
    terminal_maps: Dict[str, Any] = None,  # Terminal ID overrides by logical name
    reuse_tags: Dict[str, BuildResult] = None,  # Reuse tags from another result
    wire_labels: List[str] = None,         # Wire label strings per instance
) -> BuildResult
```

### 5.8. ComponentRef & PortRef

`add_component`, `add_terminal`, `add_reference`, and `place_right` all return a `ComponentRef`.

```python
ref = builder.add_component(coil_symbol, "K", pins=("A1", "A2"))

# Access specific ports:
ref.pin("A1")    # -> PortRef by pin name
ref.pole(0)      # -> PortRef by pole index

# Backwards-compatible tuple unpacking:
_, idx = builder.add_component(coil_symbol, "K")
```

### 5.9. BuildResult

Returned by `builder.build()`.

- `state`: The *new* autonumbering state (must be used for next operation).
- `circuit`: The `Circuit` object containing `elements` (visuals) and `symbols` (logical objects).
- `used_terminals`: List of terminal IDs touched by this builder.
- `component_map`: Dictionary `{prefix: [tags]}` (e.g., `{"K": ["K1", "K2"]}`).
- `reuse_tags(prefix) -> Callable`: Returns a tag generator that yields tags from this result's component_map. Used with the `reuse_tags` build parameter.

```python
# Tuple unpacking:
state, circuit, used_terminals = result

# Tag reuse across builders:
result_a = builder_a.build()
result_b = builder_b.build(reuse_tags={"K": result_a})
```

---

## 6. Terminal Type

The `Terminal` class is an immutable `str` subclass with metadata. It remains backwards-compatible with strings everywhere terminal IDs are accepted.

```python
from pyschemaelectrical import Terminal

# Basic terminal
tm = Terminal("X001", description="Main 400V AC")

# Terminal with bridging info
tm = Terminal("X002", description="24V DC", bridge="all")
tm = Terminal("X003", bridge=[(1, 3), (5, 7)])  # Bridge ranges

# Reference terminal (excluded from reports)
tm = Terminal("PLC:DO", reference=True)

# Works everywhere strings work:
state, circuit, _ = std_circuits.dol_starter(state, x=0, y=0, tm_top=tm, ...)
```

**Terminal attributes:**

- `description` (str): Human-readable description
- `bridge` (Optional): `"all"`, list of `(start, end)` tuples, or `None`
- `reference` (bool): True for non-physical terminals (PLC, etc.)

---

## 7. Wire Labeling

### Wire Specification Helper

```python
from pyschemaelectrical import wire

# Create wire labels
labels = [wire("RD", "2.5mm2"), wire("BK", "2.5mm2"), wire("BU", "2.5mm2")]

# Apply via build():
result = builder.build(wire_labels=labels)

# Or via std_circuits:
state, circuit, _ = std_circuits.dol_starter(
    state, x=0, y=0, ..., wire_labels=labels
)

# Empty wire label (no label on that wire):
wire.EMPTY  # ""
```

### Post-Processing Wire Labels

Apply labels *after* the circuit is built but *before* rendering.

```python
from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

labels = ["L1", "L2", "L3", "N", "PE"]
new_circuit = add_wire_labels_to_circuit(circuit, labels)
```

---

## 8. PLC I/O Mapping

The `PlcMapper` provides declarative PLC I/O allocation with automatic module bin-packing.

```python
from pyschemaelectrical import PlcMapper

plc = PlcMapper()

# 1. Define module types (all methods return self for chaining)
plc.module_type("AI_mA", capacity=4, pin_format="CH{ch}{polarity}")
plc.module_type("AI_RTD", capacity=2, pin_format="CH{ch}_{pin}")

# 2. Define sensor types
plc.sensor_type("2Wire-mA", module="AI_mA",
    pins=["Signal", "GND"], polarity={0: "+", 1: "-"})
plc.sensor_type("RTD", module="AI_RTD",
    pins=["R+", "RL", "R-"])

# 3. Add sensor instances
plc.sensor("TT-01-CX", type="RTD", cable="W0102", terminal="X007")
plc.sensor("PT-01", type="2Wire-mA", cable="W0103", terminal="X007")

# 4. Generate connections
connections = plc.generate_connections()      # List[PlcConnection]
table = plc.generate_connections_table()      # List[List[str]] for CSV
counts = plc.module_count                     # Dict[str, int] (property)

# Optional: seed terminal pin counter
plc.set_terminal_start("X007", 10)
```

**PlcConnection fields:**
`sensor_tag`, `cable`, `terminal`, `terminal_pin`, `module_name`, `module_pin`, `sensor_pin`

---

## 9. Terminal Output & Exports

### 9.1. Connection Registry (The Netlist)

Every time `auto_connect` runs or you use `register_connection`, the `state` updates its internal `TerminalRegistry`.

```python
from pyschemaelectrical import get_registry, export_registry_to_csv

registry = get_registry(state)
export_registry_to_csv(registry, "terminal_connections.csv")
```

**Output Format**:

| Component From | Pin From | Terminal Tag | Terminal Pin | Component To | Pin To |
| :--- | :--- | :--- | :--- | :--- | :--- |
| K1 / K2 | 14 / 14 | X1 | 1 | M1 | U |

### 9.2. Terminal List Export

```python
from pyschemaelectrical import export_terminal_list

used_terminals = ["X1", "X2", "X1"]  # can contain duplicates
descriptions = {"X1": "Main Power", "X2": "Control 24V"}
export_terminal_list("terminals_bom.csv", used_terminals, descriptions)
```

### 9.3. Terminal Bridge Utilities

```python
from pyschemaelectrical import (
    BridgeRange,
    expand_range_to_pins,
    get_connection_groups_for_terminal,
    generate_internal_connections_data,
    parse_terminal_pins_from_csv,
    update_csv_with_internal_connections,
)

# Expand range to pins: (1, 3) → [1, 2, 3]
pins = expand_range_to_pins(1, 3)

# Get connection groups from registry
groups = get_connection_groups_for_terminal("X1", [1, 2, 3], {"X1": "all"})

# Generate internal connections and update CSV
connections = generate_internal_connections_data(
    {"X1": [1, 2, 3]},      # terminal_pins
    {"X1": "all"}            # internal_connections
)
update_csv_with_internal_connections("connections.csv", {"X1": "all"})
```

---

## 10. State Management & Autonumbering

```python
from pyschemaelectrical import (
    create_autonumberer,
    get_tag_number,
    next_terminal_pins,
    set_tag_counter,
    set_terminal_counter,
)

# Create fresh state
state = create_autonumberer()

# Get next tag number (read-only)
num = get_tag_number(state, "K")  # 1

# Override counters
state = set_tag_counter(state, "K", 5)     # Next K tag will be K5
state = set_terminal_counter(state, "X1", 10)  # Next X1 pin will be 10

# Generate terminal pins (advances state)
state, pins = next_terminal_pins(state, "X1", poles=3)  # ("1","2","3")
```

### Additional Autonumbering Functions

```python
from pyschemaelectrical.utils.autonumbering import (
    next_tag,             # Get next tag and advance state: (state, "K1")
)
```

### Utility Functions

```python
from pyschemaelectrical.utils.utils import (
    apply_start_indices,     # Apply start indices to tag counters
    merge_terminals,         # Merge terminal lists (deduplicating)
)
```

### Sharing State Across Circuits

```python
state = create_autonumberer()
state, c1, _ = std_circuits.dol_starter(state, x=0, y=0, tm_top="X1", tm_bot="X2")
state, c2, _ = std_circuits.dol_starter(state, x=200, y=0, tm_top="X1", tm_bot="X3")
# X1 pin numbers continue sequentially across c1 and c2
```

---

## 11. System & Rendering

### Circuit Container

```python
from pyschemaelectrical import Circuit, add_symbol, render_system
from pyschemaelectrical.system.system import merge_circuits, auto_connect_circuit

# Create and populate
c = Circuit()
placed_sym = add_symbol(c, symbol, x=10, y=20)
auto_connect_circuit(c)  # Wire adjacent symbols

# Merge multiple circuits into one page
main = Circuit()
merge_circuits(main, dol_circuit)
merge_circuits(main, safety_circuit)

# Render to SVG
render_system(main, "output.svg")
render_system(main, "output.svg", width="210mm", height="297mm")  # A4
```

### Transform Utilities

```python
from pyschemaelectrical.utils.transform import translate, rotate

new_symbol = translate(symbol, dx=50, dy=0)    # Pure, returns new instance
new_symbol = rotate(symbol, angle=90, center=Point(0, 0))
```

### Connection Registry (Low-Level)

```python
from pyschemaelectrical.system.connection_registry import (
    Connection,              # Frozen dataclass: terminal_tag, terminal_pin, component_tag, component_pin, side
    TerminalRegistry,        # Immutable registry with .add_connection() and .add_connections()
    get_registry,            # Get registry from state
    update_registry,         # Update registry in state
    register_connection,     # Register single connection in state
    register_3phase_connections,  # Register 3-phase connections in bulk
    register_3phase_input,   # Register 3-phase input connections (pins 1,3,5)
    register_3phase_output,  # Register 3-phase output connections (pins 2,4,6)
    export_registry_to_csv,  # Export to CSV
)
```

---

## 12. Complete Symbol Reference

All symbol factories live in `pyschemaelectrical.symbols` and follow the pattern:

```python
symbol_func(label: str = "", pins: tuple = (...)) -> Symbol
```

### Contacts (`symbols.contacts`)

| Function | Poles | Ports | Default Pins |
|---|---|---|---|
| `normally_open_symbol` | 1 | `"1"` (up), `"2"` (down) | `()` |
| `normally_closed_symbol` | 1 | `"1"` (up), `"2"` (down) | `()` |
| `spdt_contact_symbol` | 1 | `"1"` (common), `"2"` (NC), `"4"` (NO) | `("1","2","4")` |
| `three_pole_normally_open_symbol` | 3 | `"1"`-`"6"` | `("1","2","3","4","5","6")` |
| `three_pole_normally_closed_symbol` | 3 | `"1"`-`"6"` | `("1","2","3","4","5","6")` |
| `three_pole_spdt_symbol` | 3 | `"{pole}_{type}"` (e.g., `"1_com"`, `"1_nc"`, `"1_no"`) | 9 pins: `("11","12","14","21","22","24","31","32","34")` |
| `multi_pole_spdt_symbol` | N | `"{pole}_{type}"` per pole | Dynamic IEC numbering |

**`spdt_contact_symbol` special parameter:**

- `inverted` (bool): If True, Common at Top (input), NC/NO at Bottom (output). Default `False` (Common at Bottom).

**`multi_pole_spdt_symbol` parameters:**

- `poles` (int): Number of SPDT poles (default 3).

### Coils (`symbols.coils`)

| Function | Ports | Notes |
|---|---|---|
| `coil_symbol` | `"A1"` (top), `"A2"` (bottom) | Only when `show_terminals=True` |

- `show_terminals` (bool): If `False`, hides the vertical lead lines. Size: 10mm x 5mm.

### Breakers (`symbols.breakers`)

| Function | Poles | Ports | Default Pins |
|---|---|---|---|
| `circuit_breaker_symbol` | 1 | `"1"` (up), `"2"` (down) | `()` |
| `two_pole_circuit_breaker_symbol` | 2 | `"1"`-`"4"` | `("1","2","3","4")` |
| `three_pole_circuit_breaker_symbol` | 3 | `"1"`-`"6"` | `("1","2","3","4","5","6")` |

### Protection (`symbols.protection`)

| Function | Poles | Ports | Default Pins |
|---|---|---|---|
| `thermal_overload_symbol` | 1 | `"1"` (up), `"2"` (down) | `()` |
| `three_pole_thermal_overload_symbol` | 3 | `"1"`-`"6"` | `("1","2","3","4","5","6")` |
| `fuse_symbol` | 1 | `"1"` (up), `"2"` (down) | `()` |

### Motors (`symbols.motors`)

| Function | Ports | Default Pins |
|---|---|---|
| `motor_symbol` | `"1"` (top), `"2"` (bottom) | `()`, single-phase, diameter 15mm |
| `three_pole_motor_symbol` | `"U"`, `"V"`, `"W"`, `"PE"` | `("U","V","W","PE")` |

**`three_pole_motor_symbol` notes:**

- If `pins` length is 4: renders U, V, W + PE terminal.
- If `pins` length is 3: connects U, V, W but suppresses PE graphic.

### Terminals (`symbols.terminals`)

| Function | Poles | Ports | Default Pins |
|---|---|---|---|
| `terminal_symbol` | 1 | `"1"` (up), `"2"` (down), `"top"`, `"bottom"` | `()` |
| `multi_pole_terminal_symbol` | N | `"1"`-`"2N"` (two ports per pole) | `()` |
| `three_pole_terminal_symbol` | 3 | `"1"`-`"6"` | `("1","2","3")` |

**`terminal_symbol` parameters:**

- `label_pos` (str): `"left"` (default) or `"right"` for label placement.

**`multi_pole_terminal_symbol` parameters:**

- `poles` (int): Number of poles (default 2).
- `label_pos` (str): `"left"` or `"right"`.

### Blocks (`symbols.blocks`)

| Function | Notes |
|---|---|
| `dynamic_block_symbol` | Configurable top/bottom pins, width auto-calculated |
| `psu_symbol` | Fixed: top (L, N, PE), bottom (24V, GND), AC/DC separator |
| `terminal_box_symbol` | Rectangular box with configurable pins pointing up |

**`dynamic_block_symbol` parameters:**

- `top_pins` (tuple): Pin names for top side
- `bottom_pins` (tuple): Pin names for bottom side
- `pin_spacing` (float): Global fallback spacing (default: `DEFAULT_POLE_SPACING`)
- `top_pin_positions` (tuple): Explicit X coords for top pins
- `bottom_pin_positions` (tuple): Explicit X coords for bottom pins

**`terminal_box_symbol` parameters:**

- `num_pins` (int): Number of pins (default 1)
- `start_pin_number` (int): Starting pin number (default 1)
- `pin_spacing` (float): Distance between pins (default: `DEFAULT_POLE_SPACING`)
- `pins` (tuple): Explicit pin names (overrides `start_pin_number`)

### Actuators (`symbols.actuators`)

| Function | Notes |
|---|---|
| `emergency_stop_button_symbol` | Mushroom head, `rotation` param (0=right) |
| `turn_switch_symbol` | S-shaped rotary, `rotation` param (0=default, 180=left) |

### Assemblies (`symbols.assemblies`)

| Function | Components | Notes |
|---|---|---|
| `contactor_symbol` | 3-pole NO + coil | Mechanical linkage (dashed line) |
| `emergency_stop_assembly_symbol` | NC contact + mushroom button | Button on left |
| `turn_switch_assembly_symbol` | NO contact + rotary actuator | Actuator on left |

**`contactor_symbol` parameters:**

- `coil_pins` (tuple): Pins for the coil side (None = hidden coil terminals)
- `contact_pins` (tuple): Pins for the 3-pole contact side (default: `("1","2","3","4","5","6")`)

### References (`symbols.references`)

| Function | Notes |
|---|---|
| `ref_symbol` | Arrow for cross-references. `direction`: `"up"` or `"down"`. Port: `"1"` (tail if down) or `"2"` (tail if up) |

**Parameters:** `tag`, `label`, `pins`, `direction="down"`, `label_pos="left"`

### Transducers (`symbols.transducers`)

| Function | Notes |
|---|---|
| `current_transducer_symbol` | Circle with line, no ports (decorative) |
| `current_transducer_assembly_symbol` | Transducer + terminal box, ports from box |

---

## 13. Model & Constants Reference

### Core Geometric Types

```python
from pyschemaelectrical.model.core import Point, Vector, Port, Style, Symbol, Element

Point(x: float, y: float)           # Immutable. Supports +Vector, -Point
Vector(dx: float, dy: float)        # Immutable. Supports +Vector, *scalar
Port(id: str, position: Point, direction: Vector)
Style(stroke="black", stroke_width=1.0, fill="none",
      stroke_dasharray=None, opacity=1.0, font_family=None)
Symbol(elements: List[Element], ports: Dict[str, Port],
       label=None, skip_auto_connect=False)   # Frozen dataclass
```

### Primitive Elements

```python
from pyschemaelectrical.model.primitives import Line, Circle, Text, Path, Group, Polygon

Line(start: Point, end: Point, style: Style)
Circle(center: Point, radius: float, style: Style)
Text(content: str, position: Point, style: Style,
     anchor: str, dominant_baseline: str, font_size: float, rotation: float)
Path(d: str, style: Style)          # Raw SVG path data
Group(elements: List[Element], style: Optional[Style])
Polygon(points: List[Point], style: Style)
```

### Component Part Factories

```python
from pyschemaelectrical.model.parts import (
    standard_style,        # Create standard symbol Style
    standard_text,         # Create component label Text element
    terminal_circle,       # Create standard connection terminal circle
    box,                   # Create rectangular box centered at a Point
    create_pin_labels,     # Generate Text labels for pins
    three_pole_factory,    # Create 3-pole symbol from single-pole factory
    two_pole_factory,      # Create 2-pole symbol from single-pole factory
)
```

### Constants

```python
from pyschemaelectrical.model.constants import *

GRID_SIZE = 5.0                     # mm, base grid unit
GRID_SUBDIVISION = 2.5              # mm, half grid
DEFAULT_POLE_SPACING = 10.0         # 2 * GRID_SIZE
TERMINAL_RADIUS = 1.25              # 0.25 * GRID_SIZE
LINE_WIDTH_THIN = 0.25              # 0.05 * GRID_SIZE
LINE_WIDTH_THICK = 0.5              # 0.1 * GRID_SIZE
LINKAGE_DASH_PATTERN = "2.0, 2.0"   # For mechanical linkage
REF_ARROW_LENGTH = 10.0             # mm
REF_ARROW_HEAD_LENGTH = 3.0         # mm
REF_ARROW_HEAD_WIDTH = 2.5          # mm
TEXT_FONT_FAMILY = "Times New Roman"
TEXT_SIZE_MAIN = 5.0                # GRID_SIZE
TEXT_SIZE_PIN = 3.5                 # 0.7 * GRID_SIZE
TEXT_OFFSET_X = -5.0                # mm, label offset
PIN_LABEL_OFFSET_X = 1.5           # mm
DEFAULT_WIRE_ALIGNMENT_TOLERANCE = 1.0  # mm
DEFAULT_DOC_WIDTH = "210mm"         # A4 width
DEFAULT_DOC_HEIGHT = "297mm"        # A4 height
```

### StandardTags

```python
from pyschemaelectrical import StandardTags

StandardTags.BREAKER           # "F"
StandardTags.CONTACTOR         # "Q"
StandardTags.RELAY             # "K"
StandardTags.SWITCH            # "S"
StandardTags.MOTOR             # "M"
StandardTags.POWER_SUPPLY      # "PSU"
StandardTags.TRANSFORMER       # "T"
StandardTags.INDICATOR         # "H"
StandardTags.BUTTON            # "S"
StandardTags.SENSOR            # "B"
StandardTags.TERMINAL          # "X"
```

### StandardPins

```python
from pyschemaelectrical import StandardPins

StandardPins.THREE_POLE.pins          # ("L1","T1","L2","T2","L3","T3")
StandardPins.THERMAL_OVERLOAD.pins    # ("","T1","","T2","","T3")
StandardPins.CURRENT_TRANSDUCER.pins  # Standard CT pins
StandardPins.L    # "L"
StandardPins.N    # "N"
StandardPins.PE   # "PE"
StandardPins.V24  # "24V"
StandardPins.GND  # "GND"
```

### StandardSpacing

```python
from pyschemaelectrical import StandardSpacing

StandardSpacing.MOTOR              # SpacingConfig(circuit=150, symbols_start=50, symbols=60)
StandardSpacing.SINGLE_POLE        # SpacingConfig(circuit=100, symbols_start=50, symbols=60)
StandardSpacing.POWER_DISTRIBUTION # SpacingConfig(circuit=80, symbols_start=50, symbols=40)
```

### LayoutDefaults

```python
from pyschemaelectrical import LayoutDefaults

LayoutDefaults.CIRCUIT_SPACING_MOTOR       # 150.0 mm
LayoutDefaults.CIRCUIT_SPACING_POWER       # 150.0 mm
LayoutDefaults.CIRCUIT_SPACING_CONTROL     # 100.0 mm
LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE # 100.0 mm
LayoutDefaults.SYMBOL_SPACING_DEFAULT      # 50.0 mm
LayoutDefaults.SYMBOL_SPACING_STANDARD     # 60.0 mm
LayoutDefaults.PSU_TERMINAL_OFFSET         # 15.0 mm
LayoutDefaults.CHANGEOVER_TERMINAL_OFFSET  # 20.0 mm
LayoutDefaults.CONTROL_COLUMN_OFFSET       # 30.0 mm
LayoutDefaults.VOLTAGE_MONITOR_OFFSET      # 50.0 mm
LayoutDefaults.PSU_LAYOUT_OFFSET           # 25.0 mm
```

### StandardCircuitKeys

```python
from pyschemaelectrical import StandardCircuitKeys

StandardCircuitKeys.MAIN       # "MAIN"
StandardCircuitKeys.SUPPLY     # "SUPPLY"
StandardCircuitKeys.OUTPUT     # "OUTPUT"
StandardCircuitKeys.V24        # "V24"
StandardCircuitKeys.GND        # "GND"
StandardCircuitKeys.INPUT      # "INPUT"
StandardCircuitKeys.INPUT_1    # "INPUT_1"
StandardCircuitKeys.INPUT_2    # "INPUT_2"
StandardCircuitKeys.OUTPUT_24V # "OUTPUT_24V"
StandardCircuitKeys.OUTPUT_GND # "OUTPUT_GND"
```

### CircuitLayouts (Pre-Configured)

```python
from pyschemaelectrical import CircuitLayouts

CircuitLayouts.PSU             # CircuitLayoutConfig(spacing=150, symbol=60, terminal_offset=15)
CircuitLayouts.CHANGEOVER      # CircuitLayoutConfig(spacing=150, symbol=60, terminal_offset=20)
CircuitLayouts.DOL_STARTER     # CircuitLayoutConfig(spacing=150, symbol=50)
CircuitLayouts.MOTOR_CONTROL   # CircuitLayoutConfig(spacing=100, symbol=50, column_offset=30)
CircuitLayouts.SWITCH          # CircuitLayoutConfig(spacing=100, symbol=60)
CircuitLayouts.EMERGENCY_STOP  # CircuitLayoutConfig(spacing=100, symbol=50)
```

### GenerationState

```python
from pyschemaelectrical import GenerationState, create_initial_state

# GenerationState fields:
# - tags: Dict[str, int]           — tag prefix counters
# - terminal_counters: Dict[str, int] — terminal pin counters
# - contact_channels: Dict[str, int]  — SPDT channel counters
# - terminal_registry: TerminalRegistry — connection registry
# - pin_counter: int = 0           — global pin counter

# Can convert between dict and dataclass:
gs = GenerationState.from_dict(state_dict)
state_dict = gs.to_dict()

# Create initial state (alternative to create_autonumberer)
state = create_initial_state()
```

---

## 14. Exceptions

```python
from pyschemaelectrical import (
    CircuitValidationError,    # Base class
    PortNotFoundError,         # Port 'X' not found on component 'Y'
    ComponentNotFoundError,    # Component index N is out of bounds
    TagReuseError,             # reuse_tags ran out of tags for prefix 'K'
    WireLabelMismatchError,    # Wire label count doesn't match vertical wire count
)
```

---

## 15. Typst Rendering & PDF Compilation

The rendering pipeline uses Typst for PDF compilation. This is used internally by `Project.build()` but can also be used directly.

```python
from pyschemaelectrical.rendering.typst.compiler import TypstCompiler, TypstCompilerConfig

config = TypstCompilerConfig(
    drawing_name="My Schematics",
    drawing_number="DWG-001",
    author="Engineer",
    project="Project",
    revision="00",
    logo_path="/path/to/logo.png",  # Optional
    font_family="Times New Roman",
    root_dir=".",
    temp_dir="temp",
)
compiler = TypstCompiler(config)

# Add pages
compiler.add_front_page("docs/front.md", notice="CONFIDENTIAL")
compiler.add_schematic_page("Motors", "temp/motors.svg", "temp/motors_terminals.csv")
compiler.add_terminal_report("temp/system_terminals.csv", {"X1": "Main Power"})
compiler.add_plc_report("plc_connections.csv")
compiler.add_custom_page("Notes", "= Notes\nTypst content here.")

# Compile to PDF
compiler.compile("output.pdf")
```

### Frame Generation

```python
from pyschemaelectrical.rendering.typst.frame_generator import generate_frame

# Generate an A3 drawing frame as a Circuit
frame_circuit = generate_frame(font_family="Times New Roman")
```

### Markdown to Typst Conversion

```python
from pyschemaelectrical.rendering.typst.markdown_converter import markdown_to_typst

typst_content = markdown_to_typst("docs/intro.md", width="50%", notice="DRAFT")
```

---

## 16. Edge Cases & Solutions

### Case A: Feedback Loops (Connecting Bottom to Top)

**Problem**: `auto_connect` only goes Down. How do I wire a contact at the bottom back to a coil at the top?
**Solution**: Use `connect()` or `add_connection()`.

```python
coil = builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
contact = builder.add_component(normally_open_symbol, "K", pins=("13","14"),
    x_offset=40, y_increment=0, auto_connect_next=False)
builder.connect(contact.pin("13"), coil.pin("A1"), side_a="top", side_b="top")
```

### Case B: Non-Standard Pin Spacing (Dynamic Blocks)

**Problem**: VFD with pins at irregular positions.
**Solution**: Use `top_pin_positions` in `dynamic_block_symbol`.

```python
builder.add_component(
    dynamic_block_symbol, "U",
    top_pin_positions=(0.0, 15.0, 30.0, 40.0),
    top_pins=("L1", "L2", "L3", "PE"),
)
```

### Case C: Inserting a Component Without Vertical Space

**Problem**: Place a component parallel to the main line without breaking vertical flow.
**Solution**: Use `place_right`.

```python
main = builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
aux = builder.place_right(main, normally_open_symbol, "K", pins=("13","14"), spacing=40)
# Next add_component continues below `main`, NOT below `aux`
```

### Case D: Connecting Multi-Pole to Single-Pole

**Problem**: `auto_connect` assumes matching pole counts.
**Solution**: Disable auto-connect and use explicit connections.

```python
breaker = builder.add_component(three_pole_circuit_breaker_symbol, "F",
    auto_connect_next=False)
aux = builder.add_component(normally_open_symbol, "K")
builder.add_connection(breaker._index, 1, aux._index, 0)  # Pole 2 -> Pole 0
```

### Case E: Pin Configuration & Shared State

**Problem**: Split a terminal strip across two circuits but maintain sequential numbering.
**Solution**: Share the `state` object.

```python
state = create_autonumberer()
state, c1, _ = std_circuits.dol_starter(state, x=0, y=0, tm_top="X1", tm_bot="X2")
state, c2, _ = std_circuits.dol_starter(state, x=200, y=0, tm_top="X1", tm_bot="X3")
# X1 pins continue: c1 gets 1-N, c2 gets N+1-M
```

### Case F: Reusing Tags Across Circuits

**Problem**: A coil circuit and contact circuit should share the same K tag.
**Solution**: Use `reuse_tags`.

```python
coil_result = coil_builder.build()
contact_result = contact_builder.build(reuse_tags={"K": coil_result})
# contact_result uses K1, K2, ... from coil_result
```

### Case G: Fixed Tags (Non-Autonumbered)

**Problem**: You want a specific tag like "K_PUMP" instead of auto-generated "K1".
**Solution**: Use `tag_generators`.

```python
def fixed_pump(state):
    return state, "K_PUMP"

result = builder.build(tag_generators={"K": fixed_pump})
```

### Case H: Per-Instance Output Terminals

**Problem**: Each DOL starter instance needs its own output terminal.
**Solution**: Pass a list to `tm_bot`.

```python
state, circuit, _ = std_circuits.dol_starter(
    state, x=0, y=0,
    tm_top="X1",
    tm_bot=["X10", "X11", "X12"],
    count=3,
)
```

---

## 17. Recipe: Complex Control Loop

Start/stop latching circuit with parallel contact.

```python
from pyschemaelectrical import CircuitBuilder, create_autonumberer, render_system
from pyschemaelectrical.symbols import normally_open_symbol, normally_closed_symbol, coil_symbol

state = create_autonumberer()
builder = CircuitBuilder(state)
builder.set_layout(x=0, y=0, spacing=100, symbol_spacing=50)

# Top terminal
builder.add_terminal("X1")

# Start button (NO)
start = builder.add_component(normally_open_symbol, "S", pins=("13", "14"))

# Stop button (NC)
builder.add_component(normally_closed_symbol, "S", pins=("11", "12"))

# Coil
builder.add_component(coil_symbol, "K", pins=("A1", "A2"))

# Bottom terminal
builder.add_terminal("X2")

# Latch contact placed right of start button
latch = builder.place_right(start, normally_open_symbol, "K",
    pins=("13", "14"), spacing=40)

# Wire latch in parallel with start
builder.connect(latch.pin("13"), start.pin("13"), side_a="top", side_b="top")
builder.connect(latch.pin("14"), start.pin("14"), side_a="bottom", side_b="bottom")

result = builder.build()
render_system(result.circuit, "latching.svg")
```

---

## 18. Recipe: Complete Project

Full multi-page drawing set with PDF output.

```python
from pyschemaelectrical import Project, Terminal, ref, comp, term
from pyschemaelectrical.symbols import coil_symbol

project = Project(
    title="Pump Station",
    drawing_number="PS-001",
    author="J. Smith",
    project="Water Treatment",
    revision="01",
)

# Register terminals
project.terminals(
    Terminal("X1", description="Main 400V AC"),
    Terminal("X3", description="Fused 24V DC", bridge="all"),
    Terminal("X4", description="Ground", bridge="all"),
    Terminal("X10", description="Motor M1"),
    Terminal("X11", description="Motor M2"),
)

# Register circuits
project.dol_starter("motors", count=2,
    tm_top="X1", tm_bot=["X10", "X11"],
    tm_aux_1="X3", tm_aux_2="X4")

project.psu("psu",
    tm_top="X1", tm_bot_left="X3", tm_bot_right="X4")

project.spdt("relays", count=2,
    tm_top="X3", tm_bot_left="X4", tm_bot_right="PLC:DO")

# Custom inline circuit
project.circuit("custom_coils",
    components=[
        ref("PLC:DO"),
        comp(coil_symbol, "K", pins=("A1", "A2")),
        term("X4"),
    ],
    count=2,
    reuse_tags={"K": "relays"},
)

# Pages
project.front_page("docs/front.md")
project.page("Power Distribution", "psu")
project.page("Motor Circuits", "motors")
project.page("Control Relays", "relays")
project.page("Custom Coils", "custom_coils")
project.terminal_report()

# Build
project.build("pump_station.pdf")
```
