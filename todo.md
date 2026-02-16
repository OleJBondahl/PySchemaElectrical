# Quality Control TODO

Items identified during QC review that require further attention.
Items marked **BREAKING** would change the public API and should be
handled in a minor/major version bump.

## Breaking Changes (deferred)

### 1. Remove deprecated `StandardSpacing` class
- **File**: `src/pyschemaelectrical/model/constants.py` (lines 63-82)
- **Exported in**: `src/pyschemaelectrical/__init__.py` (line 21)
- `StandardSpacing` is superseded by `LayoutDefaults` with identical values.
  It is still exported from the public API. Removing it would break any
  consumer code that imports `StandardSpacing`.
- **Action**: Deprecate in next minor release, remove in next major release.

### 2. Rename `type` parameter in `PlcMapper.sensor()`
- **File**: `src/pyschemaelectrical/plc.py` (line 132)
- The parameter `type` shadows the Python builtin `type()`. Should be
  renamed to `sensor_type`.
- **Action**: Add `sensor_type` as an alias, deprecate `type` parameter.

### 3. Remove `terminal_offset` parameter from `psu()`
- **File**: `src/pyschemaelectrical/std_circuits/power.py` (line 38)
- Parameter is documented as "Kept for back-compat but ignored". It does
  nothing and should be removed when API stability allows.
- **Action**: Remove in next major release.

### 4. Make `GenerationState` frozen
- **File**: `src/pyschemaelectrical/model/state.py` (line 15)
- `GenerationState` is a mutable `@dataclass` despite the docstring claiming
  it is an "Immutable state container". Making it `frozen=True` would break
  code that mutates it directly.
- **Action**: Audit all mutation sites, then freeze in next major release.

### 5. Fix `Point.__add__` type annotation
- **File**: `src/pyschemaelectrical/model/core.py` (line 39)
- Type hint accepts `Union[Point, Vector]` but only `Vector` is valid.
  Changing the type annotation could break type-checker-dependent code.
- **Action**: Change to `other: Vector` in next minor release.

## Non-Breaking Improvements

### 6. Add `__rmul__` to `Vector`
- **File**: `src/pyschemaelectrical/model/core.py`
- `2 * vector` fails; only `vector * 2` works. Adding `__rmul__` is
  backward-compatible.

### 7. Implement Path translation in `transform.py`
- **File**: `src/pyschemaelectrical/utils/transform.py` (line 60)
- `translate()` silently ignores `Path` objects (returns unchanged).
  Should either raise `NotImplementedError` or implement proper
  translation of SVG path data.

### 8. Add missing symbol exports to `symbols/__init__.py`
- **File**: `src/pyschemaelectrical/symbols/__init__.py`
- Several symbol factories are not exported:
  - `contactor_symbol`, `emergency_stop_assembly_symbol` (assemblies.py)
  - `normally_open_symbol`, `normally_closed_symbol` (contacts.py)
  - `spdt_contact_symbol`, `three_pole_normally_open_symbol` (contacts.py)
  - `three_pole_normally_closed_symbol`, `three_pole_spdt_symbol` (contacts.py)
  - `fuse_symbol`, `thermal_overload_symbol` (protection.py)
  - `three_pole_thermal_overload_symbol` (protection.py)
  - `turn_switch_assembly_symbol` (assemblies.py)
  - `two_pole_circuit_breaker_symbol` (breakers.py)
- These are accessible via direct module import but not via
  `from pyschemaelectrical.symbols import *`.

### 9. Add `state.py` export to `model/__init__.py`
- **File**: `src/pyschemaelectrical/model/__init__.py`
- `GenerationState` and `create_initial_state` are not exported from
  the model package `__init__.py`. Users must import from submodule.

### 10. Update `AGENTS.MD` documentation
- **File**: `.agent/rules/AGENTS.MD`
- Specifies Python 3.10+ but library targets 3.8+.
- Lists outdated file paths (e.g., `core.py` instead of `model/core.py`).
- References non-existent `demo_system.py`.

### 11. Improve test coverage
- `system/system_analysis.py` has 0% coverage (110 statements).
- `utils/utils.py` has 39% coverage.
- `layout/layout.py` has 54% coverage.
- Missing tests for: wire labels, terminal bridges, export utilities.

### 12. Add `__all__` lists to package `__init__.py` files
- `utils/__init__.py`, `system/__init__.py`, `layout/__init__.py` all
  use `from .module import *` without `__all__` lists. Explicit `__all__`
  would give cleaner API boundaries.
