# Pin Configuration Patterns

This document explains the three different ways to configure pin numbers when using standard circuits in PySchemaElectrical.

## Overview

The standard circuits support flexible pin numbering through three patterns:
1. **Default Auto-numbering** - Automatic sequential numbering
2. **Shared Project State** - Share numbering across multiple circuits  
3. **Custom Pin Numbers** - Explicit pin labels

## Pattern 1: Default Auto-numbering

The simplest approach - let the library automatically assign sequential pin numbers.

```python
state = create_autonumberer()
state, circuit, terminals = dol_starter(
    state=state,
    x=0, y=0,
    tm_top="X1",
    tm_bot="X10"
)
```

**Result:**
- X1 gets pins: 1, 2, 3
- X10 gets pins: 1, 2, 3
- All component symbols use their default pins

**Use when:** Creating isolated circuits where pin numbers don't need to coordinate with other circuits.

## Pattern 2: Shared Project State

Pass the same autonumber state object across multiple circuits to continue numbering.

```python
# Create ONE shared state for the entire project
project_state = create_autonumberer()

# First circuit
project_state, circuit1, _ = dol_starter(
    state=project_state,  # Share state
    x=0, y=0,
    tm_top="X1",
    tm_bot="X10"
)

# Second circuit - continues numbering
project_state, circuit2, _ = dol_starter(
    state=project_state,  # SAME state object
    x=80, y=0,
    tm_top="X1",  # Same terminal ID
    tm_bot="X10"
)
```

**Result:**
- First circuit X1: pins 1, 2, 3
- Second circuit X1: pins 4, 5, 6 (continues!)
- Each terminal ID maintains its own counter

**Use when:** Building a complete system where terminals need continuous numbering across circuits (e.g., a full cabinet with multiple motor starters).

## Pattern 3: Custom Pin Numbers

Explicitly specify pin labels for terminals and/or symbols.

```python
state = create_autonumberer()
state, circuit, terminals = dol_starter(
    state=state,
    x=0, y=0,
    tm_top="X1",
    tm_bot="X10",
    # Custom terminal pins
    tm_top_pins=("L1", "L2", "L3"),
    tm_bot_pins=("U", "V", "W"),
    # Custom symbol pins
    breaker_pins=("1L1", "2T1", "3L2", "4T2", "5L3", "6T3"),
    thermal_pins=("", "", "", "", "", ""),  # Hide all
    contactor_pins=("A1", "A2", "13", "14", "21", "22"),
    ct_pins=("S1", "S2", "K", "L")
)
```

**Result:**
- Input terminal: L1, L2, L3 (instead of 1, 2, 3)
- Output terminal: U, V, W (instead of 1, 2, 3)
- All symbols use custom pin nomenclature

**Use when:** You need specific pin labeling (e.g., IEC standards, matching existing hardware, or special naming conventions).

## Mixed Approach

You can mix and match these patterns:

```python
state, circuit, terminals = dol_starter(
    state=state,
    x=0, y=0,
    tm_top="X1",
    tm_bot="X10",
    # Auto-number terminals (leave as None)
    tm_top_pins=None,
    tm_bot_pins=None,
    # But customize specific symbol pins
    thermal_pins=("", "T1", "", "T2", "", "T3"),
    ct_pins=("CT1+", "CT1-", "CT2+", "CT2-")
)
```

## Available Pin Parameters

### Terminal Pins
- `tm_top_pins`: Pins for top terminal (default: None = auto-number)
- `tm_bot_pins`: Pins for bottom terminal (default: None = auto-number)

### Symbol Pins
- `breaker_pins`: Circuit breaker pins (default: ("1", "2", "3", "4", "5", "6"))
- `thermal_pins`: Thermal overload pins (default: ("", "T1", "", "T2", "", "T3"))
- `contactor_pins`: Contactor contact pins (default: ("1", "2", "3", "4", "5", "6"))
- `ct_pins`: Current transducer pins (default: ("1", "2", "3", "4"))

## Examples

Run the comprehensive example to see all patterns in action:

```bash
python examples/example_pin_configurations.py
```

This generates four SVG files demonstrating each approach.
