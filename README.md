# PySchemaElectrical

A Python library for creating electrical schematic diagrams programmatically following **IEC 60617** standards.

PySchemaElectrical provides a clean, functional API for generating professional electrical schematics as SVG files. Built with immutability and type safety in mind, it offers both a simple high-level API for common use cases and a powerful lower-level API for custom designs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/pyschemaelectrical.svg)](https://pypi.org/project/pyschemaelectrical/)

## Features

✨ **Simple API** - Create schematics with minimal code  
🎨 **IEC 60617 Compliant** - Industry-standard symbols  
🔒 **Type Safe** - Full type hints throughout  
🧊 **Immutable** - Functional programming principles  
📐 **Auto-Layout** - Automatic component positioning and wiring  
🏷️ **Wire Labels** - Add color and size specifications  
📊 **CSV Export** - Generate terminal connection lists  
🎯 **Modular** - Compose complex circuits from simple symbols

## Installation

### Using `uv` (recommended)

```bash
uv pip install pyschemaelectrical
```

### Using `pip`

```bash
pip install pyschemaelectrical
```

### From source

```bash
git clone https://github.com/OleJBondahl/PySchemaElectrical.git
cd PySchemaElectrical
uv pip install -e .
```

## Quick Start

### Simple API Example

The simple API is perfect for standard vertical circuits:

```python
from pyschemaelectrical.simple_api import Circuit, Terminal, Contact, Coil

# Create a circuit
circuit = Circuit()

# Add components - they're automatically positioned and connected!
circuit.add(Terminal("X1"))
circuit.add(Contact.NO("S1"))  # Normally Open contact
circuit.add(Coil("K1"))
circuit.add(Terminal("X2"))

# Render to SVG
circuit.render("my_circuit.svg")
```

**Output:**

![Simple Circuit Example](examples/output/simple_demo.svg)

That's it! Just **4 lines of code** created a complete schematic with proper spacing, connections, and labels.

### Three-Pole Motor Circuit

```python
from pyschemaelectrical.simple_api import Circuit, Terminal, Breaker, Protection

circuit = Circuit(spacing=40)  # Tighter spacing for 3-pole components

circuit.add(Terminal.three_pole("X1"))
circuit.add(Breaker("Q1"))
circuit.add(Protection("F1"))
circuit.add(Terminal.three_pole("X2"))

circuit.render("motor_circuit.svg", width="297mm", height="210mm")
```

### Traditional API Example

For more complex layouts and custom configurations, use the traditional API:

```python
from pyschemaelectrical.core import Point
from pyschemaelectrical.symbols.terminals import three_pole_terminal
from pyschemaelectrical.symbols.breakers import three_pole_circuit_breaker
from pyschemaelectrical.symbols.assemblies import contactor
from pyschemaelectrical.layout import auto_connect
from pyschemaelectrical.transform import translate
from pyschemaelectrical.renderer import render_to_svg

# Create symbols
x1 = three_pole_terminal("X1", pins=("1", "2", "3", "4", "5", "6"))
q1 = three_pole_circuit_breaker("Q1", pins=("1", "2", "3", "4", "5", "6"))
k1 = contactor("K1", poles=3)
x2 = three_pole_terminal("X2", pins=("1", "2", "3", "4", "5", "6"))

# Position symbols
elements = []
x1_placed = translate(x1, 50, 50)
q1_placed = translate(q1, 50, 100)
k1_placed = translate(k1, 50, 150)
x2_placed = translate(x2, 50, 200)

elements.extend([x1_placed, q1_placed, k1_placed, x2_placed])

# Connect symbols
elements.extend(auto_connect(x1_placed, q1_placed))
elements.extend(auto_connect(q1_placed, k1_placed))
elements.extend(auto_connect(k1_placed, x2_placed))

# Render
render_to_svg(elements, "traditional_circuit.svg", width="297mm", height="210mm")
```

**Output:**

![Motor Circuit Example](examples/output/demo_system.svg)

## API Overview

### Simple API Components

The simple API provides convenient wrapper classes:

- **`Circuit`** - Main circuit builder with automatic layout
- **`Terminal`** - Single and three-pole terminals
- **`Contact`** - NO (Normally Open), NC (Normally Closed), SPDT contacts
- **`Coil`** - Relay/contactor coils
- **`Breaker`** - Circuit breakers
- **`Protection`** - Thermal overload relays
- **`Assembly`** - Emergency stops, contactors

All components have sensible defaults (pin numbers, spacing, etc.) that follow IEC standards.

### Traditional API Modules

For advanced usage:

- **`core`** - Core data structures (Point, Symbol, Port, Element)
- **`symbols/`** - IEC 60617 symbol library (contacts, coils, terminals, etc.)
- **`primitives`** - Geometric primitives (Line, Circle, Text, etc.)
- **`layout`** - Auto-connection and layout functions
- **`transform`** - Translation, rotation, scaling
- **`renderer`** - SVG rendering
- **`system_analysis`** - CSV export for terminal lists

## Available Symbols

### Contacts
- Normally Open (NO)
- Normally Closed (NC)
- SPDT (Single Pole Double Throw)
- Three-pole variants

### Terminals
- Single-pole terminal
- Three-pole terminal block
- Custom terminal boxes

### Protection & Switching
- Circuit breakers (1 and 3-pole)
- Thermal overload relays
- Fuses

### Control Elements
- Coils (relay/contactor)
- Emergency stop assemblies
- Push buttons

### Assemblies
- Contactors (configurable poles)
- Motor control circuits
- Current transducers with terminal boxes

## Wire Labels

Add wire specifications (color, size) to your diagrams:

```python
from pyschemaelectrical.layout import auto_connect_labeled

# Define wire specs
wire_config = {
    "X1": [("RD", "2.5mm²"), ("BK", "2.5mm²"), ("BN", "2.5mm²")]
}

# Connect with labels
elements.extend(auto_connect_labeled(x1_placed, q1_placed, wire_config["X1"]))
```

## CSV Export

Generate terminal connection lists:

```python
from pyschemaelectrical.system_analysis import export_terminals_to_csv

export_terminals_to_csv(elements, "connections.csv")
```

Output format:
```csv
Terminal,Pin From,Component From,Pin From Label,Component To,Pin To,Pin To Label
X1,1,,,Q1,1,
X1,2,,,Q1,2,
...
```

## Examples

Check out the `examples/` directory for more complex demonstrations:

- **`simple_demo.py`** - Simple API basics
- **`demo_system.py`** - Multi-circuit system with autonumbering
- **`multi_circuit_demo.py`** - Multiple motor circuits side-by-side

Run any example:

```bash
uv run examples/simple_demo.py
```

Generated files are saved to `examples/output/`.

## Architecture

PySchemaElectrical follows **Clean Architecture** and **Functional Programming** principles:

- **Immutable data structures** - All entities are frozen dataclasses
- **Pure functions** - Core logic is side-effect free
- **Type safety** - Comprehensive type hints
- **Dependency injection** - Explicit dependencies
- **Separation of concerns** - Clear module boundaries

See [`AGENTS.md`](AGENTS.md) for detailed architectural guidelines.

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# With coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_symbols.py
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/OleJBondahl/PySchemaElectrical.git
cd PySchemaElectrical

# Install with dev dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Project Structure

```
PySchemaElectrical/
├── src/pyschemaelectrical/    # Main library
│   ├── core.py               # Core data structures
│   ├── primitives.py         # Geometric primitives
│   ├── symbols/              # Symbol library
│   ├── layout.py             # Layout functions
│   ├── renderer.py           # SVG rendering
│   ├── simple_api.py         # Simple API layer
│   └── ...
├── examples/                  # Example scripts
│   └── output/               # Generated SVGs
├── tests/                     # Test suite
├── docs/                      # Documentation
└── pyproject.toml            # Project configuration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines

1. Follow existing code style (functional, immutable, typed)
2. Add tests for new features
3. Update documentation
4. Use meaningful commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Ole Johan Bondahl**

## Acknowledgments

- IEC 60617 standard for electrical symbols
- Inspired by the need for programmatic electrical diagram generation
- Built with modern Python best practices

---

**Made with ❤️ for electrical engineers and automation professionals**
