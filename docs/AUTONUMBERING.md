# Autonumbering System

## Overview

The autonumbering system provides a functional programming approach to automatically manage component tags and terminal pin numbers in electrical schematics. This eliminates the need to manually track and increment component numbers when creating multiple identical subcircuits.

## Key Features

- **Functional Design**: Pure functions with immutable state management
- **Automatic Tag Numbering**: Sequential numbering by component prefix (F1, F2, F3...)
- **Automatic Pin Generation**: Standard pin numbering for terminals, contacts, and coils
- **Terminal Pin Counter**: Sequential pin numbering across circuits while keeping terminal tags constant
- **Type Safe**: Full type hints for all functions
- **Easy to Use**: Simple API for creating multiple subcircuits

## Core Concepts

### State Management

The autonumbering system uses a dictionary with two keys to track state:
- `tags`: Component numbers by prefix
- `pin_counter`: Current terminal pin number

```python
state = create_autonumberer()  # {'tags': {}, 'pin_counter': 0}
state = increment_tag(state, "F")  # {'tags': {'F': 1}, 'pin_counter': 0}
state, pins = next_terminal_pins(state)  # {'tags': {'F': 1}, 'pin_counter': 6}
```

State is **immutable** - each function returns a new state rather than modifying the existing one.

### Terminal Numbering Strategy

For terminal blocks, it's common to want:
- **Consistent tag names** across circuits (e.g., always "X1" for top terminal)
- **Sequential pin numbers** across the entire system (1-6, 7-12, 13-18...)

This allows you to create multiple identical circuits where:
- Circuit 1: X1 (pins 1,2,3,4,5,6) → ... → X2 (pins 7,8,9,10,11,12)
- Circuit 2: X1 (pins 13,14,15,16,17,18) → ... → X2 (pins 19,20,21,22,23,24)
- Circuit 3: X1 (pins 25,26,27,28,29,30) → ... → X2 (pins 31,32,33,34,35,36)

Use `next_terminal_pins()` for this behavior instead of `next_tag()`.

### Tag Prefixes

Common component prefixes in IEC standards:
- `F`: Circuit breakers, fuses, thermal protection
- `Q`: Contactors
- `X`: Terminals
- `K`: Relays
- `M`: Motors

## API Reference

### State Management Functions

#### `create_autonumberer() -> Dict[str, int]`
Create a new autonumbering state (empty dictionary).

#### `get_tag_number(state, prefix) -> int`
Get current number for a tag prefix (0 if unused).

#### `increment_tag(state, prefix) -> Dict[str, int]`
Increment counter for a prefix and return new state.

#### `next_tag(state, prefix) -> Tuple[Dict[str, int], str]`
Get next tag and updated state in one call.

**Example:**
```python
state = create_autonumberer()
state, tag1 = next_tag(state, "F")  # state={"F": 1}, tag1="F1"
state, tag2 = next_tag(state, "F")  # state={"F": 2}, tag2="F2"
```

### Tag Formatting

#### `format_tag(prefix, number) -> str`
Format a tag from prefix and number.

**Example:**
```python
format_tag("F", 1)  # "F1"
format_tag("Q", 42)  # "Q42"
```

### Pin Generation Functions

#### `auto_terminal_pins(base=1, poles=3) -> Tuple[str, ...]`
Generate standard terminal pin numbering.

**Example:**
```python
auto_terminal_pins()  # ('1', '2', '3', '4', '5', '6')
auto_terminal_pins(base=11, poles=3)  # ('11', '12', '13', '14', '15', '16')
```

#### `auto_contact_pins(base=1, poles=3) -> Tuple[str, ...]`
Generate standard contact pin numbering (same as terminal pins).

**Example:**
```python
auto_contact_pins()  # ('1', '2', '3', '4', '5', '6')
```

#### `auto_thermal_pins(base=2, poles=3) -> Tuple[str, ...]`
Generate thermal overload pin numbering (only even numbers labeled).

**Example:**
```python
auto_thermal_pins()  # ('', '2', '', '4', '', '6')
```

#### `auto_coil_pins() -> Tuple[str, str]`
Generate standard coil pin numbering.

**Example:**
```python
auto_coil_pins()  # ('A1', 'A2')
```

### Pin Counter Functions

#### `get_pin_counter(state) -> int`
Get the current pin counter value.

**Example:**
```python
state = create_autonumberer()
state, pins1 = next_terminal_pins(state)
print(get_pin_counter(state))  # 6
```

#### `next_terminal_pins(state, poles=3) -> Tuple[Dict[str, Any], Tuple[str, ...]]`
Generate sequential terminal pins and update pin counter.

This is the key function for creating terminals with consistent tags but auto-incrementing pins across multiple circuit copies.

**Example:**
```python
state = create_autonumberer()
state, pins1 = next_terminal_pins(state, 3)  # ('1', '2', '3', '4', '5', '6')
state, pins2 = next_terminal_pins(state, 3)  # ('7', '8', '9', '10', '11', '12')
state, pins3 = next_terminal_pins(state, 3)  # ('13', '14', '15', '16', '17', '18')
```

## Usage Examples

### Basic Usage

```python
from iec_lib.autonumbering import create_autonumberer, next_tag

# Initialize state
state = create_autonumberer()

# Generate sequential tags
state, f1 = next_tag(state, "F")  # "F1"
state, f2 = next_tag(state, "F")  # "F2"
state, q1 = next_tag(state, "Q")  # "Q1"
```

### Creating Components

```python
from iec_lib.library.breakers import three_pole_circuit_breaker
from iec_lib.autonumbering import next_tag, auto_contact_pins

state = create_autonumberer()
state, breaker_tag = next_tag(state, "F")

breaker = three_pole_circuit_breaker(
    label=breaker_tag,  # "F1"
    pins=auto_contact_pins()  # ('1', '2', '3', '4', '5', '6')
)
```

### Creating Multiple Circuits with Terminal Pin Autonumbering

This example shows how to create multiple circuits where:
- Terminal **tags** stay consistent (X1, X2)
- Terminal **pins** auto-increment across circuits
- Other component **tags** auto-increment normally (F1, F2, Q1, Q2...)

```python
from iec_lib.library.terminals import three_pole_terminal
from iec_lib.autonumbering import next_tag, next_terminal_pins

def create_circuit(state, x_pos):
    """Create a motor circuit with consistent terminal tags."""
    
    # Generate auto-incrementing tags for breakers and contactors
    state, f_tag = next_tag(state, "F")
    state, q_tag = next_tag(state, "Q")
    
    # Generate auto-incrementing pins for terminals (tags stay X1/X2)
    state, x1_pins = next_terminal_pins(state, poles=3)
    state, x2_pins = next_terminal_pins(state, poles=3)
    
    # Create components
    top_terminal = three_pole_terminal(label="X1", pins=x1_pins)  # Tag: X1, Pins: auto
    breaker = three_pole_circuit_breaker(label=f_tag, pins=auto_contact_pins())
    contactor = contactor(label=q_tag, coil_pins=auto_coil_pins(), 
                         contact_pins=auto_contact_pins())
    bot_terminal = three_pole_terminal(label="X2", pins=x2_pins)  # Tag: X2, Pins: auto
    
    # ... place and connect components ...
    
    return state, elements

# Create 3 identical circuits
state = create_autonumberer()
for i in range(3):
    state, circuit = create_circuit(state, x_pos=i*100)
    # Circuit 1: X1(1-6),   F1, Q1, X2(7-12)
    # Circuit 2: X1(13-18), F2, Q2, X2(19-24)
    # Circuit 3: X1(25-30), F3, Q3, X2(31-36)
```

## Best Practices

1. **Always pass state through functions**: The state should flow through your circuit creation functions to maintain proper numbering.

2. **Use helper functions**: Create reusable circuit-building functions that accept and return state.

3. **Keep state immutable**: Never modify the state dictionary directly; always use the provided functions.

4. **Use auto pin generators**: Prefer `auto_terminal_pins()` etc. over hardcoded tuples for consistency.

5. **Document state flow**: Add comments showing how state flows through complex circuit creation.

## Advanced Example

See `examples/demo_system.py` for a complete example showing:
- Multiple subcircuit creation
- State management through function calls
- Automatic component placement and connection
- Integration with layout and rendering systems

## Functional Programming Principles

The autonumbering system follows these principles:

- **Pure Functions**: No side effects, same input always produces same output
- **Immutability**: State is never modified, only new states created
- **Composition**: Small functions combine to create complex behavior
- **Type Safety**: All functions have complete type hints
- **Clear Abstractions**: High-level functions hide low-level details

## Future Enhancements

Potential additions to the autonumbering system:

- **Hierarchical numbering**: Support for subsystem prefixes (e.g., "M1-F1")
- **Custom pin patterns**: User-definable pin numbering schemes
- **State serialization**: Save/load numbering state for large projects
- **Validation**: Ensure tag uniqueness across entire schematic
