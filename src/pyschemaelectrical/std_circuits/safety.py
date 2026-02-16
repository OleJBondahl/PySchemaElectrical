"""
Standard Safety Circuits.

This module provides standard safety circuit configurations.
All terminal IDs, tags, and pins are parameters with sensible defaults.
Layout values use constants from model.constants but can be overridden.
"""

from typing import Any, List, Optional, Tuple

from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.model.constants import (
    LayoutDefaults,
    StandardTags,
)
from pyschemaelectrical.symbols.assemblies import emergency_stop_assembly_symbol


def emergency_stop(
    state: Any,
    x: float,
    y: float,
    # Required terminal parameters
    tm_top: str,
    tm_bot: str,
    # Layout parameters (with defaults from constants)
    spacing: float = LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE,
    symbol_spacing: float = LayoutDefaults.SYMBOL_SPACING_DEFAULT,
    # Component parameters (with defaults)
    tag_prefix: str = StandardTags.SWITCH,
    # Multi-count and wire labels
    count: int = 1,
    wire_labels: Optional[List[str]] = None,
    **kwargs,
) -> Tuple[Any, Any, List[Any]]:
    """
    Create an Emergency Stop circuit.

    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        tm_top: Input terminal ID
        tm_bot: Output terminal ID
        spacing: Horizontal spacing between circuit instances
        symbol_spacing: Vertical spacing between components
        tag_prefix: Tag prefix for emergency stop (default: "S")
        count: Number of circuit instances.
        wire_labels: Wire label strings to apply per instance.

    Returns:
        Tuple of (state, circuit, used_terminals)
    """
    builder = CircuitBuilder(state)
    builder.set_layout(x, y, spacing=spacing, symbol_spacing=symbol_spacing)

    # 1. Input Terminal
    builder.add_terminal(tm_top, poles=1)

    # 2. Emergency Stop Assembly
    builder.add_component(
        emergency_stop_assembly_symbol,
        tag_prefix=tag_prefix,
        pins=("1", "2"),  # Default pins for NC contact inside assembly
    )

    # 3. Output Terminal
    builder.add_terminal(tm_bot, poles=1)

    result = builder.build(count=count, wire_labels=wire_labels)
    return result.state, result.circuit, result.used_terminals
