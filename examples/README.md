# PySchemaElectrical - Examples

This directory contains example usage of all standard circuits in the PySchemaElectrical library.

## Structure

```
examples/
├── constants.py                            # Project-specific constants
├── example_all_circuits.py                 # Run all examples at once
├── example_changeover.py                   # Changeover switch example
├── example_dol_starter.py                  # DOL motor starter example
├── example_dynamic_block.py                # Dynamic block with 5 terminals
├── example_dynamic_block_nonuniform.py     # Non-uniform dynamic block
├── example_emergency_stop.py               # Emergency stop circuit example
├── example_motor_control.py                # Motor control circuit example
├── example_motor_symbol.py                 # Motor symbol example
├── example_pin_configurations.py           # Pin configuration examples
├── example_power_distribution.py           # Complete power distribution system
├── example_project.py                      # Project API example
├── example_psu.py                          # Power supply unit example
├── example_switch.py                       # Simple switch circuit example
├── example_turn_switch.py                  # Turn switch example
├── example_two_coils.py                    # Two coils example
├── example_voltage_monitor.py              # Voltage monitor example
├── example_wire_labels.py                  # Wire labels example
└── output/                                 # Generated SVG files
```

## Constants File

The `constants.py` file contains **project-specific constants only**:
- **Terminal IDs** (e.g., `X1`, `X10`, `X20`)
- **Pin numbers/labels** (e.g., `L1`, `T1`, `1`)
- **Tag prefixes** (only if overriding library defaults)
- **File paths** for outputs

**Note**: Layout constants (grid size, spacing, offsets) are handled by the library's `model.constants` module and should NOT be defined in project-specific constants.

## Running Examples

### Run All Examples

```bash
uv run example_all_circuits.py
```

This will generate all circuit SVG files in the `output/` directory.

### Run Individual Examples

Each example can be run independently:

```bash
python example_dol_starter.py
python example_emergency_stop.py
python example_psu.py
python example_changeover.py
python example_voltage_monitor.py
python example_power_distribution.py
python example_motor_control.py
python example_switch.py
python example_dynamic_block.py
```

## Available Standard Circuits

### 1. DOL Motor Starter (`dol_starter`)
Direct-On-Line motor starter with:
- 3-pole circuit breaker
- Thermal overload protection
- Contactor
- Current transducer
- Optional auxiliary terminals (24V, GND)

**Use case**: Standard motor control for pumps, fans, conveyors

### 2. Emergency Stop (`emergency_stop`)
Single-pole emergency stop circuit with:
- Emergency stop assembly (NC contact)

**Use case**: Safety circuit for emergency shutdown

### 3. Power Supply Unit (`psu`)
AC to DC power supply with:
- AC input terminals (L/N)
- PSU block
- DC output terminals (24V/GND)

**Use case**: Converting AC mains to 24V DC for control circuits

### 4. Changeover Switch (`changeover`)
3-pole manual changeover switch with:
- Main supply input
- Emergency supply input
- Switch assembly (3-pole SPDT)
- Output terminal

**Use case**: Switching between main and backup power sources

### 5. Voltage Monitor (`voltage_monitor`)
Coil-based voltage monitoring circuit with:

- Coil circuit used as voltage monitor model
- Configurable terminal connections

**Use case**: Monitoring voltage levels via relay coil

### 6. Power Distribution (`power_distribution`)
Complete power distribution system combining:

- Changeover switch
- Power supply unit

**Use case**: Complete power management system

### 7. Motor Control (`motor_control`)
Control circuit with:
- Emergency stop integration
- Contactor coil
- Feedback contact
- Lights/switches output

**Use case**: Start/Stop control with latch or PLC integration

### 8. Simple Switch (`switch`)
Single-pole normally-open switch with:
- Input terminal
- NO contact
- Output terminal

**Use case**: Basic on/off control

### 9. Dynamic Block (`dynamic_block`)
Custom dynamic block symbol with 5 pins connected to 5 single pole terminals:
- Custom symbol creation with rectangular body
- 5 independent connection points
- Individual terminal connections
- Pin labeling demonstration

**Use case**: Template for creating custom multi-pin components (e.g., PLCs, custom modules, interface blocks)

## Customization

All standard circuits support extensive customization through parameters:

### Layout Parameters
- `spacing`: Horizontal spacing between circuits
- `symbol_spacing`: Vertical spacing between components
- `x`, `y`: Starting position

### Component Parameters
- `tag_prefix`: Component tag prefix (e.g., `"F"` for breakers)
- `pin_*`: Pin numbers/labels
- `terminal_*`: Terminal IDs

### Creation Parameters
- `count`: Number of circuit instances to create
- `start_indices`: Starting indices for autonumbering

See individual example files for detailed usage patterns.

## Integration with Projects

To integrate these examples into your project:

1. **Copy** `constants.py` to your project
2. **Customize** terminal IDs, pin numbers, and tags for your project
3. **Import** and use the standard circuits in your code:

```python
from pyschemaelectrical import create_autonumberer, render_system, std_circuits
from constants import Terminals

state = create_autonumberer()
state, circuit, terminals = std_circuits.dol_starter(
    state=state,
    x=0,
    y=0,
    tm_top=Terminals.MAIN_POWER,
    tm_bot=Terminals.MOTOR_1
)
render_system(circuit, "output/my_motor.svg")
```

## Library Architecture

The library follows a clean separation of concerns:

- **Library Constants** (`pyschemaelectrical.model.constants`): Layout, spacing, grid, standard tags
- **Project Constants** (`examples/constants.py`): Terminal IDs, pin numbers, file paths
- **Standard Circuits** (`pyschemaelectrical.std_circuits`): Pre-configured circuit builders
- **CircuitBuilder** (`pyschemaelectrical.builder`): Low-level circuit construction API

This ensures maximum reusability while maintaining flexibility for project-specific requirements.
