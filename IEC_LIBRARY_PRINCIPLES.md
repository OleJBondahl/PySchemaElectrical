# IEC Symbol Library - Driving Principles

This document outlines the core architectural and design principles for the IEC Symbol Library project. All agents and contributors should adhere to these guidelines to ensure consistency, composability, and maintainability.

## 1. Functional Programming First
*   **Immutability**: All core data structures (`Point`, `Style`, `Symbol`, `Port`) must be immutable (frozen dataclasses). Transformations never mutate state; they return new instances.
*   **Pure Functions**: Functions should yield deterministic results based solely on their inputs. Avoid side effects (like global state or printing) within the core logic.
*   **Composition**: Complex behaviors should be built by composing simple, single-purpose functions.

## 2. Declarative Design
*   **What, not How**: The API should allow users to describe *what* the schematic looks like (e.g., "A breaker connected to a motor"), rather than *how* to draw it (e.g., "draw line to x,y").
*   **Explicit Data**: The structure of the schematic is a data structure (the Scene Graph or Component Tree) independent of the rendering target.

## 3. Clear Abstraction Layers
1.  **Primitives**: The lowest level. Lines, circles, primitive geometry. No electrical meaning.
2.  **Symbols**: Geometric primitives combined with metadata (Ports, Labels). These represent physical components (IEC 60617).
3.  **Schematic/Layout**: Logic for arranging symbols and routing wires. The "Canvas".
4.  **rendering**: The act of turning the internal representation into an artifact (SVG Code).

## 4. Visual Quality & Standards
*   **IEC 60617 Compliance**: Symbols should visually match the international standard.
*   **Grid System**: Symbols should be designed on a grid (e.g., 2.5mm or 5mm base) to ensure they snap together cleanly.

## 5. Developer Experience (DX)
*   **Type Safety**: Use Python type hints strictly.
*   **Discoverability**: The API should be intuitive.
*   **Self-Documentation**: Code should be self-explanatory where possible.
