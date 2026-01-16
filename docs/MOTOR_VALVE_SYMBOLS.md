# Motor and Valve Symbols

This document describes the IEC 60617 compliant motor and valve symbols available in the PySchemaElectrical library.

## Motor Symbols

### Three-Phase Motor (`three_pole_motor_symbol`)

The three-phase motor symbol represents a standard asynchronous (squirrel cage) motor, which is the most common type in industrial applications.

**Symbol Features:**
- Rectangular body with "M" and "3~" designations
- Three terminals (U, V, W) for three-phase connection
- Dimensions: 30mm × 15mm (6 × 3 GRID_SIZE)
- Follows IEC 60617 standard for motor representation

**Usage:**
```python
from pyschemaelectrical.symbols import three_pole_motor_symbol

# Create a three-phase motor
motor = three_pole_motor_symbol(
    label="-M1",           # Component tag
    pins=("U", "V", "W")   # Phase designations
)
```

**Ports:**
- `U`: Phase U (left terminal)
- `V`: Phase V (center terminal)  
- `W`: Phase W (right terminal)

### Single-Phase Motor (`motor_symbol`)

The single-phase motor symbol represents a generic motor with two terminals.

**Symbol Features:**
- Circular body with "M" designation
- Two terminals (top and bottom)
- Diameter: 15mm (3 GRID_SIZE)
- Follows IEC 60617 standard for motor representation

**Usage:**
```python
from pyschemaelectrical.symbols import motor_symbol

# Create a single-phase motor
motor = motor_symbol(
    label="-M1",      # Component tag
    pins=("1", "2")   # Terminal numbers
)
```

**Ports:**
- `1`: Top terminal (input)
- `2`: Bottom terminal (output)

## Valve Symbols

### Solenoid Valve (`solenoid_valve_symbol`)

The solenoid valve symbol represents the electromagnetic coil actuator for a valve. This is the electrical component that drives the valve mechanism.

**Symbol Features:**
- Rectangular coil body with "Y" designation
- Diagonal cross lines indicating electromagnetic coil
- Two terminals (A1, A2) for coil energization
- Dimensions: 10mm × 10mm (2 × 2 GRID_SIZE)
- Follows IEC 60617 standard, using "Y" prefix for valve actuators

**Usage:**
```python
from pyschemaelectrical.symbols import solenoid_valve_symbol

# Create a solenoid valve
valve = solenoid_valve_symbol(
    label="-Y1",        # Component tag
    pins=("A1", "A2")   # Coil terminals
)
```

**Ports:**
- `A1`: Top coil terminal (typically positive/live)
- `A2`: Bottom coil terminal (typically negative/neutral)

### Two-Way Valve (`two_way_valve_symbol`)

The two-way valve symbol provides a more detailed representation showing valve positions using the square notation common in hydraulic/pneumatic diagrams, adapted for electrical schematics.

**Symbol Features:**
- Two position squares showing:
  - Top square: Normally closed (NC) position with "T" (blocked)
  - Bottom square: Energized/open position with flow arrow
- Two terminals (A1, A2) for actuation
- Dimensions: 10mm × 20mm (2 × 4 GRID_SIZE)
- Shows valve state visually

**Usage:**
```python
from pyschemaelectrical.symbols import two_way_valve_symbol

# Create a two-way valve
valve = two_way_valve_symbol(
    label="-Y2",        # Component tag
    pins=("A1", "A2")   # Actuator terminals
)
```

**Ports:**
- `A1`: Top terminal (typically positive/live)
- `A2`: Bottom terminal (typically negative/neutral)

## Integration with Terminals

All motor and valve symbols are designed to work seamlessly with the CircuitBuilder and terminal system:

```python
from pyschemaelectrical import CircuitBuilder, create_autonumberer
from pyschemaelectrical.symbols import three_pole_motor_symbol

state = create_autonumberer()

# Build a circuit with terminals and motor
builder = CircuitBuilder(state)
result = (
    builder
    .set_layout(x=0, y=0, symbol_spacing=50)
    # Add input terminals
    .add_terminal(
        tm_id="X1",
        poles=3,
        pins=("1", "2", "3"),
        label_pos="left"
    )
    # Add motor
    .add_component(
        symbol_func=three_pole_motor_symbol,
        tag_prefix="M",
        poles=3,
        pins=("U", "V", "W")
    )
    .build()
)
```

## IEC 60617 Compliance

All motor and valve symbols follow the IEC 60617 standard:

- **Motors**: Use "M" designation with appropriate phase indicators
  - Single-phase: Circle with "M"
  - Three-phase: Rectangle with "M" and "3~"
  
- **Valves**: Use "Y" designation for valve actuators
  - Standard solenoid: Rectangle with "Y" and coil indication
  - Positional: Multiple squares showing valve states

## Examples

See `examples/example_motors_valves.py` for complete working examples including:
- Three-phase motor with terminals
- Single-phase motor with terminals
- Solenoid valve with terminals
- Two-way valve with terminals
- Combined motor and valve circuits

## Testing

Unit tests for all motor and valve symbols are included in `tests/unit/test_symbols.py`.

Run tests with:
```bash
uv run pytest tests/unit/test_symbols.py --no-cov
```
