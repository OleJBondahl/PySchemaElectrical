# Type Safety To-Do List

This document logs the strict type checking errors found in the `src` directory. These issues should be resolved to ensure the library is type-safe and robust.

## 1. Argument Type Mismatches in Standard Circuits

Refactor the calls to symbol factory functions to match their strict type signatures.

- [ ] **`src/pyschemaelectrical/std_circuits/motor.py`**
  - [ ] `contactor_symbol` call at line 127: The `contact_pins` argument expects a rigid `Tuple[str, str, str, str, str, str]` but receives a variable-length `Tuple[str, ...]`.
    - *Fix:* Ensure `contact_pins` is validated or cast to the correct size, or update `contactor_symbol` to accept `Tuple[str, ...]`.

- [ ] **`src/pyschemaelectrical/std_circuits/power.py`**
  - [ ] `terminal_symbol` calls (lines 280, 291, 302):
    - **List vs Tuple**: The `pins` argument is passed as a `list` (e.g., `[input1_pins[i]]`), but the function defined in `symbols/terminals.py` expects a `tuple`.
      - *Fix:* Convert lists to tuples: `tuple([input1_pins[i]])`.
    - **None vs Str**: The `label_pos` argument uses a ternary operator `... else None` (lines 280, 302). `terminal_symbol` strictly expects `str` (default "left").
      - *Fix:* Change `None` to the default value (e.g., `"left"` or `""`) or update `terminal_symbol` to accept `Optional[str]`.

## 2. Unresolved Attributes in System

- [ ] **`src/pyschemaelectrical/system/system.py`**
  - [ ] `render_system` at line 81: `all_elements.extend(c.elements)` fails with "Object of type 'object' has no attribute 'elements'".
    - *Context:* The input `circuits` is `Union[Circuit, List[Circuit]]`. The normalization logic `circuit_list = circuits if isinstance(circuits, list) else [circuits]` might be confusing the inference engine, leading it to treat `c` as `object`.
    - *Fix:* Add an explicit type annotation for `circuit_list`: `circuit_list: List[Circuit] = ...`.

## 3. Generic Return Type Issues

- [ ] **`src/pyschemaelectrical/utils/transform.py`**
  - [ ] `translate` function return type mismatch.
    - *Error:* `Expected T@translate, found Point`.
    - *Context:* The function signature is `def translate(obj: T, ...) -> T`. Inside, it returns new instances like `Point(...)` or `Sym(...)`. The type checker cannot verify that `Point(...)` is exactly `T` (even if `T` was bound to `Point`).
    - *Fix:* This is a common pattern with generics. Use `cast(T, result)` or avoid strict `T` if the return type is structurally identical but a new instance.
