# PySchemaElectrical API Guide

**Version**: 2.0 (Deep Dive)
**Target Audience**: LLM Agents & Advanced Developers

This guide provides a masterful understanding of the `PySchemaElectrical` library. It goes beyond the basics to cover internal mechanics, edge cases, and the full "optionality" of the high-level APIs.

---

## 1. Core Concepts & Architecture

### The "Pure Core" Philosophy
The library separates **Layout/Logic** from **Rendering**.
1.  **State (Immutable)**: The `state` object (created by `create_autonumberer`) holds the current counters for tags (K1, K2...) and terminals (X1:1, X1:2...). It must be threaded through every function call.
2.  **Spec (Declarative)**: The `CircuitBuilder` builds a *Specification* (`CircuitSpec`), not the circuit itself immediately.
3.  **Build (Functional)**: The `.build()` method executes the spec, mutating the state and generating the `Circuit` object.

### The Coordinate System
- **Grid**: 1 Grid Unit = 5.0mm (`GRID_SIZE`).
- **Standard Spacing**:
    - Terminals are usually 10mm (2 Grids) apart.
    - Component vertical spacing is usually 50mm.
- **Direction**: Y-axis points **DOWN**. (0,0) is top-left.

---

## 2. CircuitBuilder: The Infinite Power Tool

The `CircuitBuilder` is a fluent interface for `ComponentSpec`. It is the preferred way to build *any* circuit logic.

### 2.1. Initialization & Layout Control
```python
state = create_autonumberer()
builder = CircuitBuilder(state)
builder.set_layout(
    x=0, y=0,
    spacing=150,        # Horizontal gap between REPEATED instances (count > 1)
    symbol_spacing=50   # Vertical gap between ADDED components (default y_increment)
)
```

### 2.2. Adding Components (`add_component`)
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
)
```

**Advanced Usage:**
- **Invisible Vertical Steps**: Set `y_increment=0` to overlay components or place them horizontally adjacent (using `x_offset`).
- **Hidden Terminals**: Pass specific kwargs supported by symbols, e.g., `builder.add_component(coil_symbol, ..., show_terminals=False)`.

### 2.3. Adding Terminals (`add_terminal`)
Terminals are special. They interact with the connection registry to create netlists.

**Signature:**
```python
builder.add_terminal(
    tm_id: str,                 # Physical Strip ID (e.g., "X1")
    poles: int = 1,
    pins: List[str] = None,     # Specific pin numbers (["1", "2"])
    logical_name: str = None,   # LOGICAL alias for mapping (e.g., "INPUT_A")
    label_pos: str = "left",    # Visual label placement
    **kwargs
)
```
**Power Feature: Logical Names**
Assign a `logical_name="MAIN_PWR"` to a terminal. Later, when using `standard_circuits`, you can map "MAIN_PWR" to any physical terminal ID (e.g., "X100") using `terminal_maps`.

### 2.4. Explicit Connections (`add_connection`)
Manual wiring when `auto_connect` isn't enough (e.g., feedback loops, parallel branches).

**Signature:**
```python
builder.add_connection(
    comp_idx_a: int,    # Index of component in builder order (0, 1, 2...)
    pole_idx_a: int,    # 0-indexed pole (0=L1, 1=L2, 2=L3)
    comp_idx_b: int,
    pole_idx_b: int,
    side_a: str = "bottom", 
    side_b: str = "top"
)
```
- **Indices**: The index refers to the order components were added to the builder. `0` is the first component.
- **Sides**: `top` (Input) vs `bottom` (Output).

---

## 3. Standard Circuits: Optionality & Overrides

The functions in `pyschemaelectrical.std_circuits` (like `dol_starter`, `psu`) are built using `CircuitBuilder`. They all share a powerful injection mechanism.

### 3.1. The `terminal_maps` Override
You can redirect internal logical connections to arbitrary physical terminals.

**Scenario**: You have a `power_distribution` circuit calling `psu` internally. The `psu` function expects `tm_top` (Input).
```python
# In standard_circuits/power.py
psu(..., tm_top="X1", ...)
```
**Override**:
If you call `power_distribution(..., terminal_maps={"PSU_INPUT": "X99"})`, the builder inside `psu` will resolve the logical input to "X99" instead of the default.

### 3.2. The `tag_generators` Override
You can force specific naming schemes for components.

**Scenario**: You want all Motors to differ from the standard "M1, M2" pattern, e.g., "M_PUMP_1".
```python
def my_motor_gen(state):
    return state, "M_PUMP_1"

dol_starter(..., tag_generators={"M": my_motor_gen})
```
This intercepts any request for a tag with prefix "M" and uses your generator.

---

## 4. Edge Cases & Solutions

### Case A: Feedback Loops (Connecting Bottom to Top)
**Problem**: `auto_connect` only goes Down. How do I wire a contact at the bottom back to a coil at the top?
**Solution**: Use `add_connection` or `register_connection`.
1.  **Visuals**: You must manually draw lines/polylines using `pyschemaelectrical.model.primitives.Line` if the standard "direct line" looks bad (crossing components). *However*, `add_connection` draws a straight line.
2.  **Registry**: Use `register_connection(state, "K1", "14", "X1", "1", side="... manual")` if specific netlist logic is needed.

### Case B: Non-Standard Pin Spacing (Dynamic Blocks)
**Problem**: You have a VFD (Variable Frequency Drive) with pins: `L1` (0mm), `L2` (15mm), `L3` (30mm), `PE` (40mm).
**Solution**: Use `top_pin_positions` in `dynamic_block_symbol`.
```python
builder.add_component(
    dynamic_block_symbol,
    "U",
    top_pins=("L1", "L2", "L3", "PE"),
    kwargs={
        "top_pin_positions": (0.0, 15.0, 30.0, 40.0) # Explicit X coords
    }
)
```

### Case C: Inserting a Component "Inline" without Vertical Space
**Problem**: You want to add a Voltage Monitor typically placed *parallel* to the line, but visually adjacent, without breaking the vertical flow.
**Solution**:
```python
# 1. Main Component
builder.add_component(..., y_increment=50) 
# 2. Parallel Component (Offset X, No Y increment)
builder.add_component(
    ..., 
    x_offset=50,    # Move Right
    y_increment=0,  # Don't move down global cursor
    auto_connect_next=False 
)
# 3. Next Main Component (Back at X=0)
builder.add_component(..., x_offset=0, y_increment=50)
```

### Case D: Connecting a 3-Pole Breaker to 1-Pole Auxiliaries
**Problem**: `auto_connect` assumes matching pole counts. If connecting 3-Pole -> 1-Pole, it connects Pole 0 -> Pole 0.
**Solution**:
1.  Disable auto-connect: `auto_connect_next=False`.
2.  Use `add_connection` to explicitly map leads.
```python
# Connect Breaker Pole 2 (Idx 1) to Aux Contact Pole 0
builder.add_connection(idx_breaker, 1, idx_aux, 0)
```

### Case E: "Ghost" Terminals (Passthrough)
**Problem**: You need a logical connection point that doesn't render a big terminal symbol (e.g., a simple wire junction).
**Solution**: Use a `ref_symbol` or a custom tiny Circle symbol, or simply rely on `register_connection` if visuals aren't strictly required. The `ref_symbol` is often used for page breaks but serves well as a labeled junction.

### Case F: Pin Configuration & Shared State
**Problem**: You want to split a long strip of terminals across two pages (circuits) but maintain sequential numbering (1, 2, 3 ... 4, 5, 6).
**Solution**: Share the `state` object.
```python
# Circuit 1
state = create_autonumberer()
state, c1, _ = dol_starter(state, tm_top="X1", ...)

# Circuit 2 (Continues X1 numbering)
state, c2, _ = dol_starter(state, tm_top="X1", ...)
```

---

## 5. Terminal Output & Exports

Terminals are more than just symbols; they are the interface to the physical world. `PySchemaElectrical` provides tools to generate manufacturing data.

### 5.1 Connection Registry (The Netlist)
Every time `auto_connect` runs or you use `register_connection`, the `state` updates its internal `TerminalRegistry`.

**Accessing Registry**:
```python
from pyschemaelectrical.system.connection_registry import get_registry, export_registry_to_csv

registry = get_registry(state)
export_registry_to_csv(registry, "terminal_connections.csv")
```

**Output Format**:
The CSV groups connections by Terminal Tag and Pin.
| Component From | Pin From | Terminal Tag | Terminal Pin | Component To | Pin To |
| :--- | :--- | :--- | :--- | :--- | :--- |
| K1 / K2 | 14 / 14 | X1 | 1 | M1 | U |

- **Top Side** ("From"): Usually internal components (Contactors, PLCs).
- **Bottom Side** ("To"): Usually field components (Motors, Sensors).

### 5.2 Terminal List Export
Simple list of all terminals used in a project.
```python
from pyschemaelectrical.utils.export_utils import export_terminal_list

used_terminals = ["X1", "X2", "X1"] # can contain duplicates
descriptions = {"X1": "Main Power", "X2": "Control 24V"}

export_terminal_list("terminals_bom.csv", used_terminals, descriptions)
```

---

## 6. Wire Labeling & Post-Processing

You can apply logic *after* the circuit is built but *before* rendering.

### Wire Labels
Add text labels to vertical wire segments (e.g., cross-references or wire colors).

```python
from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

labels = ["L1", "L2", "L3", "N", "PE"]
# Applies labels cyclically to found vertical connection lines
add_wire_labels_to_circuit(circuit, labels)
```

### Merging Circuits
Combine multiple sub-circuits into one page.
```python
from pyschemaelectrical.system.system import merge_circuits

main_c = Circuit()
merge_circuits(main_c, dol_circuit)
merge_circuits(main_c, safety_circuit)

render_system(main_c, "combined.svg")
```

---

## 7. Comprehensive Symbol Arguments Reference

### `coil_symbol`
- `show_terminals` (bool): If `False`, hides the vertical lead lines. useful for integrated electronics.

### `dynamic_block_symbol`
- `top_pin_positions` (Tuple[float]): Explicit X coords.
- `bottom_pin_positions` (Tuple[float]): Explicit X coords.
- `pin_spacing` (float): Global fallback spacing.

### `three_pole_motor_symbol`
- `pins`: Must be length 4 for PE rendering logic `(U, V, W, PE)`. If length 3, connects U,V,W but suppresses PE terminal graphic.

### `spdt_contact_symbol`
- `inverted` (bool): Flips the geometry so Common is at the TOP (Input) and NO/NC are at bottom. Default `False` (Common Bottom).

---
## 8. Internal Data Structures (For Debugging)

### `BuildResult`
Returned by `builder.build()`.
- `state`: The *new* autonumbering state (must be used for next operation).
- `circuit`: The `Circuit` object containing `elements` (visuals) and `symbols` (logical objects).
- `used_terminals`: List of terminal IDs touched by this builder.
- `component_map`: A Dictionary `{prefix: [tags]}` (e.g., `{"K": ["K1", "K2"]}`). Useful for retrieving generated tags to register external connections.

### `Symbol`
- `posts`: Dictionary `{port_id: Port}`.
- `skip_auto_connect`: (bool) Critical flag set by Builder when `auto_connect_next=False`.

---

## 9. Recipe: Complex Control Loop

Here is a pro-pattern for a start/stop latching circuit handling the builder manually.

```python
# 1. Start Button (NO)
builder.add_component(normally_open_symbol, "S", pins=("13", "14"))

# 2. Stop Button (NC)
builder.add_component(normally_closed_symbol, "S", pins=("11", "12"))

# 3. Latching Contact (Parallel to Start) - Needs Manual handling
# We add it efficiently with 0 height increment relative to Start
# But simplifying: Just add Coil, then wire back manually
builder.add_component(coil_symbol, "K", pins=("A1", "A2"))

# 4. Latch Contact (Aux on Contactor K)
# Place it explicitly to the right of Start Button
builder.add_component(normally_open_symbol, "K", pins=("13", "14"), x_offset=40, y_increment=0)

# Retrieving Indices:
# 0: Start, 1: Stop, 2: Coil, 3: Latch
# Wire Latch (3) in parallel with Start (0)
builder.add_connection(3, 0, 0, 0, side_a="top", side_b="top")       # Latch Top -> Start Top
builder.add_connection(3, 0, 0, 0, side_a="bottom", side_b="bottom") # Latch Bot -> Start Bot
```
