# Naming Convention for Standard Circuits

To ensure consistency and ease of use across the generic standard circuits library, we adhere to the following parameter naming convention. These names describe **what** the parameter controls in the context of the generic template, rather than a specific project usage (e.g., `tm_top` instead of `terminal_main_supply`).

## 1. Terminals (`tm_`)

Terminal parameters should use the prefix `tm_` followed by their geometric position or logical role within the standard circuit layout.

*   `tm_top`: Terminal located at the top of the circuit (typically input).
*   `tm_bot`: Terminal located at the bottom of the circuit (typically output).
*   `tm_top_left`: Terminal at the top-left position.
*   `tm_top_right`: Terminal at the top-right position.
*   `tm_bot_left`: Terminal at the bottom-left position.
*   `tm_bot_right`: Terminal at the bottom-right position.
*   `tm_in`: Input terminal (if geometry is ambiguous).
*   `tm_out`: Output terminal (if geometry is ambiguous).

## 2. Terminal Pins (`tm_*_pins`)

Pin configurations for terminals should strictly follow the terminal parameter name with the suffix `_pins`.

*   `tm_top` → `tm_top_pins`
*   `tm_bot` → `tm_bot_pins`
*   `tm_top_left` → `tm_top_left_pins`
*   etc.

The `_pins` parameter should typically accept a `Tuple[str, ...]` or `None`.

## 3. Circuit Components (`<component>_`)

Parameters related to specific components within the circuit should use the component name as the prefix.

### Tags
Use `_tag_prefix` to specify the prefix for auto-numbering (e.g., "K", "Q", "F").

*   `breaker_tag_prefix`
*   `coil_tag_prefix`
*   `switch_tag_prefix`

### Pins
Use `_pins` to specify the static pin numbers for the symbols.

*   `breaker_pins`
*   `coil_pins`
*   `contact_pins`

## 4. Layout

*   `spacing`: Horizontal spacing between repeated instances.
*   `symbol_spacing`: Vertical spacing between components within a circuit.
*   `x`, `y`: Origin coordinates.

## Example Signature

```python
def example_circuit(
    state: Any,
    x: float,
    y: float,
    # Terminals
    tm_top: str,
    tm_bot: str,
    # Terminal Pins
    tm_top_pins: Optional[Tuple[str, ...]] = None,
    tm_bot_pins: Optional[Tuple[str, ...]] = None,
    # Components
    breaker_tag_prefix: str = "F",
    breaker_pins: Tuple[str, ...] = ("1", "2"),
    # Layout (optional)
    spacing: float = 50.0
)
```
