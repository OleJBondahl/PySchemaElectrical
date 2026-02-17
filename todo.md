# PySchemaElectrical — Codebase Audit & TODO

**Last updated:** 2026-02-17
**Scope:** Full codebase audit + `auxillary_cabinet_v3` real-world usage analysis
**Tool analysis:** `ruff check --select ALL` (1053 issues), `ty check` (54 diagnostics), `pytest` (219 tests, 79% coverage)

---

## 0. Questions & Uncertainties for Maintainer

These require your input before the relevant tasks can proceed. Please answer inline.

### Q1: `text_anchor` vs `anchor` in `create_pin_label_text()`

`model/parts.py:85` passes `text_anchor=anchor` to `Text()`, but the `Text` dataclass field
is named `anchor` (not `text_anchor`). `ty` flags this as `unknown-argument`. This _should_ be
a runtime crash whenever pin labels are created, yet all 219 tests pass and the real project
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
    text_anchor=anchor,  # ← Text dataclass has `anchor`, not `text_anchor`
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

- [ ] `builder.py:173` — `state: Any` → `dict[str, Any] | GenerationState`
- [ ] `builder.py:190` — `tm_id: Any` → `str | Terminal`
- [ ] `descriptors.py:37` — `symbol_fn: Any` → `Callable[..., Symbol]`
- [ ] `builder.py:576` — `tag_generators: dict | None` → `dict[str, Callable[[dict], tuple[dict, str]]] | None`
- [ ] `builder.py:577` — `terminal_maps: dict | None` → `dict[str, Any] | None`
- [ ] `system/system_analysis.py:64` — `direction_filter: Any | None` → `Vector | None`

### Task 4.4: Tighten `GenerationState.terminal_registry` type

`model/state.py:31` — `TerminalRegistry | dict` is too loose.

- [ ] Tighten to `TerminalRegistry` only (pending Q4)
- [ ] Or specify dict structure: `TerminalRegistry | dict[str, Any]`

---

## 5. Code Quality — `ruff` Complexity & Style

### Task 5.1: Reduce function complexity (14 C901 violations)

`ruff` reports 14 functions exceeding complexity threshold (>10):

- [ ] `builder.py:483` — `build()` complexity 22 → break into sub-methods
- [ ] `builder.py:611` — `_create_single_circuit_from_spec()` complexity 46 → largest single function, needs decomposition
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
- [ ] Make `increment_tag()` and `format_tag()` private (`_` prefix)
- [ ] Update/remove tests in `test_utils_advanced.py` that test these functions
- [ ] Verify nothing in `__init__.py` exports these

### Task 6.2: Remove commented-out code (12 ERA001)

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

- [ ] `utils/terminal_bridges.py:227-280` — Wrap CSV file operations with specific exception handling
  (currently uses bare `except Exception`)
- [ ] `system/system_analysis.py:173-207` — `export_terminals_to_csv()`: check directory exists,
  handle `PermissionError`
- [ ] `system/system_analysis.py:210-250` — `export_components_to_csv()`: same
- [ ] `utils/renderer.py:260-289` — SVG file output: handle `PermissionError`, `OSError`

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

- [ ] `TagReuseExhausted` → `TagReuseError`
- [ ] `TerminalReuseExhausted` → `TerminalReuseError`
- [ ] `WireLabelCountMismatch` → `WireLabelMismatchError`
- [ ] Keep old names as aliases for one release cycle

---

## 9. Test Coverage Gaps

**Current:** 219 tests, 79% line coverage. Key uncovered areas:

### Task 9.1: Test `builder.py` (19% coverage → target 60%+)

The builder is the most complex module (391 statements, 317 uncovered).

- [ ] Test `CircuitBuilder.connect()` — pin names via `PortRef`, invalid pin, side inference
- [ ] Test `build()` with `count > 1`
- [ ] Test `build()` with `wire_labels`
- [ ] Test `build()` with `reuse_tags` and `reuse_terminals`
- [ ] Test `_validate_connections()` — invalid indices
- [ ] Test `PortNotFoundError` is raised for bad pin references
- [ ] Test `TagReuseExhausted` is raised when source runs out
- [ ] Test `TerminalReuseExhausted` is raised when source runs out

### Task 9.2: Test `project.py` (31% coverage → target 50%+)

- [ ] Test `Project.build()` — no circuits registered
- [ ] Test `Project.build()` — with standard circuit
- [ ] Test `Project.build()` — with descriptor circuit
- [ ] Test error case: missing circuit key in page reference
- [ ] Test `set_pin_start()` works correctly

### Task 9.3: Test `system/system.py` (86% coverage → target 95%+)

- [ ] Test `auto_connect_circuit()` — empty circuit, `skip_auto_connect` symbols
- [ ] Test `merge_circuits()` — verify original circuits unchanged (immutability)

### Task 9.4: Test `system/system_analysis.py` (0% coverage)

Entire module untested (115 statements, 0 covered).

- [ ] Test `build_connectivity_graph()` — with simple circuit
- [ ] Test `trace_connection()` — forward/backward tracing
- [ ] Test CSV export functions — correct format, escaping

### Task 9.5: Test `layout/layout.py` (16% coverage)

- [ ] Test `auto_connect()` — matching ports, no matching ports
- [ ] Test `_find_matching_ports()` — tolerance edge cases
- [ ] Test `create_horizontal_layout()` — basic layout correctness

### Task 9.6: Test `std_circuits/*.py` (11-17% coverage)

- [ ] Test each standard circuit factory creates valid `BuildResult`
- [ ] Test with various `count` values
- [ ] Test `wire_labels` are applied correctly
- [ ] Test `reuse_tags` and `reuse_terminals` propagation

### Task 9.7: Test `rendering/typst/compiler.py` (36% coverage)

- [ ] Test with relative vs absolute paths
- [ ] Test special characters in metadata (escaping in Typst strings)
- [ ] Test missing SVG files
- [ ] Test page ordering

### Task 9.8: Test `utils/transform.py` (38% coverage)

- [ ] Test `_translate_path_d()` — various SVG path commands
- [ ] Test `_rotate_path_d()` — 90°, 180°, 270° rotations
- [ ] Test with complex multi-command paths

---

## 10. Remaining Items from Original Audit

These were identified in the original audit and haven't been completed.

### Task 10.1: Standardize parameter naming in `wire_labels.py`

- [ ] Rename `offset_x` to `label_offset_x` in `calculate_wire_label_position` and
  `add_wire_labels_to_circuit` for consistency with `create_labeled_wire`

### Task 10.2: Extract contactor linkage constants

`symbols/assemblies.py:64-65` — Magic numbers for linkage line placement.

- [ ] Extract to named constants or add geometry documentation comment

### Task 10.3: Document port ID conventions

Port naming is inconsistent across symbols (numeric, semantic, composite). Currently undocumented.

- [ ] Add section to CLAUDE.md or create `docs/port_conventions.md` explaining:
  - Numeric sequential: contacts (`"1"`, `"2"`)
  - IEC standard non-sequential: SPDT (`"1"`, `"2"`, `"4"`)
  - Semantic: motors (`"U"`, `"V"`, `"W"`, `"PE"`)
  - Composite: multi-pole SPDT (`"1_com"`, `"1_nc"`, `"1_no"`)

### Task 10.4: Update CLAUDE.md

- [ ] Note that `Circuit` is a mutable exception to the frozen dataclass rule
- [ ] Update Python version target from "3.8+" to "3.12+"
- [ ] Document port ID conventions (see 10.3)

### Task 10.5: Motor pin label cleanup (from 12.3)

- [ ] Verify `create_pin_labels()` no longer sorts (was marked done in 12.6)
- [ ] Replace manual label code in `three_pole_motor_symbol` with `create_pin_labels()` call

### Task 10.6: State threading documentation

- [ ] Document the shallow copy strategy in `autonumbering.py:61-63`
- [ ] Consider migrating to `GenerationState` frozen dataclass with `replace()` (pending Q4)

---

## 11. API Improvements — From Real-World Usage

Analysis of `auxillary_cabinet_v3` (14 Python modules) identified these patterns.

### Task 11.1: Add typed `BuildResult` accessors

`power_supply.py:158` uses `result.component_map[StandardTags.POWER_SUPPLY][0]` — no IDE
autocomplete, requires `[0]` without safety.

- [ ] Add `BuildResult.component_tag(prefix: str) -> str` (returns first tag, raises if missing)
- [ ] Add `BuildResult.component_tags(prefix: str) -> list[str]` (returns all tags)

### Task 11.2: Add `BuildResult.get_terminals()` accessor

`power_supply.py:219` iterates `circuit.elements` with `hasattr(e, "ports")` to find terminals.

- [ ] Add `BuildResult.get_terminals() -> list[Symbol]`
- [ ] Or add `BuildResult.get_components_by_prefix(prefix: str) -> list[Symbol]`

### Task 11.3: String shorthand for `tag_generators`

`power_switching.py:67-69` manually defines `k1_tag_gen(s): return (s, "K1")`. Common pattern.

- [ ] Accept `str` values in `tag_generators` dict
- [ ] Auto-wrap with `create_fixed_tag_generator()` equivalent
- [ ] Example: `tag_generators={"K": "K1"}` instead of `{"K": k1_tag_gen}`

### Task 11.4: Review `StandardPins` — extend or deprecate?

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

### Task 11.5: Port `DeviceTemplate` system to library (pending Q8)

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

### Task 11.6: Port `_merge_and_sort_terminal_csv()` to library

`main.py:218-251` defines CSV post-processing (merge duplicate terminal rows, natural sort).
This is a generic operation on the library's CSV output format.

- [ ] Add `merge_terminal_csv(csv_path: str) -> None` to `utils/export_utils.py` or similar
- [ ] Port `_terminal_pin_sort_key()` (natural sort for pin numbers)
- [ ] Add `_merge_terminal_rows()` logic

### Task 11.7: Port PLC connection generation to library

`plc_modules.py` defines a complete PLC module/rack/channel auto-assignment system. The
`PlcMapper` class in the library is simpler. Consider enhancing it with:

- [ ] Auto-assignment of connections to free module channels
- [ ] Multi-pin grouping (e.g., RTD with +R, RL, -R pins on same channel)
- [ ] Overflow warnings when modules are full
- [ ] CSV report generation for PLC connections

---

## 12. Previously Completed Items (Archive)

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

### Tier 1: Bugs & Type Safety (do first)

| Task | Effort | Blocked by |
|------|--------|------------|
| 2. Fix `text_anchor` bug | 15 min | Q1 |
| 3.1 Fix None-safety in builder/project | 30 min | — |
| 3.2 Fix motor.py type mismatches | 30 min | — |
| 3.3 Fix TerminalBlock constructor | 10 min | — |
| 3.4 Fix merge_circuits type narrowing | 10 min | — |
| 3.5 Fix autonumbering state handling | 1 hr | Q4 |

### Tier 2: Quality & Robustness (do next)

| Task | Effort | Blocked by |
|------|--------|------------|
| 4.1-4.3 Type annotations | 2-3 hr | — |
| 7.1-7.4 Validation & error handling | 2 hr | — |
| 8.1-8.2 Exception docs & naming | 1 hr | Q7 |
| 5.1 Reduce function complexity | 3-4 hr | — |

### Tier 3: Test Coverage (do later)

| Task | Effort | Blocked by |
|------|--------|------------|
| 9.1 Test builder.py | 4-5 hr | — |
| 9.2 Test project.py | 2-3 hr | — |
| 9.3-9.5 Test system/layout | 3-4 hr | — |
| 9.6-9.8 Test std_circuits/typst/transform | 4-5 hr | — |

### Tier 4: API Improvements (from real usage)

| Task | Effort | Blocked by |
|------|--------|------------|
| 11.1-11.3 BuildResult accessors + tag shorthand | 2-3 hr | — |
| 11.4 Extend StandardPins | 30 min | — |
| 11.5 Port DeviceTemplate system | 4-5 hr | Q8 |
| 11.6-11.7 Port CSV merge + PLC connection gen | 3-4 hr | Q8 |

### Tier 5: Cleanup & Docs

| Task | Effort | Blocked by |
|------|--------|------------|
| 5.2-5.4 Line length, imports, future | 1-2 hr | Q3 |
| 6.1-6.2 Dead code removal | 1 hr | Q5 |
| 10.1-10.6 Remaining audit items | 2-3 hr | Q4 |
