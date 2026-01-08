# Symbol Reference

This document lists all available electrical symbols in the **PySchemaElectrical** library.

**Import Convention:**
```python
from pyschemaelectrical.symbols.contacts import normally_open
from pyschemaelectrical.symbols.coils import coil
# etc...
```

## Table of Symbols

| Category | Function Call | Description |
| :--- | :--- | :--- |
| **Actuators** | `emergency_stop_button(label="", rotation=0.0)` | Mushroom-head emergency stop button (no contacts). |
| **Assemblies** | `contactor(label="", coil_pins=("A1","A2"), contact_pins=("1".."6"))` | Combined 3-pole contactor with coil and linkage. |
| | `emergency_stop_assembly(label="", pins=("1","2"))` | Emergency stop button mechanically linked to an NC contact. |
| **Blocks** | `terminal_box(label="", num_pins=1, start_pin_number=1, pin_spacing=10.0)` | Rectangular terminal box with customizable number of pins. |
| **Breakers** | `circuit_breaker(label="", pins=())` | Single-pole circuit breaker (Switch with 'X'). |
| | `three_pole_circuit_breaker(label="", pins=("1".."6"))` | Three-pole circuit breaker. |
| **Coils** | `coil(label="", pins=(), show_terminals=True)` | Relay/Contactor coil (Square). |
| **Contacts** | `normally_open(label="", pins=())` | Regulation Normally Open (NO) contact. |
| | `normally_closed(label="", pins=())` | Regulation Normally Closed (NC) contact. |
| | `three_pole_normally_open(label="", pins=("1".."6"))` | Three-pole NO contact block. |
| | `three_pole_normally_closed(label="", pins=("1".."6"))` | Three-pole NC contact block. |
| | `spdt_contact(label="", pins=("1","2","4"))` | Single Pole Double Throw (Changeover). 1 Common, 1 NC, 1 NO. |
| **Protection** | `thermal_overload(label="", pins=())` | Single-pole thermal overload protection (Pulse). |
| | `three_pole_thermal_overload(label="", pins=("1".."6"))` | Three-pole thermal overload protection. |
| | `fuse(label="", pins=())` | Standard fuse symbol. |
| **Terminals** | `terminal(label="", pins=())` | Single terminal circle. |
| | `three_pole_terminal(label="", pins=("1".."6"))` | Three-pole terminal block. |
| **Transducers** | `current_transducer_assembly(label="", pins=("1","2"))` | Current transducer (Circle on wire) + Terminal Box. |
| | `current_transducer_symbol()` | Basic current transducer circle (no ports/box). |

## Usage Notes

*   **Pins**: Most symbols accept a `pins` tuple. The order usually follows standard IEC conventions (e.g., Input, Output).
*   **3-Pole Symbols**: Require flattened pin tuples (e.g., `("1", "2", "3", "4", "5", "6")` maps to L1, T1, L2, T2, L3, T3).
*   **Labels**: Function label arguments set the main component tag (e.g., `-K1`).
