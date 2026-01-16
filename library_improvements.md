# Library Improvements & Roadmap

## 1. Introduction
This document serves as a comprehensive analysis and roadmap for the `pyschemaelectrical` (referred to as "the library") and its usage in the `auxillary_cabinet_v3` project. The goal is to evolve the library into a robust, type-safe, and logical foundation for electrical schematic generation, adhering to the "Pure Core, Imperative Shell" and "Data-Oriented Programming" philosophies.

## 2. Philosophy & Architecture

### Current State
*   **Data-Oriented**: The core models (`Symbol`, `Point`, `Circuit`) are correctly implemented as immutable dataclasses (`frozen=True`). This is a strong foundation.
*   **Pure Core**: The generation logic (`_create_single_circuit_from_spec`) is largely functional.
*   **Imperative Shell**: `CircuitBuilder` acts as the mutable builder/shell.
*   **Leakage**: There is leakage of "shell" concerns into the "core". For example, `Symbol` factories (`three_pole_factory`) make layout assumptions (translating by `pole_spacing`) that should ideally be handled by a layout engine or `CircuitBuilder`.

### Proposed Improvements
*   **Strict Separation**: Ensure `symbols` are purely data providers. They should define *what* they are, not *where* they are relative to others.
*   **Layout Engine**: Abstract the "stacking" and "flow" logic (currently manually calculated in `valves.py` via `x_off` and `y_inc`) into a more powerful Layout Engine within the library.

## 3. API & Usability (`CircuitBuilder`)

### Current Issues
1.  **Index-Based Connections**: `builder.add_connection(idx_a, pole_a, idx_b, pole_b)` is fragile. It requires the user to manually track indices returned by `add_component`.
2.  **Ambiguous Pin Resolution**: `_resolve_pin` in `builder.py` relies on heuristics (e.g., "if pin list length == poles * 2"). This is non-deterministic and hard to debug.
3.  **Broken Fluent Interface**: `add_component` returns `(self, index)`, breaking the method chaining potential of the builder pattern.

### Recommendations
*   **Tag-Based Connections**: references components by their **Logical Name** or **Tag**.
    ```python
    builder.add_component(..., logical_name="BREAKER_1")
    builder.connect("BREAKER_1", "L1", "MOTOR_1", "U")
    ```
*   **Explicit Ports**: Deprecate "Pole Index" based connections. Connect specific *Port IDs* (e.g., "L", "13", "A1") to *Port IDs*.
*   **Fluent Return Objects**: `add_component` should return a `ComponentRef` object (containing UUID/Tag) that can be used for connections, rather than an integer index. This enables:
    ```python
    ref_motor = builder.add_component(...)
    ref_breaker = builder.add_component(...)
    builder.connect(ref_breaker.pin("2"), ref_motor.pin("U"))
    ```

## 4. Type Safety & Error Handling

### Current Issues
*   **Loose Typing**: Widespread use of `Any`, especially in `state` management and `kwargs`.
*   **Runtime Errors**: Connection errors often manifest as "key error" or silent failures (missing lines) during rendering, rather than strict validation errors at build time.
*   **Fragile Constants**: Pin names are strings (e.g., "24V", "1"). Mismatches are easy.

### Recommendations
*   **Typed State**: Replace `Dict[str, Any]` state with a structured `GenerationState` dataclass.
*   **Validation Layer**: The `CircuitBuilder.build()` method should perform a complete graph validation pass before attempting layout:
    *   Verify all referenced components exist.
    *   Verify all referenced ports exist on those components.
    *   Check for simplified electrical rules (e.g., output-to-output shorts).
*   **Literal Types**: Use `Literal["top", "bottom", "left", "right"]` for side definitions instead of strings.

## 5. Symbols & Factories

### Current Issues
1.  **Rigid Port Remapping**: Multi-pole factories (`three_pole_factory`) forcibly remap ports to "1".."6". This destroys semantic port names (like "L1", "L2", "L3") if they were present in the single-pole symbol.
2.  **Alphabetical Labeling**: `create_pin_labels` sorts port keys alphabetically. This disregards the user's intended pin order (e.g., "L", "N", "PE" might become "L", "N", "P" -> sorted -> "L", "N", "PE" might change order if keys differ).
3.  **Dynamic Block Usage**: While `dynamic_block_symbol` supports explicit positioning, consuming code (like `valves.py`) is forced to manually calculate these arrays, leading to verbose boilerplate.

### Recommendations
*   **Preserve Port Semantics**: Multi-pole factories should allow retaining original port IDs with a suffix (e.g. "L_1", "L_2") or use a strictly documented mapping strategy that doesn't rely on hardcoded "1".."6" unless requested.
*   **Ordered Ports**: `Symbol` should store ports in an `OrderedDict` or list-preserving structure to maintain visual ordering for labeling.
*   **Smart Dynamic Blocks**:
    *   Input: `inputs=["24V", "0V"]`, `outputs=["L1", "N"]`
    *   Auto-layout: The block should calculate its own width and pin positions based on simple "spacing" and "margin" rules, without requiring explicit coordinate arrays from the user.

## 6. Layout & Connections

### Current Issues
*   `valves.py` manually calculates `group_base_x`, `terminal_step_x`, `block_y_offset` to achieve a "staggered" connection to the valve block. This geometric logic is hardcoded in the user script.

### Recommendations
*   **Grid System**: Introduce a formal Grid system. `width=5` should mean 5 grid units, not "5 * GRID_SIZE calculated manually".
*   **Layout Containers**:
    *   `RowLayout`, `ColumnLayout`, `StaggeredLayout` (for the valve terminal stairs).
    *   The user should define *structure*, the library should calculate *coordinates*.

## 7. Immediate Action Items (Refactoring Protocol)

1.  **Fix `create_pin_labels`**: Stop sorting keys. Iterate through the `pins` tuple provided by the user and look up ports.
2.  **Fix `CircuitBuilder` Types**: Add type hints to `builder.py` to remove `Any`.
3.  **Standardize Dynamic Blocks**: Refactor `dynamic_block_symbol` to be more robust and less repetitive.

## 8. Investigation Findings (Resolved)

### 8.1 State Persistence
*   **Finding**: State is a purely ephemeral dictionary (`{'tags': {}, ...}`). It exists only during the runtime of the Python script.
*   **Impact**: Good for "clean build" reproducibility. No "stale state" issues.
*   **Recommendation**: Keep it this way for now. If incremental builds are needed later, introduce a `StateManager` interface that can save/load JSON, but default to in-memory.

### 8.2 Auto-Connect Logic
*   **Finding**: Logic is purely **Geometric**, not Topological. It finds "Down" ports on Top symbol and "Up" ports on Bottom symbol, and connects them if their X-coordinates match within 0.1mm.
*   **Impact**:
    *   Fragile: Slight misalignments break connections.
    *   Blind: Connects anything that aligns, regardless of electrical validity.
*   **Recommendation**:
    *   **Graph-Awareness**: `CircuitBuilder` should maintain a logical Netlist. `auto_connect` should only draw lines for logically connected ports.
    *   **Port Aliasing**: Keep the geometric fallback for simple "stacking" (like terminal blocks), but prefer explicit connections.

### 8.3 Wire Labeling
*   **Finding**: Wire labeling is **Index-Based**. It finds all vertical lines in the final circuit and applies labels from a list *in the order the lines were created/added*.
*   **Impact**:
    *   **Dangerous**: If the build order changes (e.g., drawing right-to-left instead of left-to-right), wire labels will be applied to the wrong wires.
    *   No verification that the "RD" label is actually on a "Live" wire.
*   **Recommendation**:
    *   **Topological Labeling**: Wire properties (color, cross-section) should be attributes of the **Connection/Net** in `CircuitBuilder`.
    *   **Render-Time Labels**: The renderer should look at the `Connection` object to decide what label to draw next to the line, rather than post-processing the geometry list.

## 9. QC Review Findings (Agent Analysis)

### 9.1 Confirmed Issues
*   **Ambiguous Pin Resolution**: Verified in `builder.py: _resolve_pin`. The heuristic `len(pins) == poles * 2` is indeed fragile and opaque.
*   **Index-Based Connections**: Verified in `builder.py`. The builder relies entirely on list indices (`comp_idx_a`), which makes refactoring circuit definitions extremely error-prone.
*   **Broken Fluent Pattern**: Verified in `builder.py`. `add_component` returns `(self, index)`, forcing the user to break the chain to store the index.

### 9.2 Wire Labeling Logic
*   **Finding**: Wire labeling is handled in `layout.py: auto_connect_labeled`. It uses `_find_matching_ports` which sorts ports by X-coordinate.
*   **Problem**: If the geometry of the symbol changes (e.g. pins move slightly), the sorted order might change, causing "L1" wire specs to be applied to "L2" wires if they cross or shift.
*   **Refinement**: Wire specifications must be bound to the **Logical Connection** (Port A -> Port B), not the geometric line.

### 9.3 Missing Layout Primitives
*   **Finding**: `valves.py` implements a "Staggered" layout manually.
*   **Recommendation**: Add `StaggeredLayout` or `StepLayout` to `pyschemaelectrical.layout`.
    ```python
    # Concept
    layout.chain(
        components=[t1, t2, t3, t4, t5],
        pattern="diagonal", 
        step=(10, 10)
    ).connect_to(shared_block)
    ```

### 9.4 "ComponentRef" Proposal
To solve the Index-Based Connection issue, introduce a `ComponentRef` handle:
```python
class ComponentRef:
    builder: CircuitBuilder
    index: int
    tag: str

    def pin(self, pin_name: str) -> 'PortRef':
        return PortRef(self, pin_name)

# Usage
m1 = builder.add(Motor, ...)
k1 = builder.add(Contactor, ...)
builder.connect(m1.pin("U"), k1.pin("2"))
```
This restores the imperative fluent chain while keeping the underlying index-based engine (temporarily) until a full graph engine is built.
