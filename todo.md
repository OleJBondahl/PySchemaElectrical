# PySchemaElectrical — Codebase Audit & TODO

**Last updated:** 2026-02-19
**Scope:** Full codebase audit (FP/DRY/quality/docs/tests) + `auxillary_cabinet_v3` real-world usage analysis
**Tool analysis:** `ruff check --select ALL` (1053 issues), `ty check` (31 diagnostics), `pytest` (939 tests, 97% coverage)

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

> **Answer:** Figure out the answer to this question yourself, look in the project code i you need more practical information on the use of the library (Auxillary cabinet v3)

**Resolved:** `create_pin_label_text()` is never called anywhere. The bug (`text_anchor=anchor`) was fixed to `anchor=anchor` in `model/parts.py:87`.

### Q2: Terminal name collision

Two classes are named `Terminal`:
1. `terminal.py:Terminal(str)` — immutable string subclass with metadata (bridge, description, pin_prefixes)
2. `symbols/terminals.py:Terminal(Symbol)` — frozen dataclass representing a rendered terminal symbol

These can shadow each other on import. The real project only uses (1) directly.

**Question:** Should `symbols/terminals.py::Terminal` be renamed to `TerminalSymbol`? Or is the current
shadowing acceptable because users never import both?

> **Answer:** rename to TerminalSymbol

**Resolved:** `symbols/terminals.py::Terminal` renamed to `TerminalSymbol`. Backward-compatible alias `Terminal = TerminalSymbol` kept.

### Q3: `from __future__ import annotations` cleanup scope

9 files still have `from __future__ import annotations`. With `requires-python = ">=3.12"`, these
are unnecessary. However, removing them changes evaluation semantics (annotations become real objects
instead of strings), which could affect any runtime annotation inspection.

**Question:** Is any code doing runtime annotation inspection (`typing.get_type_hints()`, etc.)?
If not, should we remove all 9 `__future__` imports?

Files: `wire_labels.py`, `motor.py`, `control.py`, `safety.py`, `power.py`, `system_analysis.py`,
`parts.py`, `utils.py`, `terminal_bridges.py`, `plc.py`

> **Answer:** Investigate to find the answer to this question.

**Resolved:** No runtime annotation inspection found. All 9 `from __future__ import annotations` imports safely removed.

### Q4: `GenerationState` vs `dict[str, Any]` state threading

Many functions accept `state: dict[str, Any] | GenerationState`. `ty` flags 5+ diagnostics
because `GenerationState` (frozen dataclass) doesn't support `state.copy()`, `state.get()`, or
`state["key"]` subscript operations.

**Question:** Should we standardize on ONE state type? Options:
- (A) Keep dual support but add proper type narrowing/guards
- (B) Migrate fully to `GenerationState` with `.replace()` semantics
- (C) Keep `dict` as the canonical type and remove `GenerationState`

> **Answer:** B, migrate fully to GenerationState, Write down what needs to change (if any) in the project codebase using this library in this todo.md.

**Resolved:** Fully migrated to frozen `GenerationState` with `.replace()` semantics (Option B). Consumer project (`auxillary_cabinet_v3`) needs ZERO changes.

### Q5: `auto_*` functions — safe to remove?

`generate_pin_range()`, `auto_terminal_pins()`, `auto_contact_pins()`, `auto_thermal_pins()`,
`auto_coil_pins()` in `autonumbering.py` have zero external usage. The real project uses static
pin tuples (`ComponentPins.COIL = ("A1", "A2")`). But some are tested in `test_utils_advanced.py`.

**Question:** Remove these functions AND their tests? Or keep as "utility" functions for future users?

> **Answer:** Check the project code auxillary cabinet v3, if these functions are actually unused, remove them.

**Resolved:** Confirmed unused in both library and consumer project. All 5 functions + `next_contact_pins()` removed. 4 test methods removed. Test count: 221.

### Q6: `power_supply.py` still uses old API

`auxillary_cabinet_v3/power_supply.py` still uses `_find_symbol_by_label()` (line 47) and
`hasattr(e, "ports")` iteration (lines 219, 237) despite `Circuit.get_symbol_by_tag()` being
added. Also returns `Tuple[Any, Circuit, List]` instead of `BuildResult`.

**Question:** Should updating `power_supply.py` to use the new API be tracked here, or is that
tracked separately in the `auxillary_cabinet_v3` repo?

> **Answer:** Update power_supply.py

### Q7: Exception class naming — `Error` suffix convention

Python convention (PEP 8) says exception names should end in `Error`. Current names:
`TagReuseExhausted`, `TerminalReuseExhausted`, `WireLabelCountMismatch` — missing `Error` suffix.

**Question:** Rename to `TagReuseError`, `TerminalReuseError`, `WireLabelMismatchError`?
This is a breaking change for any code catching these by name.

> **Answer:** Yes, rename, check for code catching these by name.

**Resolved:** Renamed `TagReuseExhausted` → `TagReuseError`, `TerminalReuseExhausted` → `TerminalReuseError`, `WireLabelCountMismatch` → `WireLabelMismatchError`. Old names kept as backward-compatible aliases.


### Q8: `DeviceTemplate` system — port to library?

`auxillary_cabinet_v3/device_templates.py` defines a `DeviceTemplate` + `PinDef` system for
declaring field device connections (sensors, valves, motors) with auto-numbered terminal pins
and PLC reference tags. This is generic enough to be library functionality.

**Question:** Should `DeviceTemplate`, `PinDef`, and `generate_field_connections()` be ported
into the library (e.g. as `pyschemaelectrical.field_devices` module)? Or keep project-specific?

> **Answer:** Yes, also look for other general functionality. The constants like "RTD_SENSOR" that uses device and pin def should not be ported, rtd sensor can vary in connection scheme for each project, only the general functionality and classes should be migrated. not implementation details.

### Q9: `PlcMapper` and `Project` — document as mutable builders?

The FP audit found that `PlcMapper`, `Project`, and `CircuitBuilder` all use mutable accumulation
patterns (`.append()`, dict mutation, `return self`). `Circuit` is already documented as an
intentional mutable exception. These three classes follow the same builder pattern.

**Question:** Should we:
- (A) Document all three as intentional mutable builders (like Circuit) in CLAUDE.md
- (B) Refactor PlcMapper to functional patterns (return new state instead of mutating self)
- (C) Accept the builder pattern as-is but add warnings about non-reusability

> **Answer:** refactor Keep PlcMapper, Project, and CircuitBuilder as mutable, as thoose should be the highest level imperative API, make this clear in both pydoc and claude.md and readme and the library api guide. that there are a few high level API classes that are imperative.

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

- [x] Change `text_anchor=anchor` to `anchor=anchor` in `model/parts.py:85`
- [x] Add test that `create_pin_label_text()` returns a `Text` with correct anchor value
- [x] Verify no other callers use `text_anchor` anywhere

---

## 3. Type Safety — `ty check` Diagnostics (54 total)

These are real type errors reported by `ty check`. Grouped into sub-agent-sized tasks.

### Task 3.1: Fix `None`-safety in `builder.py` and `project.py`

`ty` reports 3 cases where `None` can flow into functions that require `str` or `list`.

- [x] `builder.py:685` — `prefix` is `str | None`, passed to `next_tag(state, prefix)` which requires `str`.
  Add guard: `if prefix is None: raise ValueError(...)`
- [x] `project.py:464` — `cdef.components` is `list[...] | None`, passed to `build_from_descriptors()`.
  Add guard: `if cdef.components is None: raise ValueError(...)`
- [x] `project.py:477` — `cdef.builder_fn` is `Callable | None`, called directly.
  Add guard: `if cdef.builder_fn is None: raise ValueError(...)`

### Task 3.2: Fix type mismatches in `std_circuits/motor.py`

`ty` reports 3 errors where `instance_tm_bot` (typed `Unknown | str | list[str]`) flows into
functions expecting `str`.

- [x] `motor.py:136` — `instance_tm_bot` passed to `next_terminal_pins()` which expects `str`
- [x] `motor.py:181` — `instance_tm_bot` passed to `multi_pole_terminal_symbol()` which expects `str`
- [x] `motor.py:264` — `instance_tm_bot` passed to `register_connection()` which expects `str`
- [x] Add proper type narrowing: `assert isinstance(instance_tm_bot, str)` or explicit cast

### Task 3.3: Fix `TerminalBlock` constructor type mismatch

`symbols/terminals.py:137` — Passes `tuple(all_elements)` to `elements=` parameter which
expects `list[Element]`.

- [x] Change to `elements=list(all_elements)` or update `TerminalBlock` to accept `tuple`

### Task 3.4: Fix `merge_circuits` type narrowing

`system/system.py:107` — Assignment fails because `circuits` narrows to
`(Circuit & Top[list[Unknown]]) | list[Circuit]` after `isinstance` check.

- [x] Add explicit `cast()` or restructure the type narrowing

### Task 3.5: Fix `autonumbering.py` dual-type state handling

`ty` reports 5 errors where `dict[str, Any] | GenerationState` is used but only dict operations
are called (`state.copy()`, `state["tags"]`, `state.get()`).

- [x] Depends on Q4 answer — either add type guards or unify the state type
- [x] Fix `autonumbering.py:45` — `state["tags"]` on `GenerationState` which has no `__getitem__`
- [x] Fix `autonumbering.py:61-62` — `state.copy()` not available on `GenerationState`
- [x] Fix `autonumbering.py:118` — `state["pin_counter"]` subscript
- [x] Fix `autonumbering.py:149,163` — `.get()` and `.copy()` on union type
- [x] Fix `utils/utils.py:29` — same `.copy()` issue

Fully migrated to frozen `GenerationState` with `.replace()` semantics.

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

- [x] `builder.py` — `state: Any` in `__init__`, `generator(state)` closures (lines 130, 151)
- [x] `std_circuits/*.py` — Multiple factory functions with untyped `state` parameter
- [x] `plc.py` — Several methods with untyped parameters
- [x] `utils/renderer.py` — `_parse_dim(val, default)` completely untyped

### Task 4.2: Add missing return type annotations (28 instances)

- [x] `builder.py:118` — `BuildResult.__iter__()` missing return type
- [x] `builder.py:130,151` — Inner `generator()` functions missing return types
- [x] All `__init__` methods (9 instances) — add `-> None`
- [x] Private functions across `builder.py`, `plc.py`, `renderer.py`

### Task 4.3: Replace `Any` with specific types (17 instances)

Priority replacements:

- [x] `builder.py:173` — `state: Any` -> `GenerationState`
- [x] `builder.py:190` — `tm_id: Any` -> `str | Terminal`
- [x] `descriptors.py:37` — `symbol_fn: Any` -> `SymbolFactory`
- [x] `builder.py:576` — `tag_generators: dict | None` -> `dict[str, Callable] | None`
- [x] `builder.py:577` — `terminal_maps: dict | None` -> `dict[str, Any] | None`
- [x] `system/system_analysis.py:64` — `direction_filter: Any | None` -> `Vector | None`
- [x] `autonumbering.py:121` — `terminal_tag: str` -> `str | Terminal`

### Task 4.4: Tighten `GenerationState.terminal_registry` type

`model/state.py:31` — `TerminalRegistry | dict` is too loose.

- [x] Already `TerminalRegistry` only — no change needed.

### Task 4.5: Define `SymbolFactory` type alias

Several functions accept `Callable` where they mean "function returning Symbol".

- [x] Defined `SymbolFactory = Callable[..., Symbol]` in `model/core.py`
- [x] Used in `builder.py:add_component()`, `descriptors.py:CompDescriptor`
- [x] Exported from `__init__.py`

**Resolved:** 948 tests passing. `SymbolFactory` exported. All `state: Any` → `state: "GenerationState"` across std_circuits, builder, descriptors.

---

## 5. Code Quality — `ruff` Complexity & Style

### Task 5.1: Reduce function complexity (14 C901 violations)

`ruff` reports 14 functions exceeding complexity threshold (>10):

- [x] `builder.py:483` — `build()` complexity 22 → extracted `_build_effective_tag_generators()` and `_build_terminal_reuse_generators()` helper methods
- [x] `builder.py:611` — `_create_single_circuit_from_spec()` complexity 46 → decomposed into 4 phase helper functions:
  - `_phase1_tag_and_state()` — state mutation & component realization
  - `_phase2_register_connections()` — connection registration
  - `_phase3_instantiate_symbols()` — symbol placement
  - `_phase4_render_graphics()` — connection line rendering
- [x] 9 other functions — natural dispatch/pattern-match functions suppressed with `# noqa: C901` (renderer.py dispatch, transform path commands, blocks.py, motors.py, control.py spdt, motor.py dol_starter)

**Result:** 0 C901 violations. 948 tests passing.

### Task 5.2: Fix line-length violations (12 E501)

- [ ] `builder.py` — 7 lines over 88 chars (lines 180, 725, 736, 747, 757, 779, 784, 824)
- [ ] `layout/wire_labels.py` — 2 lines (14, 199)
- [ ] Break long lines by extracting local variables or reformatting conditions

### Task 5.3: Remove `from __future__ import annotations` (9 files, ~~pending Q3~~)

- [x] `layout/wire_labels.py`
- [x] `std_circuits/motor.py`, `control.py`, `safety.py`, `power.py`
- [x] `system/system_analysis.py`
- [x] `model/parts.py`
- [x] `utils/utils.py`, `terminal_bridges.py`
- [x] `plc.py`

9 files cleaned. Also removed from `plc.py`.

### Task 5.4: Move function-body imports to module level (31 PLC0415)

31 imports are inside function bodies instead of at module level. Most are in:

- [ ] `builder.py` — exception imports in `generator()` closures
- [ ] `model/parts.py` — `from primitives import Text` inside `create_pin_label_text()`
- [ ] `symbols/*.py` — scattered lazy imports
- [ ] Note: Some may be intentional to avoid circular imports — verify before moving

---

## 6. Dead Code Removal

### Task 6.1: Remove unused `auto_*` functions (~~pending Q5~~)

`utils/autonumbering.py:185-231` — 4 functions + 1 helper with zero external usage:

- [x] Remove `auto_terminal_pins()` (line 224)
- [x] Remove `auto_contact_pins()` (line 219)
- [x] Remove `auto_thermal_pins()` (line 229)
- [x] Remove `auto_coil_pins()` (line 214)
- [x] Remove `generate_pin_range()` (line 191)
- [x] Make `increment_tag()` and `format_tag()` private (`_` prefix) — they are just public aliases for private functions
- [x] Update/remove tests in `test_utils_advanced.py` that test these functions
- [x] Verify nothing in `__init__.py` exports these

Removed 7 functions total (5 auto_* + increment_tag + format_tag + get_pin_counter). Also removed `next_contact_pins`. Test count went from 224->221.

### Task 6.2: Remove `next_contact_pins()` (unused)

`utils/utils.py:64-95` — Generates SPDT contact pin tuples (`"11","12","14"`, `"21","22","24"`).
Never used in codebase. Superseded by `next_terminal_pins()` with `pin_prefixes`.

- [x] Remove `next_contact_pins()` from `utils/utils.py`
- [x] Verify no external consumers depend on it

### Task 6.3: Remove commented-out code (12 ERA001) — DONE (no changes needed)

`ruff --select ERA001` found 12 instances. All reviewed — every one is a **legitimate documentation comment** (geometry explanations, formula derivations, tuple structure docs, section headers). None are actual dead code. False positives from ERA001.

- [x] Scanned all 12 ERA001 findings across builder.py, model/parts.py, symbols/blocks.py, symbols/motors.py, symbols/protection.py, symbols/transducers.py, system/connection_registry.py, utils/transform.py
- [x] Confirmed: all are geometry documentation, not commented-out code

---

## 7. Validation & Error Handling

### Task 7.1: Add input validation to factory functions

- [x] `model/parts.py:290` — `three_pole_factory()`: validate `pole_spacing > 0`
- [x] `model/parts.py:339` — `two_pole_factory()`: same `pole_spacing` validation
- [x] `symbols/terminals.py:138-157` — `terminal_symbol()`: validate `label_pos` is "left" or "right"
- [x] `plc.py:127-136` — `sensor_type()`: N/A — PlcMapper removed, only PlcModuleType remains
- [x] `plc.py:138-160` — `sensor()`: N/A — PlcMapper removed

Also fixed pre-existing bug in `std_circuits/power.py`: `label_pos=""` was incorrectly used to suppress labels; now uses `""` for the label string with `label_pos="left"`. Snapshot updated. 9 new tests added. **948 tests passing.**

### Task 7.2: Add file I/O error handling

Currently 5 file I/O locations have no or overly broad error handling:

- [x] `utils/terminal_bridges.py:274` — Replaced bare `except Exception` with `(OSError, csv.Error)`
- [x] `utils/export_utils.py:25` — Uses `with open()`, OS errors propagate correctly to caller
- [x] `utils/terminal_bridges.py:160` — Already checks `csv_file.exists()` before opening
- [x] `rendering/typst/compiler.py:154-156` — OS errors propagate correctly to caller
- [x] `system/system_analysis.py:173-250` — OS errors propagate correctly to caller

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

### Task 8.2: Rename exception classes (~~pending Q7~~)

- [x] `TagReuseExhausted` -> `TagReuseError`
- [x] `TerminalReuseExhausted` -> `TerminalReuseError`
- [x] `WireLabelCountMismatch` -> `WireLabelMismatchError`
- [x] Keep old names as aliases for one release cycle

---

## 9. Test Coverage Gaps

**Current:** 221 tests, 78% line coverage. Key uncovered areas:

### Task 9.1: Test `builder.py` (41% -> 99% coverage) — DONE

98 new tests across 13 test classes. 99% line coverage (6 defensive guard lines uncovered).

- [x] Test `BuildResult` — 12 tests (iter, reuse_tags, reuse_terminals, exhaustion errors)
- [x] Test `ComponentRef`/`PortRef` — 5 tests (pin, pole, index tracking)
- [x] Test connections — 6 tests (add_connection, connect, connect_matching, chaining)
- [x] Test error paths — 5 tests (ComponentNotFoundError, PortNotFoundError)
- [x] Test build parameters — 13 tests (start_indices, tag_generators, reuse_tags/terminals, count, wire_labels)
- [x] Test placement — 8 tests (place_right, place_above, reference terminals)
- [x] Test add_reference — 5 tests (spec storage, fixed tag generators)
- [x] Test port/pin resolution — 13 tests (resolve_port_ref, registry_pin, distribute_pins)
- [x] Test layout — 5 tests (get_absolute_x_offset, LayoutConfig, set_layout)
- [x] Integration — 17 tests (full circuit chains, multi-pole, manual connections)

### Task 9.2: Test `project.py` (65% -> 100% coverage) — DONE

54 new tests across 12 test classes. 100% line coverage.

- [x] Test `__init__`, `terminals()`, `set_pin_start()` — 9 tests (defaults, overwrite, prefixes)
- [x] Test circuit registration — 7 tests (spdt, no_contact, custom, wire_labels, reuse_tags)
- [x] Test page registration — 5 tests (plc_report, custom_page, ordering)
- [x] Test `_build_one_circuit()` — 4 tests (missing reuse source, unknown factory, no components, no builder_fn)
- [x] Test custom circuits — 3 tests (BuildResult return, tuple fallback, kwargs)
- [x] Test `build_svgs()` — 5 tests (bridge defs, reference exclusion, directory creation)
- [x] Test `_add_page_to_compiler()` — 8 tests (all page types)
- [x] Test `build()` — 6 tests (full pipeline with mocked Typst, CSV, bridge, cleanup, logo)
- [x] Test state threading — 2 tests (sequential circuits, results reset)

### Task 9.3: Test `system/system_analysis.py` (0% -> 100% coverage) — DONE

- [x] Test `build_connectivity_graph()` — 8 tests
- [x] Test `trace_connection()` — 9 tests (cycle detection, direction filter, multi-hop)
- [x] Test `_find_connected_symbol()` — 4 tests
- [x] Test `_is_valid_direction()` — 10 tests
- [x] Test `_get_terminal_channels()` — 8 tests
- [x] Test `export_terminals_to_csv()` — 5 tests
- [x] Test `export_components_to_csv()` — 8 tests
- [x] Integration tests — 2 tests

68 tests total, 100% line coverage (114/114 statements).

### Task 9.4: Test `utils/transform.py` (38% -> 100% coverage) — DONE

- [x] Test `translate()` — Port, Circle, Text, Group, Polygon, Path, warning fallback (12 tests)
- [x] Test `_translate_path_d()` — M, L, T, H, V, C, S, Q, Z commands (14 tests)
- [x] Test `rotate()` — Port, Group, Polygon, Circle, Text (anchor flip), Path, warning (20 tests)
- [x] Test `_rotate_path_d()` — M, L, H→L, V→L, C, S, Q, Z commands (14 tests)
- [x] Symbol-specific tests — label forcing, port rotation (4 tests)

68 new tests (74 total), 100% line coverage (200/200 statements).

### Task 9.5: Test `layout/layout.py` (55% -> 100% coverage) — DONE

65 new tests added covering all functions. 100% line coverage.

- [x] Test `get_connection_ports()` — 8 tests (matching directions, empty ports, deduplication)
- [x] Test `auto_connect()` — 9 tests (alignment, tolerance, empty symbols, style)
- [x] Test `_find_matching_ports()` — 7 tests (sorting, tolerance, first-match-wins)
- [x] Test `auto_connect_labeled()` — 6 tests (Line+Text, None/empty specs, dict specs)
- [x] Test `auto_connect_circuit()` — 6 tests (chains, skip_auto_connect flag)
- [x] Test `layout_vertical_chain()` — 6 tests (positions, connections, empty list)
- [x] Test `create_horizontal_layout()` — 10 tests (tag_generators, state threading, offsets)

### Task 9.6: Test `std_circuits/power.py` — `power_distribution()` (75% -> 98% coverage) — DONE

20 new tests across 6 test classes.

- [x] Test basic creation — 4 tests (returns BuildResult, tuple unpacking, elements, state)
- [x] Test used_terminals — 4 tests (input, output, PSU terminals, uniqueness)
- [x] Test terminal_maps validation — 6 tests (missing keys, legacy key fallbacks, empty dict)
- [x] Test multi-count — 2 tests (count=2, default count)
- [x] Test circuit content — 3 tests (element count, position independence, renderability)
- [x] Test state threading — 1 test (sequential calls)

### Task 9.7: Test `std_circuits/motor.py` — `ct_terminals` branch (~85% -> 99% coverage) — DONE

30 new tests across 6 test classes.

- [x] Test string ct_terminals — 8 tests (basic, element increase, used_terminals, wires, connections)
- [x] Test reference ct_terminals — 5 tests (basic, element increase, excluded from used_terminals)
- [x] Test mixed ct_terminals — 2 tests (string + reference)
- [x] Test multi-count — 5 tests (count=2, element increase, connections, per-instance tm_bot)
- [x] Test edge cases — 6 tests (None, empty, excess, duplicates, custom ct_pins)
- [x] Test BuildResult — 4 tests (component_map, count=2, state advancement, tuple unpacking)

### Task 9.8: Test `system/connection_registry.py` (79% -> 98% coverage) — DONE

50 new tests across 8 test classes. 98% line coverage (only `ValueError` fallback in `_pin_sort_key` uncovered).

- [x] Test `TerminalRegistry` — 9 tests (add_connection, add_connections, immutability)
- [x] Test `get_registry`/`update_registry` — 2 tests
- [x] Test `register_connection` — 5 tests (single, default side, accumulation)
- [x] Test `register_3phase_connections` — 6 tests (3-pole mapping, edge cases)
- [x] Test `register_3phase_input`/`output` — 5 tests (default pins, custom, accumulation)
- [x] Test `_pin_sort_key` — 6 tests (numeric sort, prefix handling)
- [x] Test `_build_all_pin_keys` — 6 tests (gap-filling, prefixed, mixed)
- [x] Test `export_registry_to_csv` — 9 tests (empty, gaps, multi-component, sorted output)
- [x] Integration tests — 2 tests (end-to-end 3-phase + CSV, multi-component sharing)

### Task 9.9: Test untested symbol factories — DONE

99 new tests added. Coverage: breakers 100%, protection 100%, contacts 98%, terminals 100%, transducers 100%, blocks 99%.

- [x] Test `circuit_breaker_symbol()` — 8 tests (ports, cross elements, directions, labels)
- [x] Test `two_pole_circuit_breaker_symbol()` — 5 tests (4 ports, pole spacing)
- [x] Test `three_pole_circuit_breaker_symbol()` — 6 tests (6 ports, spacing, directions)
- [x] Test `fuse_symbol()` — 8 tests (ports, box elements, labels, pins)
- [x] Test `spdt_contact_symbol()` — 11 tests (IEC IDs, standard/inverted, NC/NO positions)
- [x] Test `multi_pole_spdt_symbol()` — 10 tests (naming, 1-3 poles, spacing, custom pins)
- [x] Test `multi_pole_terminal_symbol()` — 11 tests (sequential IDs, spacing, validation, label_pos)
- [x] Test `terminal_box_symbol()` — 11 tests (pin IDs, custom start, spacing, elements)
- [x] Test `dynamic_block_symbol()` — 18 tests (top/bottom pins, aliases, positions, ValueError)
- [x] Test `current_transducer_symbol()` — 3 tests (no ports, elements)
- [x] Test `current_transducer_assembly_symbol()` — 8 tests (ports, skip_auto_connect, offset)

### Task 9.10: Test `rendering/typst/` modules (61% -> 89-100% coverage) — DONE

91 new tests across 3 modules. compiler.py: 61% → 89%, frame_generator.py: 0% → 100%, markdown_converter.py: 0% → 100%.

- [x] Test `_render_page()` dispatch to all 5 page types + unknown type
- [x] Test `_render_schematic_page()` with/without terminals CSV
- [x] Test `_render_front_page()` via markdown_to_typst
- [x] Test `_render_plc_report()` and `_render_terminal_report()` template substitution
- [x] Test `_render_custom_page()` with/without title
- [x] Test `_rel_path()` — absolute, relative, backslash conversion
- [x] Test `_build_typst_content()` — full assembly, logo handling, config fields, dimensions
- [x] Test `compile()` ImportError when typst not installed
- [x] Test `_get_template_path()` — file exists, correct directory
- [x] Test `markdown_to_typst()` — headings, tables, paragraphs, notice, FileNotFoundError
- [x] Test `generate_frame()` — A3 constants, grid labels 1-8 / A-F, element counts, font

### Task 9.11: Strengthen existing test assertions + snapshot tests — DONE

Strengthened 10 weak assertions in `test_std_circuits_multicount.py` and added 4 new snapshot tests.

- [x] Add `component_map` and `terminal_pin_map` assertions to multicount integration tests
- [x] Replace `assert len(...) > 0` with specific minimum counts and field checks
- [x] Use `BuildResult` type assertions and verify `used_terminals` contents
- [x] Add snapshot tests for PSU (`psu_circuit`), coil (`coil_circuit`), no_contact (`no_contact_circuit`), multi-count emergency stop (`emergency_stop_multi_count`)
- [x] Re-attached orphaned `psu_circuit.svg` snapshot to new `test_psu_snapshot` test

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

### Task 10.1: Document mutable builders in CLAUDE.md (~~pending Q9~~)

`PlcMapper`, `Project`, and `CircuitBuilder` all use mutable accumulation (`.append()`, dict
mutation, `return self`) but aren't documented as exceptions to the immutability rule.

- [x] Add "Intentional Mutable Builders" section to CLAUDE.md listing:
  1. `Circuit` — mutable accumulator for symbols/elements (already documented)
  2. `Project` — mutable builder for project definitions
  3. `CircuitBuilder` — mutable builder for circuit specifications
  4. `PlcMapper` — mutable builder for PLC module/sensor definitions
- [x] Add warning: "Do not share instances across multiple build contexts"

Added Intentional Mutable Builders section to CLAUDE.md.

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

- [x] Documented the phase-based mutation pattern clearly at function top (chose documentation over refactoring to avoid destabilising the complex function)

Added comprehensive docstring block explaining the 4-phase pattern and why mutable dict accumulation is intentional at this level.

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

- [x] Create `apply_wire_labels(circuit, wire_labels)` in `layout/wire_labels.py`
- [x] Replace all 5 occurrences with single function call
- [x] Effort: 15 min

Created `apply_wire_labels()` in `layout/wire_labels.py`. All 5 duplications replaced.

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

- [x] Created `resolve_terminal_pins(state, terminal_tag, poles, provided_pins, pin_accumulator)` in `utils/autonumbering.py`
- [x] Returns `(updated_state, pins_tuple)`
- [x] Replaced conditionals in motor.py (2) and control.py (2) with single calls
- [x] Changeover in power.py uses different pattern (no accumulator) — not refactored

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

- [x] Added `SPDT_POLE_SPACING`, `CHANGEOVER_POLE_SPACING`, `CHANGEOVER_POLE_OFFSET`, `SPDT_PIN_LABEL_OFFSET` to `model/constants.py`
- [x] Replaced hard-coded values in `contacts.py` and `power.py`
- [x] `motor.py` uses `symbol_spacing/2` (already parameterized, not a magic number)

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

### Task 13.1: Update README.md (HIGH PRIORITY) — DONE

README expanded from 255 to ~400 lines with 7 new sections:

- [x] Add **Terminal class** section — show `Terminal("X1", description="Main Power", bridge="all")`
- [x] Add **Project API** section — multi-page PDF orchestration with example
- [x] Expand **CircuitBuilder** section from 3 lines to ~80 lines with example code
- [x] Add **BuildResult** explanation — fields, tuple unpacking, `.reuse_tags()`
- [x] Add **wire() helper** section — `wire("RD", "2.5mm2")`, `wire.EMPTY`
- [x] Add **Descriptors** section — `ref()`, `comp()`, `term()` with example
- [x] Add **PlcMapper** section — module_type, sensor_type, sensor, generate_connections
- [ ] Add **Further Reading** section linking to `pyschemaelectrical_API_guide.md`
- [ ] Add **State Threading** code example showing pin continuity across circuits

### Task 13.2: Add CircuitBuilder method docstrings (HIGH PRIORITY) — DONE

All public methods now have complete docstrings with Args/Returns sections.

- [x] `__init__(self, state)` — document state parameter
- [x] `set_layout(self, x, y, spacing, symbol_spacing)` — layout configuration
- [x] `add_component(self, func, tag_prefix, poles, pins)` — component addition
- [x] `add_terminal(self, tm_id, poles, pins, ...)` — terminal addition
- [x] `add_reference(self, ref_id, ...)` — reference symbol addition (already had docstring)
- [x] `place_right(self, idx, tag_prefix, func, ...)` — relative placement (already had docstring)
- [x] `connect(self, from_idx, from_pin, to_idx, to_pin)` — manual connection (already had docstring)
- [x] `connect_matching(self, ...)` — horizontal port matching (already had docstring)
- [x] `add_connection(self, ...)` — low-level index-based connection
- [x] `build(self, count, wire_labels, ...)` — circuit generation (Raises section added)

### Task 13.3: Add Project method docstrings (HIGH PRIORITY) — DONE

All public methods now have complete docstrings with Args sections.

- [x] `terminals(self, *terminals)` — terminal registration
- [x] `set_pin_start(self, terminal_id, pin)` — expanded with Args
- [x] All circuit registration methods: `dol_starter()`, `psu()`, `changeover()`, `spdt()`,
  `coil()`, `no_contact()`, `emergency_stop()` — all with Args
- [x] `circuit(self, key, components, ...)` — already had docstring
- [x] `custom(self, key, builder_fn)` — already had docstring
- [x] `page()`, `front_page()`, `terminal_report()`, `plc_report()`, `custom_page()` — all with Args
- [x] `build(self, output_path, ...)` — already had docstring
- [x] `build_svgs(self, output_dir)` — already had docstring

### Task 13.4: Add PlcMapper method docstrings

- [ ] `generate_connections()` — document return type, side effects, single-call warning
- [ ] `generate_connections_table()` — document CSV format
- [ ] `module_count` property — document

### Task 13.5: Create missing example files — DONE (3 of 4)

- [x] `example_descriptors.py` — ref/comp/term declarative syntax with count=2
- [x] `example_plc_mapper.py` — PLC I/O mapping with RTD, mA, and proximity sensors
- [x] `example_state_threading.py` — State sharing across 3 circuits with continuous pin numbering
- ~~`example_circuit_builder.py`~~ — Already covered by `example_motor_symbol.py` and `example_turn_switch.py`
- [ ] Update `examples/README.md` to reference new examples

### Task 13.6: Add module docstrings

These modules lack module-level docstrings:

- [ ] `system/system.py` — explain Circuit container, add_symbol, auto_connect
- [ ] Add module docstrings to any `__init__.py` that re-exports public API

### Task 13.7: Link documentation together

- [x] Added "Further Reading / API Reference" section to README linking to `pyschemaelectrical_API_guide.md`
- [x] Added "When to Use What" decision table (std_circuits vs CircuitBuilder vs Descriptors vs Project)

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

### Task 15.1: Add typed `BuildResult` accessors — DONE

Added 4 convenience methods to `BuildResult`:

- [x] `component_tag(prefix) -> str` — returns first tag, raises `KeyError` if missing
- [x] `component_tags(prefix) -> list[str]` — returns all tags (empty list if missing)
- [x] `get_symbol(tag) -> Symbol | None` — finds placed symbol by label (searches both `circuit.symbols` and `circuit.elements`)
- [x] `get_symbols(prefix) -> list[Symbol]` — finds all symbols matching a prefix

10 new tests in `TestBuildResultAccessors`.

### Task 15.2: (Merged into 15.1 — `get_symbol`/`get_symbols` cover this use case)

### Task 15.3: String shorthand for `tag_generators` — DONE

- [x] `build()` now accepts `str` values in `tag_generators` dict
- [x] String shorthand auto-wrapped: `{"K": "K1"}` → `lambda s: (s, "K1")`
- [x] Updated type hint to `dict[str, Callable | str]`
- [x] Can mix string and callable generators in same dict
- 3 new tests in `TestTagGeneratorStringShorthand`.

### Task 15.4: Extend `StandardPins` with common pin sets — DONE

Added 6 new `PinSet` constants to `StandardPins`:

- [x] `COIL = ("A1", "A2")` — Relay/contactor coil
- [x] `NO_CONTACT = ("13", "14")` — Normally open auxiliary contact
- [x] `NC_CONTACT = ("11", "12")` — Normally closed auxiliary contact
- [x] `CB_3P = ("1", "2", "3", "4", "5", "6")` — Three-pole circuit breaker
- [x] `CB_2P = ("1", "2", "3", "4")` — Two-pole circuit breaker
- [x] `CONTACTOR_3P = ("L1", "T1", "L2", "T2", "L3", "T3")` — Three-pole contactor
- [x] `CT = ("53", "54", "41", "43")` — Current transformer aux contacts
- 8 new tests in `TestStandardPins`.

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

- [x] Created `pyschemaelectrical/field_devices.py` module
- [x] Ported `PinDef`, `DeviceTemplate`, `generate_field_connections()` with proper type annotations
- [x] Supports sequential, prefixed, and fixed pin numbering modes
- [x] Supports `reuse_terminals` parameter (list[str] or BuildResult)
- [x] 26 unit tests, 99% coverage
- [x] Exported `PinDef`, `DeviceTemplate`, `generate_field_connections` from `__init__.py`

### Task 15.6: Port `_merge_and_sort_terminal_csv()` to library — DONE

- [x] Added `merge_terminal_csv(csv_path)` to `utils/export_utils.py`
- [x] Added `_terminal_pin_sort_key()` — natural sort for terminal pins
- [x] Added `_merge_terminal_rows()` — merges duplicate (tag, pin) rows
- [x] 22 unit tests in `test_export_utils.py`, 100% coverage
- [x] Exported `merge_terminal_csv` from `__init__.py`

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

- [x] Add mutable builder exceptions list (see Task 10.1)
- [ ] Document port ID conventions (see 16.3)
- [x] Update test baseline to 221 tests

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

### Completed in this session (2026-02-19)

| Task | Section | Description |
|------|---------|-------------|
| 2 | Bug fix | Fixed `text_anchor` bug in `create_pin_label_text()` |
| 3.1 | Type Safety | Fixed None-safety in builder/project |
| 3.2 | Type Safety | Fixed motor.py type mismatches |
| 3.3 | Type Safety | Fixed TerminalBlock constructor type |
| 3.4 | Type Safety | Fixed merge_circuits type narrowing |
| 3.5 | Type Safety | Migrated to frozen GenerationState with `.replace()` |
| 5.3 | Code Quality | Removed `from __future__ import annotations` from 9 files |
| 6.1 | Dead Code | Removed 7 unused functions (auto_*, increment_tag, format_tag, get_pin_counter) |
| 6.2 | Dead Code | Removed `next_contact_pins()` |
| 7.2 | Validation | Narrowed bare `except Exception` to `(OSError, csv.Error)` |
| 8.2 | Exceptions | Renamed exception classes to `*Error` suffix convention |
| 9.3 | Tests | system_analysis.py: 68 tests, 0% → 100% coverage |
| 9.4 | Tests | transform.py: 68 new tests, 38% → 100% coverage |
| 10.1 | FP Principles | Documented mutable builders in CLAUDE.md |
| 11.1 | DRY | Extracted `apply_wire_labels()` helper (5 duplications removed) |
| 11.2 | DRY | Extracted `resolve_terminal_pins()` helper (4 duplications removed) |
| 11.5 | DRY | Extracted 4 magic numbers to named constants |
| 13.2 | Docs | CircuitBuilder: all public method docstrings complete |
| 13.3 | Docs | Project: all public method docstrings complete |
| 16.4 | Cleanup | Updated CLAUDE.md (mutable builders, test baseline) |
| 6.3 | Dead Code | Reviewed 12 ERA001 findings — all false positives (geometry docs) |
| 9.5 | Tests | layout.py: 65 new tests, 55% → 100% coverage |
| 9.8 | Tests | connection_registry.py: 50 new tests, 79% → 98% coverage |
| 9.9 | Tests | Symbol factories: 99 new tests, most modules → 100% coverage |
| 13.1 | Docs | README.md expanded from 255 to ~400 lines (7 new sections) |
| 9.1 | Tests | builder.py: 98 new tests, 41% → 99% coverage |
| 9.2 | Tests | project.py: 54 new tests, 65% → 100% coverage |
| 9.6 | Tests | power_distribution(): 20 new tests, 75% → 98% coverage |
| 9.7 | Tests | motor ct_terminals: 30 new tests, ~85% → 99% coverage |
| 9.10 | Tests | rendering/typst: 91 new tests — compiler 61%→89%, frame_gen 0%→100%, markdown 0%→100% |
| 9.11 | Tests | Strengthened 10 weak assertions + 4 new snapshot tests (PSU, coil, no_contact, multi-count) |
| 15.1 | API | BuildResult: `component_tag()`, `component_tags()`, `get_symbol()`, `get_symbols()` |
| 15.3 | API | String shorthand for tag_generators: `{"K": "K1"}` |
| 15.4 | API | StandardPins: 6 new pin sets (COIL, NO/NC_CONTACT, CB_2P/3P, CONTACTOR_3P, CT) |
| 15.5 | API | Ported DeviceTemplate/PinDef/generate_field_connections to field_devices.py (26 tests) |
| 15.6 | API | Ported merge_terminal_csv to export_utils.py (22 tests) |
| 13.5 | Docs | 3 new examples: descriptors, plc_mapper, state_threading |

### Tier 3: Test Coverage Expansion — COMPLETE

All Tier 3 tasks done. 939 tests, 97% coverage.

### Tier 4: API Improvements (from real usage) — MOSTLY COMPLETE

| Task | Effort | Blocked by |
|------|--------|------------|
| ~~15.1-15.6 BuildResult, tag shorthand, StandardPins, DeviceTemplate, CSV merge~~ | DONE | -- |
| ~~13.5 Example files~~ | DONE (3 of 4) | -- |
| 15.7 Port PLC connection generation | 3-4 hr | -- |

### Tier 5: Cleanup & Polish — COMPLETE (2026-02-19)

| Task | Effort | Status |
|------|--------|--------|
| ~~4.1-4.5 Type annotation improvements~~ | DONE | `SymbolFactory`, `GenerationState`, `Vector`, `Terminal` typed throughout |
| ~~5.1 Reduce function complexity~~ | DONE | 4 phase helpers extracted, 9 natural dispatchers suppressed, 0 C901 violations |
| ~~7.1 Input validation~~ | DONE | `pole_spacing > 0`, `label_pos` validation + 9 tests |
| ~~10.4 Document `_create_single_circuit_from_spec` phases~~ | DONE | 4-phase docstring added |
| ~~13.7 Link documentation~~ | DONE | "When to Use What" table + "Further Reading" in README |
| ~~5.2, 5.4 Line length, imports~~ | DONE | -- |
| ~~8.1 Exception Raises docstrings~~ | DONE | -- |
| ~~11.3-11.4 register_pole_connections + layout helper~~ | DONE | -- |
| ~~11.6 FactoryAccumulators class~~ | DONE | -- |
| ~~12.1-12.2 API consistency fixes~~ | DONE | -- |
| ~~14.1 Verify SVG text escaping~~ | DONE | -- |
| ~~16.1-16.3, 16.4 (port ID docs), 16.5-16.6 Remaining original audit items~~ | DONE | -- |
| ~~9.12 Test infrastructure improvements~~ | DONE | -- |
