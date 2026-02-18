# PySchemaElectrical — Codebase Audit & TODO

**Last updated:** 2026-02-18
**Scope:** Full codebase audit (FP/DRY/quality/docs/tests) + `auxillary_cabinet_v3` real-world usage analysis
**Tool analysis:** `ruff check --select ALL` (1053 issues), `ty check` (54 diagnostics), `pytest` (224 tests, 79% coverage)

---

## 0. Questions & Uncertainties for Maintainer

These require your input before the relevant tasks can proceed. Please answer inline.

### Q1: `text_anchor` vs `anchor` in `create_pin_label_text()`

`model/parts.py:85` passes `text_anchor=anchor` to `Text()`, but the `Text` dataclass field
is named `anchor` (not `text_anchor`). `ty` flags this as `unknown-argument`. This _should_ be
a runtime crash whenever pin labels are created, yet all 224 tests pass and the real project
renders correctly.

**Question:** Is there dynamic handling (e.g. `**kwargs` passthrough, SVG renderer fallback)
that silently absorbs `text_anchor`? Or is pin label creation simply never exercised by the
current tests? Should this be renamed to `anchor=anchor`?

> **Answer:**

### Q2: Terminal name collision

Two classes are named `Terminal`:
1. `terminal.py:Terminal(str)` — immutable string subclass with metadata (bridge, description, pin_prefixes)
2. `symbols/terminals.py:Terminal(Symbol)` — frozen dataclass representing a rendered terminal symbol

These can shadow each other on import. The real project only uses (1) directly.

**Question:** Should `symbols/terminals.py::Terminal` be renamed to `TerminalSymbol`? Or is the current
shadowing acceptable because users never import both?

> **Answer:**

### Q3: `from __future__ import annotations` cleanup scope

9 files still have `from __future__ import annotations`. With `requires-python = ">=3.12"`, these
are unnecessary. However, removing them changes evaluation semantics (annotations become real objects
instead of strings), which could affect any runtime annotation inspection.

**Question:** Is any code doing runtime annotation inspection (`typing.get_type_hints()`, etc.)?
If not, should we remove all 9 `__future__` imports?

Files: `wire_labels.py`, `motor.py`, `control.py`, `safety.py`, `power.py`, `system_analysis.py`,
`parts.py`, `utils.py`, `terminal_bridges.py`, `plc.py`

> **Answer:**

### Q4: `GenerationState` vs `dict[str, Any]` state threading

Many functions accept `state: dict[str, Any] | GenerationState`. `ty` flags 5+ diagnostics
because `GenerationState` (frozen dataclass) doesn't support `state.copy()`, `state.get()`, or
`state["key"]` subscript operations.

**Question:** Should we standardize on ONE state type? Options:
- (A) Keep dual support but add proper type narrowing/guards
- (B) Migrate fully to `GenerationState` with `.replace()` semantics
- (C) Keep `dict` as the canonical type and remove `GenerationState`

> **Answer:**

### Q5: `auto_*` functions — safe to remove?

`generate_pin_range()`, `auto_terminal_pins()`, `auto_contact_pins()`, `auto_thermal_pins()`,
`auto_coil_pins()` in `autonumbering.py` have zero external usage. The real project uses static
pin tuples (`ComponentPins.COIL = ("A1", "A2")`). But some are tested in `test_utils_advanced.py`.

**Question:** Remove these functions AND their tests? Or keep as "utility" functions for future users?

> **Answer:**

### Q6: `power_supply.py` still uses old API

`auxillary_cabinet_v3/power_supply.py` still uses `_find_symbol_by_label()` (line 47) and
`hasattr(e, "ports")` iteration (lines 219, 237) despite `Circuit.get_symbol_by_tag()` being
added. Also returns `Tuple[Any, Circuit, List]` instead of `BuildResult`.

**Question:** Should updating `power_supply.py` to use the new API be tracked here, or is that
tracked separately in the `auxillary_cabinet_v3` repo?

> **Answer:**

### Q7: Exception class naming — `Error` suffix convention

Python convention (PEP 8) says exception names should end in `Error`. Current names:
`TagReuseExhausted`, `TerminalReuseExhausted`, `WireLabelCountMismatch` — missing `Error` suffix.

**Question:** Rename to `TagReuseError`, `TerminalReuseError`, `WireLabelMismatchError`?
This is a breaking change for any code catching these by name.

> **Answer:**

### Q8: `DeviceTemplate` system — port to library?

`auxillary_cabinet_v3/device_templates.py` defines a `DeviceTemplate` + `PinDef` system for
declaring field device connections (sensors, valves, motors) with auto-numbered terminal pins
and PLC reference tags. This is generic enough to be library functionality.

**Question:** Should `DeviceTemplate`, `PinDef`, and `generate_field_connections()` be ported
into the library (e.g. as `pyschemaelectrical.field_devices` module)? Or keep project-specific?

> **Answer:**

### Q9: `PlcMapper` and `Project` — document as mutable builders?

The FP audit found that `PlcMapper`, `Project`, and `CircuitBuilder` all use mutable accumulation
patterns (`.append()`, dict mutation, `return self`). `Circuit` is already documented as an
intentional mutable exception. These three classes follow the same builder pattern.

**Question:** Should we:
- (A) Document all three as intentional mutable builders (like Circuit) in CLAUDE.md
- (B) Refactor PlcMapper to functional patterns (return new state instead of mutating self)
- (C) Accept the builder pattern as-is but add warnings about non-reusability

> **Answer:**

---

## 1. Critical Bugs (Previously Found — All Fixed)

All 4 critical bugs from the original audit have been resolved:

- [x] ~~1.1 Path translation/rotation silent no-op~~ *(done — `_translate_path_d`, `_rotate_path_d`)*
- [x] ~~1.2 `_resolve_registry_pin()` returns `None` unsafely~~ *(done)*
- [x] ~~1.3 Division-by-zero in blade calculation~~ *(done — `create_extended_blade`)*
- [x] ~~1.4 `Project.set_pin_start()` unsafe dict mutation~~ *(done)*

---

## 2. New Bug: `create_pin_label_text()` wrong keyword argument

**Severity:** Likely critical (but see Q1 above)
**File:** `model/parts.py:85`
**Tool:** `ty check` reports `unknown-argument` error

```python
return Text(
    ...
    text_anchor=anchor,  # <- Text dataclass has `anchor`, not `text_anchor`
)
```

The `Text` dataclass (`primitives.py:66`) has `anchor: str = "middle"`. The call uses
`text_anchor=anchor` which is not a valid parameter.

### Task: Fix `text_anchor` keyword (pending Q1 answer)

- [ ] Change `text_anchor=anchor` to `anchor=anchor` in `model/parts.py:85`
- [ ] Add test that `create_pin_label_text()` returns a `Text` with correct anchor value
- [ ] Verify no other callers use `text_anchor` anywhere

---

## 3. Type Safety — `ty check` Diagnostics (54 total)

These are real type errors reported by `ty check`. Grouped into sub-agent-sized tasks.

### Task 3.1: Fix `None`-safety in `builder.py` and `project.py`

`ty` reports 3 cases where `None` can flow into functions that require `str` or `list`.

- [ ] `builder.py:685` — `prefix` is `str | None`, passed to `next_tag(state, prefix)` which requires `str`.
  Add guard: `if prefix is None: raise ValueError(...)`
- [ ] `project.py:464` — `cdef.components` is `list[...] | None`, passed to `build_from_descriptors()`.
  Add guard: `if cdef.components is None: raise ValueError(...)`
- [ ] `project.py:477` — `cdef.builder_fn` is `Callable | None`, called directly.
  Add guard: `if cdef.builder_fn is None: raise ValueError(...)`

### Task 3.2: Fix type mismatches in `std_circuits/motor.py`

`ty` reports 3 errors where `instance_tm_bot` (typed `Unknown | str | list[str]`) flows into
functions expecting `str`.

- [ ] `motor.py:136` — `instance_tm_bot` passed to `next_terminal_pins()` which expects `str`
- [ ] `motor.py:181` — `instance_tm_bot` passed to `multi_pole_terminal_symbol()` which expects `str`
- [ ] `motor.py:264` — `instance_tm_bot` passed to `register_connection()` which expects `str`
- [ ] Add proper type narrowing: `assert isinstance(instance_tm_bot, str)` or explicit cast

### Task 3.3: Fix `TerminalBlock` constructor type mismatch

`symbols/terminals.py:137` — Passes `tuple(all_elements)` to `elements=` parameter which
expects `list[Element]`.

- [ ] Change to `elements=list(all_elements)` or update `TerminalBlock` to accept `tuple`

### Task 3.4: Fix `merge_circuits` type narrowing

`system/system.py:107` — Assignment fails because `circuits` narrows to
`(Circuit & Top[list[Unknown]]) | list[Circuit]` after `isinstance` check.

- [ ] Add explicit `cast()` or restructure the type narrowing

### Task 3.5: Fix `autonumbering.py` dual-type state handling

`ty` reports 5 errors where `dict[str, Any] | GenerationState` is used but only dict operations
are called (`state.copy()`, `state["tags"]`, `state.get()`).

- [ ] Depends on Q4 answer — either add type guards or unify the state type
- [ ] Fix `autonumbering.py:45` — `state["tags"]` on `GenerationState` which has no `__getitem__`
- [ ] Fix `autonumbering.py:61-62` — `state.copy()` not available on `GenerationState`
- [ ] Fix `autonumbering.py:118` — `state["pin_counter"]` subscript
- [ ] Fix `autonumbering.py:149,163` — `.get()` and `.copy()` on union type
- [ ] Fix `utils/utils.py:29` — same `.copy()` issue

### Task 3.6: Fix test type errors

`ty` reports 12 errors in test files — mostly accessing attributes on `Element` base type that
only exist on subclasses (`Line.start`, `Text.content`, `Circle.style`).

- [ ] Add `assert isinstance(elem, Line)` or similar type narrowing before attribute access
- [ ] Fix `test_system.py:8-9` — passing `list[str]` where `list[Element]` expected
- [ ] Fix `test_renderer.py:31-45` — chain of `.find()` calls returning `Element | None`
- [ ] Fix `test_parts.py:27` — accessing `.style` on generic `Element`

---

## 4. Type Hint Improvements — `ruff` ANN findings

`ruff --select ALL` found 44 missing type annotations (ANN001), 28 missing return types
(ANN201/ANN202), 23 missing `**kwargs` types (ANN003), and 17 `Any` usages (ANN401).

### Task 4.1: Add missing parameter type annotations (44 instances)

Key files with missing annotations:

- [ ] `builder.py` — `state: Any` in `__init__`, `generator(state)` closures (lines 130, 151)
- [ ] `std_circuits/*.py` — Multiple factory functions with untyped `state` parameter
- [ ] `plc.py` — Several methods with untyped parameters
- [ ] `utils/renderer.py` — `_parse_dim(val, default)` completely untyped

### Task 4.2: Add missing return type annotations (28 instances)

- [ ] `builder.py:118` — `BuildResult.__iter__()` missing return type
- [ ] `builder.py:130,151` — Inner `generator()` functions missing return types
- [ ] All `__init__` methods (9 instances) — add `-> None`
- [ ] Private functions across `builder.py`, `plc.py`, `renderer.py`

### Task 4.3: Replace `Any` with specific types (17 instances)

Priority replacements:

- [ ] `builder.py:173` — `state: Any` -> `dict[str, Any] | GenerationState`
- [ ] `builder.py:190` — `tm_id: Any` -> `str | Terminal`
- [ ] `descriptors.py:37` — `symbol_fn: Any` -> `Callable[..., Symbol]`
- [ ] `builder.py:576` — `tag_generators: dict | None` -> `dict[str, Callable[[dict], tuple[dict, str]]] | None`
- [ ] `builder.py:577` — `terminal_maps: dict | None` -> `dict[str, Any] | None`
- [ ] `system/system_analysis.py:64` — `direction_filter: Any | None` -> `Vector | None`
- [ ] `autonumbering.py:121` — `terminal_tag: str` -> `str | Terminal` (code uses `getattr(terminal_tag, "pin_prefixes", None)`)

### Task 4.4: Tighten `GenerationState.terminal_registry` type

`model/state.py:31` — `TerminalRegistry | dict` is too loose.

- [ ] Tighten to `TerminalRegistry` only (pending Q4)
- [ ] Or specify dict structure: `TerminalRegistry | dict[str, Any]`

### Task 4.5: Define `SymbolFactory` type alias

Several functions accept `Callable` where they mean "function returning Symbol".

- [ ] Define `SymbolFactory = Callable[..., Symbol]` in `model/core.py` or a types module
- [ ] Use in `builder.py:add_component()`, `descriptors.py:CompDescriptor`, `parts.py` factories

---

## 5. Code Quality — `ruff` Complexity & Style

### Task 5.1: Reduce function complexity (14 C901 violations)

`ruff` reports 14 functions exceeding complexity threshold (>10):

- [ ] `builder.py:483` — `build()` complexity 22 -> break into sub-methods
- [ ] `builder.py:611` — `_create_single_circuit_from_spec()` complexity 46 -> largest single function (302 lines), decompose into phase functions:
  - `_phase1_tag_and_state()` — state mutation & component realization
  - `_phase2_register_connections()` — connection registration
  - `_phase3_instantiate_symbols()` — symbol placement
  - `_phase4_render_graphics()` — connection line rendering
- [ ] Other files with C901: `plc.py`, `project.py`, `std_circuits/motor.py`, `std_circuits/power.py`, `std_circuits/control.py`

### Task 5.2: Fix line-length violations (12 E501)

- [ ] `builder.py` — 7 lines over 88 chars (lines 180, 725, 736, 747, 757, 779, 784, 824)
- [ ] `layout/wire_labels.py` — 2 lines (14, 199)
- [ ] Break long lines by extracting local variables or reformatting conditions

### Task 5.3: Remove `from __future__ import annotations` (9 files, pending Q3)

- [ ] `layout/wire_labels.py`
- [ ] `std_circuits/motor.py`, `control.py`, `safety.py`, `power.py`
- [ ] `system/system_analysis.py`
- [ ] `model/parts.py`
- [ ] `utils/utils.py`, `terminal_bridges.py`
- [ ] `plc.py`

### Task 5.4: Move function-body imports to module level (31 PLC0415)

31 imports are inside function bodies instead of at module level. Most are in:

- [ ] `builder.py` — exception imports in `generator()` closures
- [ ] `model/parts.py` — `from primitives import Text` inside `create_pin_label_text()`
- [ ] `symbols/*.py` — scattered lazy imports
- [ ] Note: Some may be intentional to avoid circular imports — verify before moving

---

## 6. Dead Code Removal

### Task 6.1: Remove unused `auto_*` functions (pending Q5)

`utils/autonumbering.py:185-231` — 4 functions + 1 helper with zero external usage:

- [ ] Remove `auto_terminal_pins()` (line 224)
- [ ] Remove `auto_contact_pins()` (line 219)
- [ ] Remove `auto_thermal_pins()` (line 229)
- [ ] Remove `auto_coil_pins()` (line 214)
- [ ] Remove `generate_pin_range()` (line 191)
- [ ] Make `increment_tag()` and `format_tag()` private (`_` prefix) — they are just public aliases for private functions
- [ ] Update/remove tests in `test_utils_advanced.py` that test these functions
- [ ] Verify nothing in `__init__.py` exports these

### Task 6.2: Remove `next_contact_pins()` (unused)

`utils/utils.py:64-95` — Generates SPDT contact pin tuples (`"11","12","14"`, `"21","22","24"`).
Never used in codebase. Superseded by `next_terminal_pins()` with `pin_prefixes`.

- [ ] Remove `next_contact_pins()` from `utils/utils.py`
- [ ] Verify no external consumers depend on it

### Task 6.3: Remove commented-out code (12 ERA001)

`ruff` found 12 instances of commented-out code. Review and remove:

- [ ] Scan all files for `# old code`, `# disabled`, `# commented out` patterns
- [ ] Remove confirmed dead commented-out code
- [ ] Convert legitimate notes to proper docstrings or TODO comments

---

## 7. Validation & Error Handling

### Task 7.1: Add input validation to factory functions

- [ ] `model/parts.py:290` — `three_pole_factory()`: validate `pole_spacing > 0`
- [ ] `model/parts.py:339` — `two_pole_factory()`: same `pole_spacing` validation
- [ ] `symbols/terminals.py:138-157` — `terminal_symbol()`: validate `label_pos` is "left" or "right"
- [ ] `plc.py:127-136` — `sensor_type()`: validate `pins` is non-empty
- [ ] `plc.py:138-160` — `sensor()`: validate `name` doesn't already exist

### Task 7.2: Add file I/O error handling

Currently 5 file I/O locations have no or overly broad error handling:

- [ ] `utils/terminal_bridges.py:274` — Replace bare `except Exception` with specific exceptions
  (`FileNotFoundError`, `PermissionError`, `csv.Error`). This is the worst offender.
- [ ] `utils/export_utils.py:25` — `export_terminal_list()`: no try-except on CSV write at all
- [ ] `utils/terminal_bridges.py:160` — `read_csv_connections()`: no error handling on `open()`
- [ ] `rendering/typst/compiler.py:154-156` — template file read/write: no error handling
- [ ] `system/system_analysis.py:173-250` — `export_terminals_to_csv()` and
  `export_components_to_csv()`: no `PermissionError`/`OSError` handling

### Task 7.3: Fix silent failure in renderer

`utils/renderer.py:203-214` — `_parse_dim()` silently swallows `ValueError` with a bare `pass`.

- [ ] Add `warnings.warn()` when invalid dimension string is encountered
- [ ] Or raise `ValueError` with helpful message describing valid formats

### Task 7.4: Improve `_find_matching_ports()` duplicate handling

`layout/layout.py:85-90` — When multiple `up_ports` share the same X position, only the first
is matched. The rest are orphaned silently.

- [ ] Remove matched ports from the candidate set (consume them)
- [ ] Or add a warning when duplicates are detected

---

## 8. Exception Quality

### Task 8.1: Add `Raises` sections to docstrings

These functions raise exceptions but don't document them:

- [ ] `builder.py:378-410` — `connect()`: can raise `PortNotFoundError`, `ComponentNotFoundError`
- [ ] `builder.py:465-482` — `_validate_connections()`: raises `ComponentNotFoundError`, `PortNotFoundError`
- [ ] `builder.py:483-609` — `build()`: raises `TagReuseExhausted`, `TerminalReuseExhausted`, `WireLabelCountMismatch`
- [ ] `descriptors.py:71-130` — `build_from_descriptors()`: raises `ValueError`
- [ ] `plc.py:108-136` — `sensor_type()`: raises `ValueError`
- [ ] `plc.py:138-160` — `sensor()`: raises `ValueError`

### Task 8.2: Rename exception classes (pending Q7)

- [ ] `TagReuseExhausted` -> `TagReuseError`
- [ ] `TerminalReuseExhausted` -> `TerminalReuseError`
- [ ] `WireLabelCountMismatch` -> `WireLabelMismatchError`
- [ ] Keep old names as aliases for one release cycle

---

## 9. Test Coverage Gaps

**Current:** 224 tests, 79% line coverage (2634/3350 statements). Key uncovered areas:

### Task 9.1: Test `builder.py` (74% coverage -> target 90%+)

Builder coverage has improved significantly but key paths remain untested:

- [ ] Test `ComponentRef.pin()` and `ComponentRef.pole()` — return `PortRef`
- [ ] Test `add_reference()` — fixed tag generators for PLC references
- [ ] Test `add_matching_connection()` — horizontal port-matching connections
- [ ] Test `placed_right_of` layout logic in `_build_single_instance()`
- [ ] Test `_resolve_by_name()` helper
- [ ] Test multi-pole connection registration paths
- [ ] Test `reuse_terminals` resolution in inner build loop

### Task 9.2: Test `project.py` (66% coverage -> target 85%+)

- [ ] Test `set_pin_start()` with prefix counter update path (the `if tag_key in prefix_counters` branch)
- [ ] Test `spdt()` and `no_contact()` registration methods
- [ ] Test `custom()` — custom builder registration
- [ ] Test `build()` — full PDF compilation pipeline (mock `typst` package)
- [ ] Test `_build_custom_circuit()` — never called path
- [ ] Test `plc_report()` and `custom_page()` registration

### Task 9.3: Test `system/system_analysis.py` (0% coverage -> CRITICAL)

Entire module untested (115 statements, 0 covered). Contains recursive graph traversal.

- [ ] Test `build_connectivity_graph()` — with simple circuit of Lines and Symbols
- [ ] Test `trace_connection()` — forward/backward tracing, cycle detection
- [ ] Test `_find_connected_symbol()` — node with/without matching symbol ports
- [ ] Test `_is_valid_direction()` — direction-based line filtering
- [ ] Test `_get_terminal_channels()` — Terminal vs TerminalBlock channel extraction
- [ ] Test `export_terminals_to_csv()` — correct CSV format, escaping
- [ ] Test `export_components_to_csv()` — component list CSV format

### Task 9.4: Test `utils/transform.py` (38% coverage -> target 80%+)

Complex SVG path parsers have zero tests. A bug produces silently corrupted SVG.

- [ ] Test `translate(Circle)`, `translate(Text)`, `translate(Group)`, `translate(Polygon)`
- [ ] Test `translate(Path)` via `_translate_path_d()` — M, L, H, V, C, S, Q, T, Z commands
- [ ] Test `rotate(Point)`, `rotate(Port)`, `rotate(Line)`, `rotate(Group)`, `rotate(Polygon)`
- [ ] Test `rotate(Circle)`, `rotate(Text)` (includes anchor-flip at 180 degrees)
- [ ] Test `rotate(Path)` via `_rotate_path_d()` — 90, 180, 270 degree rotations
- [ ] Test fallback warning handlers for unhandled types

### Task 9.5: Test `layout/layout.py` (55% coverage -> target 80%+)

- [ ] Test `get_connection_ports()` — finding ports matching a direction vector
- [ ] Test `auto_connect()` — matching ports, no matching ports, multiple matches
- [ ] Test `_find_matching_ports()` — tolerance edge cases, duplicate X positions
- [ ] Test `auto_connect_labeled()` — labeled wire connections
- [ ] Test `layout_vertical_chain()` — vertical arrangement + auto-connect

### Task 9.6: Test `std_circuits/power.py` — `power_distribution()` (0% for this function)

`power_distribution()` is 106 lines with zero coverage. Composite circuit function.

- [ ] Test basic `power_distribution()` creation
- [ ] Test with various `terminal_maps` configurations
- [ ] Test error case: missing terminal_maps keys

### Task 9.7: Test `std_circuits/motor.py` — `ct_terminals` branch (0% for this branch)

40 lines of CT terminal/reference placement logic with zero coverage.

- [ ] Test `dol_starter()` with `ct_terminals` parameter
- [ ] Test terminal vs reference placement logic
- [ ] Test wire routing to CT terminals

### Task 9.8: Test `system/connection_registry.py` untested methods (79% -> target 95%)

- [ ] Test `add_connections()` — batch connection addition
- [ ] Test `register_3phase_connections()`, `register_3phase_input()`, `register_3phase_output()`
- [ ] Test `_build_all_pin_keys()` — gap-filling for sequential and prefixed terminals
- [ ] Test `_pin_sort_key()` — sort key with prefix:number handling
- [ ] Test `export_registry_to_csv()` — empty-slot branch, actual CSV content verification

### Task 9.9: Test untested symbol factories

These symbol factories have zero direct tests (only exercised indirectly via std_circuits):

- [ ] Test `fuse_symbol()` — never tested anywhere, never used in std_circuits
- [ ] Test `terminal_box_symbol()` — not tested, `pins` validation branches
- [ ] Test `circuit_breaker_symbol()`, `two_pole_circuit_breaker_symbol()`, `three_pole_circuit_breaker_symbol()`
- [ ] Test `spdt_symbol()`, `multi_pole_spdt_symbol()`, `multi_pole_terminal_symbol()`
- [ ] Test `current_transducer_symbol()`, `current_transducer_assembly_symbol()`
- [ ] Test `dynamic_block_symbol()` — validation ValueError branches

### Task 9.10: Test `rendering/typst/compiler.py` (61% -> target 80%)

- [ ] Mock `typst` import to test `compile()` method
- [ ] Test `_render_page()` dispatch to schematic/front/plc/terminal/custom
- [ ] Test `_rel_path()` helper
- [ ] Test page ordering and content generation

### Task 9.11: Strengthen existing test assertions

15+ tests use weak assertions (`assert len(circuit.elements) > 0`). They verify something was
produced but not that it was correct.

- [ ] Add `component_map` and `terminal_pin_map` assertions to multicount integration tests
- [ ] Replace `assert X is not None` with specific value assertions where possible
- [ ] Add snapshot tests for PSU, coil, no_contact, and at least one multi-count circuit
- [ ] Remove or re-attach orphaned `psu_circuit.svg` snapshot (no test references it)

### Task 9.12: Test infrastructure improvements

- [ ] Add shared fixtures to `conftest.py`: `initial_state`, `simple_builder`, `two_pole_symbol`
  (`state = create_autonumberer()` appears in ~40 test functions)
- [ ] Add `@pytest.mark.parametrize` for symbol factory tests
- [ ] Add pytest markers: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.snapshot`

---

## 10. FP Principles — Violations & Remediation

**Audit Grade: B+** — Excellent in core data structures, inconsistent in state management classes.

### Positive findings (no action needed)

- All core data types (`Symbol`, `Port`, `Point`, `Vector`, `Element`, `Style`) are properly frozen
- `translate()` and `rotate()` in `transform.py` correctly return new instances via `replace()`
- `autonumbering.py` demonstrates gold-standard state threading (`new_state = state.copy()`)
- No mutable default arguments anywhere (`def f(...=[])` antipattern absent)
- All file I/O properly isolated at module boundaries
- No `datetime.now()`, `random`, `os.environ`, or other non-deterministic calls in core

### Task 10.1: Document mutable builders in CLAUDE.md (pending Q9)

`PlcMapper`, `Project`, and `CircuitBuilder` all use mutable accumulation (`.append()`, dict
mutation, `return self`) but aren't documented as exceptions to the immutability rule.

- [ ] Add "Intentional Mutable Builders" section to CLAUDE.md listing:
  1. `Circuit` — mutable accumulator for symbols/elements (already documented)
  2. `Project` — mutable builder for project definitions
  3. `CircuitBuilder` — mutable builder for circuit specifications
  4. `PlcMapper` — mutable builder for PLC module/sensor definitions
- [ ] Add warning: "Do not share instances across multiple build contexts"

### Task 10.2: Fix `Project.set_pin_start()` state threading

`project.py:140-159` — Mutates `self._state` in-place with `-> None` return. Violates the state
threading pattern where functions should return `(new_state, result)`.

- [ ] Either return `self` for chaining consistency
- [ ] Or document that Project methods mutate internal state (builder pattern)

### Task 10.3: Fix `PlcMapper._next_terminal_pin()` hidden mutation

`plc.py:179` — `_next_terminal_pin()` mutates `self._terminal_pin_counters` as a side effect.
Called from `generate_connections()`. Calling `generate_connections()` twice produces different
results (non-deterministic).

- [ ] Option A: Reset counters at start of `generate_connections()`
- [ ] Option B: Make `generate_connections()` take a snapshot and work from that
- [ ] Document that `generate_connections()` should only be called once

### Task 10.4: Fix `_create_single_circuit_from_spec` multi-phase mutation

`builder.py:646-928` — Function mutates `realized_components` dicts across 4 phases (adding
`"symbol"` key in Phase 3, `"y"` in Phase 1). State accumulates implicitly.

- [ ] Make each phase return its own data structure instead of mutating shared dicts
- [ ] Or document the phase-based mutation pattern clearly at function top

---

## 11. DRY Violations — Code Duplication

### Task 11.1: Extract `apply_wire_labels()` helper (5 duplications)

Identical 4-line block appears in 5 locations:
- `builder.py:600-604`
- `std_circuits/power.py:161-165` and `320-324`
- `std_circuits/control.py:271-275`
- `std_circuits/motor.py:284-288`

```python
if wire_labels is not None:
    from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit
    circuit = add_wire_labels_to_circuit(circuit, wire_labels)
```

- [ ] Create `apply_wire_labels(circuit, wire_labels)` in `layout/wire_labels.py`
- [ ] Replace all 5 occurrences with single function call
- [ ] Effort: 15 min

### Task 11.2: Extract `resolve_terminal_pins()` helper (3 duplications)

Identical "provided-or-auto-generate" conditional pattern appears in:
- `std_circuits/power.py:240-251` (changeover)
- `std_circuits/motor.py:129-139`
- `std_circuits/control.py:144-154`

```python
if tm_top_pins is None:
    s, pins = next_terminal_pins(s, tm_top, poles)
else:
    pins = tm_top_pins
pin_accumulator.setdefault(str(tm_top), []).extend(pins)
```

- [ ] Create `resolve_terminal_pins(state, terminal_id, poles, provided_pins)` in `utils/autonumbering.py`
- [ ] Returns `(updated_state, pins_tuple)`
- [ ] Replace 3 multi-line conditionals with single call
- [ ] Effort: 15 min

### Task 11.3: Extract `register_pole_connections()` helper (2 duplications in motor.py)

`std_circuits/motor.py:239-250` and `255-265` — Nearly identical loop registering multi-pole
connections with index transformation (`i*2` for input, `(i*2)+1` for output).

- [ ] Create `register_pole_connections(state, poles, term_tag, term_pins, comp_tag, comp_pins, pin_index_fn, side)` in `system/connection_registry.py`
- [ ] Replace 2 complex loops with parameterized calls
- [ ] Effort: 20 min

### Task 11.4: Extract horizontal layout boilerplate (3 duplications)

11-13 lines of nearly identical `create_horizontal_layout()` invocation in:
- `std_circuits/control.py:255-267`
- `std_circuits/motor.py:270-280`
- `std_circuits/power.py:306-316`

- [ ] Create wrapper that standardizes parameters and returns `(final_state, Circuit)`
- [ ] Effort: 10 min

### Task 11.5: Extract magic numbers to constants

Hard-coded geometry values scattered across factories:

| Value | Location | Meaning | Suggested Constant |
|-------|----------|---------|-------------------|
| 2.5 | power.py:266,279,292 | GRID_SIZE/2 | `CHANGEOVER_POLE_OFFSET` |
| 8 * GRID_SIZE | power.py:233 | Pole spacing | `CHANGEOVER_POLE_SPACING` |
| 0.5 | motor.py:166,192 | Half symbol spacing | `THERMAL_OVERLOAD_SPACING_FACTOR` |
| 2.0 | contacts.py:288 | Pin label offset | `PIN_LABEL_OFFSET_X` |
| 4.0 | contacts.py:372 | SPDT spacing multiplier | `SPDT_POLE_SPACING_FACTOR` |

- [ ] Add these constants to `model/constants.py`
- [ ] Replace all hard-coded values with named constants
- [ ] Effort: 15 min

### Task 11.6: Create `FactoryAccumulators` helper class

Tag/pin accumulator initialization and usage repeated in control.py and motor.py:
```python
tag_accumulator: dict[str, list[str]] = {}
pin_accumulator: dict[str, list[str]] = {}
# ... then many: tag_accumulator.setdefault(prefix, []).append(tag)
```

- [ ] Create `FactoryAccumulators` dataclass with `append_tag()`, `extend_pins()`, `to_build_result()` methods
- [ ] Refactor control.py and motor.py to use it
- [ ] Effort: 30 min

---

## 12. API Consistency

### Task 12.1: Standardize std_circuits factory terminal parameters

Factory signatures are inconsistent for terminal parameters:
- Most: `(state, x, y, tm_top, tm_bot, count, wire_labels, **kwargs)`
- `psu()`: uses `tm_top, tm_bot_left, tm_bot_right`
- `changeover()`: uses `tm_top_left, tm_top_right, tm_bot`
- `spdt()`: uses `tm_top, tm_bot_left, tm_bot_right`
- `power_distribution()`: uses `terminal_maps` dict

- [ ] Document the deviation in each function's docstring (why it differs from pattern)
- [ ] Consider adding `tm_bot: str | list[str]` overload pattern for multi-output circuits
- [ ] Update CLAUDE.md factory signature documentation to note exceptions

### Task 12.2: Fix `str | Terminal` type hints in autonumbering

`autonumbering.py:121` types `terminal_tag: str` but code uses `getattr(terminal_tag, "pin_prefixes", None)` — it actually accepts `Terminal` objects too. Same in `motor.py:205`.

- [ ] Update type hints to `str | Terminal` where `getattr()` is used on the parameter
- [ ] Add to docstrings that Terminal objects carry metadata

---

## 13. Documentation Gaps

### Task 13.1: Update README.md (HIGH PRIORITY)

README is missing 7+ major features from the public API. Expand from 255 to ~450 lines:

- [ ] Add **Terminal class** section — show `Terminal("X1", description="Main Power", bridge="all")`
- [ ] Add **Project API** section — multi-page PDF orchestration with example
- [ ] Expand **CircuitBuilder** section from 3 lines to ~80 lines with example code
- [ ] Add **BuildResult** explanation — fields, tuple unpacking, `.reuse_tags()`
- [ ] Add **wire() helper** section — `wire("RD", "2.5mm2")`, `wire.EMPTY`
- [ ] Add **Descriptors** section — `ref()`, `comp()`, `term()` with example
- [ ] Add **PlcMapper** section — module_type, sensor_type, sensor, generate_connections
- [ ] Add **Further Reading** section linking to `pyschemaelectrical_API_guide.md`
- [ ] Add **State Threading** code example showing pin continuity across circuits

### Task 13.2: Add CircuitBuilder method docstrings (HIGH PRIORITY)

15+ public methods on CircuitBuilder have no docstrings:

- [ ] `__init__(self, state)` — document state parameter
- [ ] `set_layout(self, x, y, spacing, symbol_spacing)` — layout configuration
- [ ] `add_component(self, func, tag_prefix, poles, pins)` — component addition
- [ ] `add_terminal(self, tm_id, poles, pins, ...)` — terminal addition
- [ ] `add_reference(self, ref_id, ...)` — reference symbol addition
- [ ] `place_right(self, idx, tag_prefix, func, ...)` — relative placement
- [ ] `connect(self, from_idx, from_pin, to_idx, to_pin)` — manual connection
- [ ] `add_matching_connection(self, ...)` — horizontal port matching
- [ ] `build(self, count, wire_labels, ...)` — circuit generation
- [ ] All methods need Args/Returns/Raises/Example sections

### Task 13.3: Add Project method docstrings (HIGH PRIORITY)

20+ public methods on Project have no docstrings:

- [ ] `terminals(self, *terminals)` — terminal registration
- [ ] `set_pin_start(self, terminal_id, pin)` — expand existing partial docstring
- [ ] All circuit registration methods: `dol_starter()`, `psu()`, `changeover()`, `spdt()`,
  `coil()`, `no_contact()`, `emergency_stop()`, `power_distribution()`
- [ ] `circuit(self, key, components, ...)` — descriptor circuit registration
- [ ] `custom(self, key, builder_fn)` — custom builder registration
- [ ] `page()`, `front_page()`, `terminal_report()`, `plc_report()`, `custom_page()`
- [ ] `build(self, output_path, ...)` — PDF compilation pipeline
- [ ] `build_svgs(self, output_dir)` — SVG-only output

### Task 13.4: Add PlcMapper method docstrings

- [ ] `generate_connections()` — document return type, side effects, single-call warning
- [ ] `generate_connections_table()` — document CSV format
- [ ] `module_count` property — document

### Task 13.5: Create missing example files

4 key API patterns have no example files:

- [ ] `example_circuit_builder.py` — CircuitBuilder direct usage (50-60 lines)
- [ ] `example_descriptors.py` — ref/comp/term declarative syntax (40-50 lines)
- [ ] `example_plc_mapper.py` — PLC I/O mapping workflow (60-80 lines)
- [ ] `example_state_threading.py` — State sharing across multiple circuits (40-50 lines)
- [ ] Update `examples/README.md` to reference new examples

### Task 13.6: Add module docstrings

These modules lack module-level docstrings:

- [ ] `system/system.py` — explain Circuit container, add_symbol, auto_connect
- [ ] Add module docstrings to any `__init__.py` that re-exports public API

### Task 13.7: Link documentation together

- [ ] Add "Further Reading / API Reference" section to README linking to `pyschemaelectrical_API_guide.md`
- [ ] Add "When to Use What" decision guide (std_circuits vs CircuitBuilder vs Descriptors vs Project)

---

## 14. Security & Robustness

### Task 14.1: Verify SVG text escaping

`utils/renderer.py:79` — `e.text = elem.content` assigns user-provided text directly.
ElementTree *should* auto-escape on serialization, but verify.

- [ ] Confirm `ET.tostring()` properly escapes `<`, `>`, `&` in text content
- [ ] Add test: render a symbol with `label="<script>test</script>"` and verify escaped output
- [ ] If not auto-escaped, use `xml.sax.saxutils.escape()` explicitly

---

## 15. API Improvements — From Real-World Usage

Analysis of `auxillary_cabinet_v3` (14 Python modules) identified these patterns.

### Task 15.1: Add typed `BuildResult` accessors

`power_supply.py:158` uses `result.component_map[StandardTags.POWER_SUPPLY][0]` — no IDE
autocomplete, requires `[0]` without safety.

- [ ] Add `BuildResult.component_tag(prefix: str) -> str` (returns first tag, raises if missing)
- [ ] Add `BuildResult.component_tags(prefix: str) -> list[str]` (returns all tags)

### Task 15.2: Add `BuildResult.get_terminals()` accessor

`power_supply.py:219` iterates `circuit.elements` with `hasattr(e, "ports")` to find terminals.

- [ ] Add `BuildResult.get_terminals() -> list[Symbol]`
- [ ] Or add `BuildResult.get_components_by_prefix(prefix: str) -> list[Symbol]`

### Task 15.3: String shorthand for `tag_generators`

`power_switching.py:67-69` manually defines `k1_tag_gen(s): return (s, "K1")`. Common pattern.

- [ ] Accept `str` values in `tag_generators` dict
- [ ] Auto-wrap with `create_fixed_tag_generator()` equivalent
- [ ] Example: `tag_generators={"K": "K1"}` instead of `{"K": k1_tag_gen}`

### Task 15.4: Review `StandardPins` — extend or deprecate?

`auxillary_cabinet_v3/constants.py` imports `StandardPins` but never uses it. Defines own
`ComponentPins` class with: `COIL`, `NO_CONTACT`, `CB_3P`, `CB_2P`, `THERMAL_OL`, `CONTACTOR_3P`, `CT`.

- [ ] Add commonly-used pin sets to `StandardPins` (or a new `PinSets` class):
  - `COIL = ("A1", "A2")`
  - `NO_CONTACT = ("13", "14")`
  - `NC_CONTACT = ("11", "12")`
  - `CB_3P = ("1", "2", "3", "4", "5", "6")`
  - `CB_2P = ("1", "2", "3", "4")`
  - `THERMAL_OL = ("", "T1", "", "T2", "", "T3")`
  - `CT = ("53", "54", "41", "43")`

### Task 15.5: Port `DeviceTemplate` system to library (pending Q8)

`device_templates.py` defines a generic system for declaring field device connections:

```python
@dataclass(frozen=True)
class PinDef:
    device_pin: str
    terminal: Terminal | None = None
    plc: Terminal | None = None
    terminal_pin: str = ""
    pin_prefix: str = ""

@dataclass(frozen=True)
class DeviceTemplate:
    mpn: str
    pins: tuple[PinDef, ...]
```

With `generate_field_connections()` that auto-numbers terminal pins and maps PLC references.
This is generic enough for the library.

- [ ] Create `pyschemaelectrical/field_devices.py` module
- [ ] Port `PinDef`, `DeviceTemplate`, `generate_field_connections()`
- [ ] Add proper type annotations and validation
- [ ] Add unit tests

### Task 15.6: Port `_merge_and_sort_terminal_csv()` to library

`main.py:218-251` defines CSV post-processing (merge duplicate terminal rows, natural sort).
This is a generic operation on the library's CSV output format.

- [ ] Add `merge_terminal_csv(csv_path: str) -> None` to `utils/export_utils.py` or similar
- [ ] Port `_terminal_pin_sort_key()` (natural sort for pin numbers)
- [ ] Add `_merge_terminal_rows()` logic

### Task 15.7: Port PLC connection generation to library

`plc_modules.py` defines a complete PLC module/rack/channel auto-assignment system. The
`PlcMapper` class in the library is simpler. Consider enhancing it with:

- [ ] Auto-assignment of connections to free module channels
- [ ] Multi-pin grouping (e.g., RTD with +R, RL, -R pins on same channel)
- [ ] Overflow warnings when modules are full
- [ ] CSV report generation for PLC connections

---

## 16. Remaining Items from Original Audit

These were identified in the original audit and haven't been completed.

### Task 16.1: Standardize parameter naming in `wire_labels.py`

- [ ] Rename `offset_x` to `label_offset_x` in `calculate_wire_label_position` and
  `add_wire_labels_to_circuit` for consistency with `create_labeled_wire`

### Task 16.2: Extract contactor linkage constants

`symbols/assemblies.py:64-65` — Magic numbers for linkage line placement.

- [ ] Extract to named constants or add geometry documentation comment

### Task 16.3: Document port ID conventions

Port naming is inconsistent across symbols (numeric, semantic, composite). Currently undocumented.

- [ ] Add section to CLAUDE.md or create `docs/port_conventions.md` explaining:
  - Numeric sequential: contacts (`"1"`, `"2"`)
  - IEC standard non-sequential: SPDT (`"1"`, `"2"`, `"4"`)
  - Semantic: motors (`"U"`, `"V"`, `"W"`, `"PE"`)
  - Composite: multi-pole SPDT (`"1_com"`, `"1_nc"`, `"1_no"`)

### Task 16.4: Update CLAUDE.md

- [ ] Add mutable builder exceptions list (see Task 10.1)
- [ ] Document port ID conventions (see 16.3)
- [ ] Update test baseline from 219 to 224 tests

### Task 16.5: Motor pin label cleanup (from 12.3)

- [ ] Verify `create_pin_labels()` no longer sorts (was marked done in 12.6)
- [ ] Replace manual label code in `three_pole_motor_symbol` with `create_pin_labels()` call

### Task 16.6: State threading documentation

- [ ] Document the shallow copy strategy in `autonumbering.py:61-63`
- [ ] Consider migrating to `GenerationState` frozen dataclass with `replace()` (pending Q4)

---

## 17. Previously Completed Items (Archive)

All items below were completed in earlier audit rounds. Kept for reference.

<details>
<summary>Click to expand completed items</summary>

### Modernization (Section 2) — DONE
- [x] Update `pyproject.toml` to `requires-python = ">=3.12"`
- [x] Replace `typing` imports with native syntax in all files
- [x] Standardize `pins` type hints to `tuple[str, ...]` across all symbol factories

### Code Duplication (Section 3) — DONE
- [x] Extract `create_extended_blade()` helper
- [x] Extract `_add_remapped_ports()` module-level helper
- [x] Extract `pad_pins()` utility
- [x] Extract `create_pin_label_text()` helper
- [x] Remove `_resolve_registry_pin` duplication
- [x] Consolidate `BridgeDef` / `ConnectionDef` type aliases

### Dead Code Removal (Section 4, partial) — DONE
- [x] Remove `create_fixed_tag_generator()`
- [x] Remove `ComponentRef.__iter__()`
- [x] Remove `RefSymbol` marker class
- [x] Remove `TerminalBlock.channel_map` attribute
- [x] Document unused `pins` parameter in `ref_symbol()`
- [x] Remove `**kwargs` from `psu_symbol()`
- [x] Clean up `__init__.py` public API

### Type Hints (Section 5, partial) — DONE
- [x] Add return types to `auto_connect_circuit`, `render_system`, `render_to_svg`
- [x] Fully type `export_terminal_list()`
- [x] Type `wire_labels.py:circuit` parameter
- [x] Type `_create_single_circuit_from_spec()` params

### State & Mutability (Section 6, partial) — DONE
- [x] Document `Circuit` mutability in docstring
- [x] Refactor `merge_terminals()` to pure function

### Patterns (Section 7, partial) — DONE
- [x] Move motor imports to module level, remove duplicates
- [x] Fix `LayoutConfig.spacing` default to match `set_layout()`
- [x] Standardize circuit registration APIs to `BuildResult`

### Validation (Section 8, partial) — DONE
- [x] Add direction validation to `ref_symbol()`
- [x] Add validation to `multi_pole_terminal_symbol()`
- [x] Add factory name error handling in `Project._build_std_circuit()`
- [x] Add empty descriptor list validation

### Constants (Section 10, partial) — DONE
- [x] Define `WIRE_LABEL_OFFSET_X` constant
- [x] Use `DEFAULT_WIRE_ALIGNMENT_TOLERANCE` in layout

### Documentation (Section 11) — DONE
- [x] Update `terminal_circle()` docstring
- [x] Fix uncertain comment in `set_terminal_counter()`
- [x] Add comprehensive docstring to `create_horizontal_layout()`
- [x] Resolve `GenerationState.from_dict()` ambiguity

### Decision Points (Section 12) — ALL RESOLVED
- [x] Remove `RefSymbol` marker class
- [x] Remove `TerminalBlock.channel_map`
- [x] Remove sorting from `create_pin_labels()`
- [x] Migrate all circuit factories to `BuildResult`
- [x] Set wire alignment tolerance to 0.1

### API Improvements (Section 13, partial) — DONE
- [x] Add `Circuit.get_symbol_by_tag()`
- [x] Refactor `merge_terminals()` to pure function
- [x] Migrate std_circuits to `BuildResult`

</details>

---

## Summary — Task Priority

### Tier 1: Bugs, Type Safety & Critical Tests (do first)

| Task | Effort | Blocked by |
|------|--------|------------|
| 2. Fix `text_anchor` bug | 15 min | Q1 |
| 3.1 Fix None-safety in builder/project | 30 min | -- |
| 3.2 Fix motor.py type mismatches | 30 min | -- |
| 3.3 Fix TerminalBlock constructor | 10 min | -- |
| 3.4 Fix merge_circuits type narrowing | 10 min | -- |
| 3.5 Fix autonumbering state handling | 1 hr | Q4 |
| 9.3 Test system_analysis.py (0% coverage!) | 2-3 hr | -- |
| 9.4 Test transform.py path parsers (0% coverage!) | 2-3 hr | -- |

### Tier 2: DRY, Quality & Documentation (do next)

| Task | Effort | Blocked by |
|------|--------|------------|
| 11.1 Extract apply_wire_labels helper | 15 min | -- |
| 11.2 Extract resolve_terminal_pins helper | 15 min | -- |
| 11.5 Extract magic numbers to constants | 15 min | -- |
| 13.1 Update README.md (7+ missing features) | 3 hr | -- |
| 13.2 Add CircuitBuilder docstrings | 2 hr | -- |
| 13.3 Add Project docstrings | 2 hr | -- |
| 7.2 Add file I/O error handling (5 locations) | 2 hr | -- |
| 10.1 Document mutable builders in CLAUDE.md | 30 min | Q9 |

### Tier 3: Test Coverage Expansion (do later)

| Task | Effort | Blocked by |
|------|--------|------------|
| 9.1 Test builder.py remaining paths | 3-4 hr | -- |
| 9.2 Test project.py remaining paths | 2-3 hr | -- |
| 9.5 Test layout/layout.py | 2-3 hr | -- |
| 9.6 Test power_distribution() | 1-2 hr | -- |
| 9.7 Test motor ct_terminals branch | 1-2 hr | -- |
| 9.8 Test connection_registry untested methods | 1-2 hr | -- |
| 9.9 Test untested symbol factories | 2-3 hr | -- |
| 9.11 Strengthen weak test assertions | 2-3 hr | -- |

### Tier 4: API Improvements (from real usage)

| Task | Effort | Blocked by |
|------|--------|------------|
| 15.1-15.3 BuildResult accessors + tag shorthand | 2-3 hr | -- |
| 15.4 Extend StandardPins | 30 min | -- |
| 15.5 Port DeviceTemplate system | 4-5 hr | Q8 |
| 15.6-15.7 Port CSV merge + PLC connection gen | 3-4 hr | Q8 |
| 13.5 Create 4 missing example files | 3-4 hr | -- |

### Tier 5: Cleanup & Polish

| Task | Effort | Blocked by |
|------|--------|------------|
| 4.1-4.5 Type annotation improvements | 3-4 hr | -- |
| 5.1 Reduce function complexity | 3-4 hr | -- |
| 5.2-5.4 Line length, imports, future | 1-2 hr | Q3 |
| 6.1-6.3 Dead code removal | 1 hr | Q5 |
| 8.1-8.2 Exception docs & naming | 1 hr | Q7 |
| 11.3-11.4 register_pole_connections + layout helper | 30 min | -- |
| 11.6 FactoryAccumulators class | 30 min | -- |
| 12.1-12.2 API consistency fixes | 2 hr | -- |
| 14.1 Verify SVG text escaping | 30 min | -- |
| 16.1-16.6 Remaining original audit items | 2-3 hr | Q4 |
| 9.10 Test typst compiler | 2-3 hr | -- |
| 9.12 Test infrastructure improvements | 1-2 hr | -- |
