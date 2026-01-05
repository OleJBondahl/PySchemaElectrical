# Available IEC Symbols

This document lists all the available symbols in the `iec_lib` library, along with their parameters and usage examples.

## Contacts (`iec_lib.library.contacts`)

### `normally_open`
*   **Description**: IEC 60617 Normally Open (NO) Contact.
*   **Parameters**:
    *   `label` (str, optional): The component tag (e.g., "-K1").
    *   `pins` (tuple, optional): Pin numbers (e.g., `("13", "14")`).
*   **Ports**: "1" (Top), "2" (Bottom).

### `three_pole_normally_open`
*   **Description**: A three-pole version of the Normally Open contact.
*   **Parameters**:
    *   `label` (str, optional): The component tag (e.g., "-K1").
    *   `pins` (tuple, optional): Pin numbers for all 3 poles (default: `("1", "2", "3", "4", "5", "6")`).
*   **Ports**: "1", "2", "3", "4", "5", "6".

### `normally_closed`
*   **Description**: IEC 60617 Normally Closed (NC) Contact.
*   **Parameters**:
    *   `label` (str, optional): The component tag (e.g., "-K1").
    *   `pins` (tuple, optional): Pin numbers (e.g., `("21", "22")`).
*   **Ports**: "1" (Top), "2" (Bottom).

## Protection (`iec_lib.library.protection`)

### `thermal_overload`
*   **Description**: IEC 60617 Thermal Overload Protection symbol (pulse shape).
*   **Parameters**:
    *   `label` (str, optional): The component tag (e.g., "-F1").
    *   `pins` (tuple, optional): Pin numbers (e.g., `("1", "2")`).
*   **Ports**: "1" (Top), "2" (Bottom).

### `three_pole_thermal_overload`
*   **Description**: A three-pole version of the Thermal Overload Protection.
*   **Parameters**:
    *   `label` (str, optional): The component tag (e.g., "-F1").
    *   `pins` (tuple, optional): Pin numbers for all 3 poles (default: `("1", "2", "3", "4", "5", "6")`).
*   **Ports**: "1", "2", "3", "4", "5", "6".

### `fuse`
*   **Description**: IEC 60617 Fuse symbol.
*   **Parameters**:
    *   `label` (str, optional): The component tag (e.g., "-F2").
    *   `pins` (tuple, optional): Pin numbers (e.g., `("1", "2")`).
*   **Ports**: "1" (Top), "2" (Bottom).

## Coils (`iec_lib.library.coils`)

### `coil`
*   **Description**: IEC 60617 Coil symbol (Square).
*   **Parameters**:
    *   `label` (str, optional): The component tag (e.g., "-K1").
    *   `pins` (tuple, optional): Pin numbers (typically `("A1", "A2")`).
*   **Ports**: "A1" (Top), "A2" (Bottom).

## Terminals (`iec_lib.library.terminals`)

### `terminal`
*   **Description**: IEC 60617 Terminal symbol (Circle).
*   **Parameters**:
    *   `label` (str, optional): The terminal strip tag (e.g., "-X1").
    *   `pins` (tuple, optional): The terminal number (e.g., `("1",)`). Only the first element is used and placed at the bottom.
*   **Ports**: "1" (Center/Top), "2" (Center/Bottom).
