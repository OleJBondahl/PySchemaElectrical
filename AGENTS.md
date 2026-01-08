# PySchemaElectrical - Agent Guide

This document provides essential context and guidelines for AI agents working on the **PySchemaElectrical** repository.

## 1. Project Overview
**PySchemaElectrical** is a Python library designed to programmatically generate electrical schematics adhering to **IEC 60617** standards. It renders diagrams to **SVG** format.

## 2. Technical Stack
*   **Language**: Python 3.10+
*   **Package Manager**: `uv` (Universal Python Package Manager)
*   **Testing Framework**: `pytest`
*   **Linting/Formatting**: Follow standard Python PEP 8 conventions.

## 3. Architectural Principles
The codebase adheres to **Functional Programming** and **Data-Oriented** principles:

### Immutability
*   Core domain entities (e.g., `Symbol`, `line`, `Circle`, `Port`) are implemented as **Frozen Dataclasses**.
*   **Do not modify objects in place.** Always create new instances with updated values (e.g., using `dataclasses.replace`).

### Pure Functions
*   Symbol creation functions (e.g., `normally_open(label, pins)`) are pure factories that return a `Symbol` object.
*   Transformation functions (e.g., `translate(symbol, x, y)`, `rotate(symbol, angle)`) returns a **new** transformed object. They do **not** mutate the input.

### Coordinate System
*   **Grid**: The system uses a virtual grid where `GRID_SIZE = 5.0` mm.
*   **Axes**: SVG coordinate system (X increases to the right, Y increases downwards).
*   **Origin**: Symbols are typically defined with their geometric center or logical anchor at `(0,0)`.

## 4. Directory Structure
*   `src/pyschemaelectrical/`: Core library package.
    *   `core.py`: Base data structures (`Element`, `Symbol`, `Port`).
    *   `system.py`: High-level helper API (`add_symbol`, `auto_connect_circuit`, `render_system`).
    *   `primitives.py`: Graphical primitives (`Line`, `Circle`, `Text`).
    *   `renderer.py`: Logic to convert objects to SVG.
    *   `symbols/`: Library of electrical symbols (Contacts, Coils, Breakers, etc.).
*   `examples/`: Usage scripts (`demo_system.py`, etc.). Use these to validate changes.
*   `tests/`: Unit tests.

## 5. Development Workflow
*   **Running Code**: Use `uv run <script_path>` to execute Python scripts in the project environment.
    *   *Example*: `uv run examples/demo_system.py`
    *   *Example*: `uv run pytest`
*   **Creating Symbols**:
    1.  Define a constant size/geometry based on `GRID_SIZE`.
    2.  Use `standard_style()` for consistency.
    3.  Define connection points as `Port` objects.
    4.  Return a `Symbol` containing elements and ports.

## 6. Common Tasks
*   **Adding Dependencies**: Use `uv add <package>`.
*   **Visual Verification**: When changing graphics, run an example script and check the generated `.svg` file (if possible) or ensure the coordinate math is sound.

## 7. System Architecture Patterns

### 7.1 Terminal Sharing Strategy
PySchemaElectrical supports sophisticated terminal sharing across multiple circuits:

**Three-Pole Terminal Sharing (Motor Circuits)**:
- Terminal tags remain constant (e.g., `X1`, `X2`)
- Pin numbers auto-increment for each circuit
- Example: 
  * Circuit 1: X1 uses pins 1, 2, 3
  * Circuit 2: X1 uses pins 4, 5, 6
  * Circuit 3: X1 uses pins 7, 8, 9

**Single-Pole Terminal Sharing (Control Circuits)**:
- Terminal tags remain constant (e.g., `X10`, `X11`, `X12`)
- Single pin per circuit, auto-incremented
- Example:
  * Circuit 1: X10 uses pin 1
  * Circuit 2: X10 uses pin 2
  * Circuit 3: X10 uses pin 3

### 7.2 Autonumbering System
The `autonumbering.py` module provides state-based numbering:

**Component Tags**:
- Use `next_tag(state, prefix)` to get auto-incremented component tags
- Example: F1, F2, F3 for circuit breakers with prefix "F"
- State is threaded through all creation functions

**Terminal Pins**:
- Use `next_terminal_pins(state, poles)` for auto-incrementing pin numbers
- Automatically handles the spacing pattern required by terminal symbols
- For 3-pole: returns `('1', '', '2', '', '3', '')` pattern
- For 1-pole: returns `('1', '')` pattern

### 7.3 Complete System Architecture
A complete electrical system typically consists of:

**Motor Circuits** (Power Distribution):
```
X1 (Input Terminal) 
  -> F (Circuit Breaker)
  -> FT (Thermal Overload Protection)
  -> Q (Contactor - Main Power Contacts)
  -> Current Transducer (on leftmost wire)
  -> X2 (Output Terminal)
```

**Motor Control Circuits** (Logic/Control):
```
X10 (Input Terminal)
  -> S0 (Emergency Stop - Normally Closed)
  -> S1 (Start Button - Normally Open)
  -> S2 (SPDT Contact)
     NC path -> Q Coil (A1-A2) -> X11 (Terminal)
     NO path -> X12 (Terminal)
```

**Key Integration Points**:
- Each motor circuit has a corresponding control circuit
- The control circuit's coil tag matches the motor circuit's contactor tag (Q1, Q2, Q3)
- All terminals export to a single CSV file for complete system documentation

### 7.4 CSV Export System
The `system_analysis.py` module provides two key export functions:

**Terminal Export (`export_terminals_to_csv`)**:
- Format: `Component From, Pin From, Terminal Tag, Terminal Pin, Component To, Pin To`
- Empty cells indicate unconnected terminal sides (e.g., input terminals have no "Component From")
- All circuits in a system export to a single CSV file
- Useful for wire routing, installation, and documentation

**Component List Export (`export_components_to_csv`)**:
- Format: `Component Tag, Component Description, MPN`
- Currently only populates the Component Tag column  
- Description and MPN columns are placeholders for future enhancement
- Plans to support merging with project-specific CSV files containing:
  - Component descriptions (e.g., "24V Contactor", "Circuit Breaker 10A")
  - Manufacturer Part Numbers (MPNs)
- Extracts unique component tags from all Symbol elements in the system
- Useful for Bill of Materials (BOM) generation and procurement


## 8. Critical Rules
*   **Imports**: Use relative imports within the package (`from ..core import ...`) and absolute imports in examples.
*   **Paths**: Always use **Absolute Paths** for file I/O tools.
*   **No Side Effects**: Avoid global state. Functional pipelines are preferred.
*   **State Threading**: When using autonumbering, always thread the state through function calls and return updated state.

