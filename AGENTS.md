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

## 7. Critical Rules
*   **Imports**: Use relative imports within the package (`from ..core import ...`) and absolute imports in examples.
*   **Paths**: Always use **Absolute Paths** for file I/O tools.
*   **No Side Effects**: Avoid global state. Functional pipelines are preferred.
