# Quick Start Guide - PySchemaElectrical Examples

This quick start guide will help you get started with the PySchemaElectrical library examples.

## Prerequisites

1. Make sure the PySchemaElectrical library is installed:
   ```bash
   pip install -e .
   ```

2. Navigate to the examples directory:
   ```bash
   cd examples
   ```

## Generate All Examples (Recommended)

The easiest way to get started is to run all examples at once:

```bash
python example_all_circuits.py
```

This will generate 8 SVG files in the `output/` directory:
- `dol_starter.svg` - Direct-On-Line motor starter
- `emergency_stop.svg` - Emergency stop circuit
- `psu.svg` - Power supply unit
- `changeover.svg` - Changeover switch
- `voltage_monitor.svg` - Voltage monitoring circuit
- `power_distribution.svg` - Complete power distribution system
- `motor_control.svg` - Motor control circuit
- `switch.svg` - Simple switch circuit

## Run Individual Examples

You can also run individual examples:

```bash
python example_dol_starter.py        # Motor starter
python example_emergency_stop.py     # Safety circuit
python example_psu.py                # Power supply
python example_changeover.py         # Power switching
python example_voltage_monitor.py    # Voltage monitoring
python example_power_distribution.py # Complete system
python example_motor_control.py      # Control circuit
python example_switch.py             # Simple switch
```

## Customize for Your Project

1. **Edit `constants.py`** to match your project:
   - Update terminal IDs (e.g., `X1`, `X10`, `X20`)
   - Customize pin numbers if needed
   - Set output paths

2. **Modify example files** to create your circuits:
   - Change terminal assignments
   - Adjust positions (x, y coordinates)
   - Add multiple circuit instances using `count` parameter

## Example: Create Your Own Circuit

```python
from pathlib import Path
from pyschemaelectrical import create_autonumberer, std_circuits, render_system
from constants import Terminals, Paths

# Initialize
state = create_autonumberer()

# Create a motor starter
state, circuit, terminals = std_circuits.dol_starter(
    state=state,
    x=0,
    y=0,
    tm_top=Terminals.MAIN_POWER,
    tm_bot=Terminals.MOTOR_1,
    count=1  # Number of motor circuits
)

# Render to SVG
render_system(circuit, "output/my_motor.svg")
print(f"Circuit saved! Used terminals: {terminals}")
```

## Understanding the Constants

The `constants.py` file contains **project-specific** values only:

### ✅ **Include in `constants.py`**:
- Terminal IDs (which terminal block to use)
- Pin numbers (which physical pins to connect)
- Tag prefixes (if overriding library defaults)
- File paths

### ❌ **Do NOT include in `constants.py`**:
- Grid size (handled by library)
- Spacing between components (handled by library)
- Symbol dimensions (handled by library)
- Layout offsets (handled by library)

These layout constants are in `pyschemaelectrical.model.constants` and should only be changed at the library level.

## Next Steps

1. **Explore the SVG files** in `output/` to see what each circuit looks like
2. **Read `README.md`** for detailed documentation on all standard circuits
3. **Experiment** by modifying the example files
4. **Build your project** by combining multiple circuits

## Need Help?

- Review the **README.md** for comprehensive documentation
- Check the library's **pydoc** documentation for each function
- Look at the `src/pyschemaelectrical/std_circuits/` source code for implementation details

Happy circuit designing! 🔌⚡
