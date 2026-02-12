# Suggestions for PySchemaElectrical

## Claude Code Usage Suggestions

Based on usage patterns across 14 sessions.

### Front-load context to avoid dead-end sessions

Provide file paths and specific context upfront instead of relying on Claude to discover them. Pointing to the exact file and describing what you want changed eliminates wasted rounds.

Example prompt:
```
Fix the calculate_tax function in src/exercises/tax_calculator.py — it should
handle the case where income is negative by returning 0 instead of raising an
error. Here's the current behavior: [paste error]
```

### Use "minimal first" framing to prevent over-engineering

Explicitly state complexity constraints in prompts to avoid bloated solutions. Adding a complexity constraint is faster than correcting after the fact.

Example prompt:
```
Write a simple Python script to seed the database from a CSV file. Requirements:
no management commands, no error handling beyond basic try/except, no
abstractions — just read the CSV and create objects. Under 30 lines.
```

### Batch conceptual questions into structured sessions

Group related learning questions into a single well-structured prompt so Claude has better context about your knowledge level.

Example prompt:
```
I'm learning Django for a recipe website project. Answer each concisely with a
short code example:
1. How does ListView work with custom querysets?
2. How do I add pagination to a ListView?
3. What's the difference between get_queryset() and get_context_data()?
4. How do I filter recipes by category in the URL?
```

### Features to try

- **Custom Skills** — Reusable prompts via `/command` for repetitive workflows (e.g., `/django-setup` encoding your "keep it minimal" preference).
- **Hooks** — Auto-run linting or syntax checks after edits to catch bugs before they snowball into multi-round debugging.
- **Task Agents** — Spawn focused sub-agents for library exploration or parallel investigation to reduce wrong-approach friction.

---

## API Improvement & Refactoring Suggestions

Suggestions for making circuit building easier while preserving full optionality.

### 1. Replace state tuple threading with a StateManager

**Problem:** Every function returns `(state, circuit, used_terminals)` requiring manual destructuring. Forgetting to thread state correctly causes silent failures. Callback signatures like `(state, x, y, tag_gens, terminal_maps, instance)` are overloaded.

**Suggestion:** Introduce a `StateManager` context that tracks mutations internally:

```python
# Before (current)
state = create_autonumberer()
state, circuit1, _ = dol_starter(state, 0, 0, "X1", "X2", "X2")
state, circuit2, _ = psu(state, 150, 0, "X3", "X4")

# After (proposed)
with StateManager() as mgr:
    circuit1, _ = dol_starter(mgr, 0, 0, "X1", "X2", "X2")
    circuit2, _ = psu(mgr, 150, 0, "X3", "X4")
    final_state = mgr.state
```

The old `(state, circuit, terminals)` signature can remain as a compatibility layer. `StateManager` would wrap the dict internally and expose `next_tag()`, `next_terminal_pins()` etc. as methods.

### 2. Named component references in CircuitBuilder

**Problem:** Components are referenced by integer index. Manual index tracking is fragile and hard to read:
```python
# Current - what does (0, 0, 1, 0) mean?
builder.add_connection(0, 0, 1, 0, side_a="bottom", side_b="top")
```

**Suggestion:** Allow logical names for components:

```python
builder.add_terminal("tm_top", tm_id, poles=3, name="input")
builder.add_component(breaker_symbol, "F", name="breaker")
builder.connect("input", "breaker")  # named references
```

Keep integer indexing as a fallback for programmatic use. This also improves error messages — `"Component 'breaker' not found"` vs `"Index 3 out of range"`.

### 3. CircuitComposer for multi-circuit systems

**Problem:** Composing multiple circuits requires manually calling each factory, threading state, collecting elements, and calling `merge_circuits` or extending element lists. `power_distribution()` is 100 lines of manual wiring.

**Suggestion:** A high-level composition API:

```python
composer = CircuitComposer(state)
composer.add(changeover, x=0, y=0, tm_top_left="X1", tm_top_right="X2", tm_bot="X3")
composer.add(psu, tm_top="X4", tm_bot="X5")  # auto-positioned after previous
composer.layout("horizontal", spacing=150)
state, circuit = composer.build()
render_system(circuit, "output.svg")
```

`CircuitComposer` would handle state threading, positioning, and merging internally. Individual factory calls remain available for custom layouts.

### 4. Standardize function signatures with config dataclasses

**Problem:** Inconsistent parameter naming and structure across std_circuits:
- `dol_starter()` has 20+ parameters
- `psu()` has 8 parameters + `**kwargs`
- Terminal params: `tm_top/tm_bot/tm_bot_right` vs `tm_top_left/tm_top_right/tm_bot`
- Some params are accepted but ignored (e.g., `terminal_offset` in `psu()`)

**Suggestion:** Introduce config dataclasses:

```python
@dataclass
class CircuitConfig:
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_MOTOR
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_DEFAULT
    count: int = 1

@dataclass
class TerminalConfig:
    input_main: str
    output_main: str
    output_aux: Optional[str] = None

# Usage
def dol_starter(state, x, y, terminals: TerminalConfig,
                config: CircuitConfig = CircuitConfig()):
    ...
```

Keep the current explicit-parameter signatures as the default for backwards compatibility. The config approach becomes an alternative for power users building reusable templates.

### 5. Consolidate layout configuration

**Problem:** Spacing and layout defaults are split across three overlapping structures: `StandardSpacing`, `LayoutDefaults`, and `CircuitLayouts` — all in `model/constants.py`.

**Suggestion:** Merge into a single `LayoutConfig`:

```python
@dataclass
class LayoutConfig:
    # Per circuit-type spacing
    motor_circuit_spacing: float = 150
    motor_symbol_spacing: float = 50
    power_circuit_spacing: float = 150
    power_symbol_spacing: float = 60
    single_pole_spacing: float = 100

    # Global
    grid_size: float = 5.0
```

Allow per-project override without forking constants:
```python
from pyschemaelectrical import set_project_defaults
set_project_defaults(LayoutConfig(motor_circuit_spacing=200))
```

### 6. Flatten imports for common use cases

**Problem:** Users need deep imports for basic operations:
```python
from pyschemaelectrical.std_circuits import dol_starter
from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.system import render_system
```

**Suggestion:** Export standard circuit factories from the top-level package:

```python
# Proposed: works alongside existing deep imports
from pyschemaelectrical import (
    create_autonumberer, render_system,
    dol_starter, psu, changeover, emergency_stop,
    spdt, no_contact, coil, power_distribution,
)
```

The `std_circuits` subpackage import remains for discoverability and namespacing, but common factories are also available at the top level.

### 7. Auto-register connections in CircuitBuilder

**Problem:** `register_connection()` is called manually throughout std_circuits (50+ lines in `dol_starter` alone). Connection registration is disconnected from the actual wiring — what's rendered and what's registered can drift apart.

**Suggestion:** When `CircuitBuilder.build()` wires two components, auto-register the connection:

```python
# Before: manual registration after building
register_connection(state, "X1", "1", "F1", "1", "top")
register_connection(state, "X1", "2", "F1", "3", "top")
register_connection(state, "X1", "3", "F1", "5", "top")

# After: builder registers during build()
builder.add_terminal("tm_top", "X1", poles=3, register=True)
builder.add_component(breaker, "F", register=True)
# Connections auto-registered when build() wires them
```

Manual `register_connection()` stays available for edge cases outside the builder.

### 8. Simplify the layout generator callback

**Problem:** `create_horizontal_layout()` requires a callback with 6 parameters:
```python
generator_func(state, x, y, tag_generators, terminal_maps, instance)
```

Most generators ignore `instance` and just forward `tag_generators`/`terminal_maps`.

**Suggestion:** Bundle into a context object:

```python
@dataclass
class GeneratorContext:
    state: Dict
    x: float
    y: float
    instance: int
    tag_generators: Dict
    terminal_maps: Dict

def create_horizontal_layout(
    state, start_x, start_y, count, spacing,
    generator: Callable[[GeneratorContext], Tuple[Dict, Circuit, List]]
):
    ...
```

A simple adapter wraps existing callbacks:
```python
def create_single_dol(ctx: GeneratorContext):
    return dol_starter(ctx.state, ctx.x, ctx.y, ...)
```

### 9. Add render_to_string and auto-sizing

**Problem:** `render_system()` only writes to files. Width/height are positional and must be guessed. No way to render to a string for testing or embedding.

**Suggestion:**

```python
# Render to string (useful for tests and embedding)
svg_string = render_to_string(circuit)

# Auto-size based on circuit bounding box
render_system(circuit, "output.svg")  # auto width/height

# Explicit sizing remains available
render_system(circuit, "output.svg", width=800, height=600)
```

### 10. Extract a PortResolver from builder internals

**Problem:** `_resolve_pin()` in `builder.py` is 60 lines of conditional logic with heuristics for terminals vs symbols vs fallback. Comments say "This function uses several heuristics."

**Suggestion:** Extract into a testable, documented `PortResolver`:

```python
class PortResolver:
    def resolve(self, component: ComponentData, pole_idx: int, side: str) -> str:
        """Resolve port ID for a component at a given pole and side."""
        ...

    def validate(self, symbol: Symbol, port_id: str) -> bool:
        """Check that a port exists on the symbol."""
        ...
```

This makes the resolution logic independently testable and easier to extend for new component types.

---

## Priority Order

| Priority | Suggestion | Impact | Effort |
|----------|-----------|--------|--------|
| 1 | Named component references (#2) | High | Medium |
| 2 | Flatten imports (#6) | High | Low |
| 3 | Auto-register connections (#7) | High | Medium |
| 4 | StateManager (#1) | High | High |
| 5 | Consolidate layout config (#5) | Medium | Low |
| 6 | CircuitComposer (#3) | High | High |
| 7 | Standardize signatures (#4) | Medium | Medium |
| 8 | Simplify generator callback (#8) | Medium | Low |
| 9 | render_to_string + auto-sizing (#9) | Medium | Low |
| 10 | Extract PortResolver (#10) | Medium | Medium |
