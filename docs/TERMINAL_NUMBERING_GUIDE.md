# Terminal Autonumbering - Quick Reference

## Problem Statement

When creating multiple identical subcircuits (e.g., 3 motor circuits), you need:
- Terminal blocks to maintain consistent tag names (X1, X2) across all circuits
- Pin numbers to increment sequentially across the entire system
- Other components (breakers, contactors) to get unique tag numbers

## Solution: Dual Numbering Strategy

The autonumbering system now supports two modes:

### Mode 1: Tag Auto-increment (for F, Q, K, etc.)
Use `next_tag()` for components that should get unique tags in each circuit.

```python
state, f1 = next_tag(state, "F")  # F1
state, f2 = next_tag(state, "F")  # F2
state, q1 = next_tag(state, "Q")  # Q1
```

### Mode 2: Pin Auto-increment (for terminals)
Use `next_terminal_pins()` for terminals with fixed tags but sequential pins.

```python
state, pins1 = next_terminal_pins(state, poles=3)  # ('1', '2', '3', '4', '5', '6')
state, pins2 = next_terminal_pins(state, poles=3)  # ('7', '8', '9', '10', '11', '12')
```

## Visual Example: 3 Motor Circuits

```
Circuit 1:
  X1 [pins 1,2,3,4,5,6]          ← Same tag "X1", different pins
    ↓
  F1                              ← Different tag
    ↓
  F2                              ← Different tag
    ↓
  Q1                              ← Different tag
    ↓
  X2 [pins 7,8,9,10,11,12]       ← Same tag "X2", different pins

Circuit 2:
  X1 [pins 13,14,15,16,17,18]    ← Same tag "X1", different pins
    ↓
  F3                              ← Different tag
    ↓
  F4                              ← Different tag
    ↓
  Q2                              ← Different tag
    ↓
  X2 [pins 19,20,21,22,23,24]    ← Same tag "X2", different pins

Circuit 3:
  X1 [pins 25,26,27,28,29,30]    ← Same tag "X1", different pins
    ↓
  F5                              ← Different tag
    ↓
  F6                              ← Different tag
    ↓
  Q3                              ← Different tag
    ↓
  X2 [pins 31,32,33,34,35,36]    ← Same tag "X2", different pins
```

## Code Template

```python
from iec_lib.autonumbering import (
    create_autonumberer,
    next_tag,
    next_terminal_pins
)

# Initialize
state = create_autonumberer()

# For each circuit
for i in range(3):
    # Components with auto-incrementing tags
    state, f1 = next_tag(state, "F")
    state, f2 = next_tag(state, "F")
    state, q1 = next_tag(state, "Q")
    
    # Terminals with fixed tags, auto-incrementing pins
    state, x1_pins = next_terminal_pins(state, poles=3)
    state, x2_pins = next_terminal_pins(state, poles=3)
    
    # Create components
    top_terminal = three_pole_terminal(label="X1", pins=x1_pins)
    breaker1 = three_pole_circuit_breaker(label=f1, pins=auto_contact_pins())
    breaker2 = three_pole_thermal_overload(label=f2, pins=auto_thermal_pins())
    contactor = contactor(label=q1, coil_pins=auto_coil_pins(), contact_pins=auto_contact_pins())
    bot_terminal = three_pole_terminal(label="X2", pins=x2_pins)
```

## Key Benefits

1. **Consistent Terminal Names**: All circuits use X1/X2, making wiring diagrams easier to read
2. **Unique Pin Numbers**: Each terminal connection has a unique pin number for the entire system
3. **Automatic Management**: No manual tracking of numbers needed
4. **Scalable**: Easy to change from 3 circuits to 10+ circuits by changing loop count
5. **Functional**: Pure functions with immutable state, easy to test and debug

## See Also

- Full documentation: `docs/AUTONUMBERING.md`
- Working example: `examples/demo_system.py`
- Standalone demo: `examples/autonumbering_demo.py`
