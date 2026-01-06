---
trigger: always_on
---

# Gemini Agent Guidelines

This document summarizes the architectural principles and coding standards established for the **WireViz Generator** project. Use these guidelines for future development to ensure consistency.

## 1. Architectural Patterns
*   **Clean Architecture**: Enforce strict separation of concerns.
*   **Dependency Injection**: Orchestrators (e.g., `WorkflowManager`) must receive their dependencies (DataSources) via `__init__`, not instantiate them internally.

## 2. Data-Oriented Programming
*   **Immutability**: Use `@dataclass(frozen=True)` for all domain entities. Data should flow but not change state in place.
*   **Type Safety**

## 3. Implementation Rules
*   **Pure Core, Imperative Shell**:
    *   Core logic functions must be deterministic and side-effect free.
    *   Push I/O (Database access, File existence checks) to the "Shell" (`main.py` / `workflow_manager.py`).
*   **Error Handling**:
    *   **Never** use `sys.exit()` in library code.
    *   Raise specific custom exceptions
    *   Handle exceptions only at the entry point

## 4. Documentation Standards
*   **In-Code**: Comprehensive `pydoc` docstrings for all modules, classes, and functions.
*   **Architecture**: Use **Mermaid** diagrams for Component and Sequence flows.


# 5. Testing Standards
*   **Unit Tests**: Write unit tests for all core logic functions.
*   **Integration Tests**: Write integration tests for all data flows.
*   **End-to-End Tests**: Write end-to-end tests for all user flows.
    **Coverage**: Use *pytest* to measure test coverage.

use py to run python files, not python command.