"""
Inline circuit descriptors for PySchemaElectrical.

Provides lightweight descriptor types for defining linear circuits
declaratively without needing a builder function.

Usage:
    from pyschemaelectrical import ref, comp, term
    from pyschemaelectrical.symbols import coil_symbol

    components = [
        ref("PLC:DO"),
        comp(coil_symbol, "K", pins=("A1", "A2")),
        term("X103"),
    ]
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class RefDescriptor:
    """Describes a reference symbol (PLC, etc.)."""

    terminal_id: str


@dataclass(frozen=True)
class CompDescriptor:
    """Describes a component with tag prefix and pins."""

    symbol_fn: Any  # symbol factory function
    tag_prefix: str
    pins: Tuple[str, ...] = ()


@dataclass(frozen=True)
class TermDescriptor:
    """Describes a physical terminal."""

    terminal_id: str
    poles: int = 1
    pins: Optional[Tuple[str, ...]] = None


def ref(terminal_id: str) -> RefDescriptor:
    """Create a reference descriptor (PLC, etc.)."""
    return RefDescriptor(terminal_id)


def comp(symbol_fn: Any, tag_prefix: str, pins: Tuple[str, ...] = ()) -> CompDescriptor:
    """Create a component descriptor."""
    return CompDescriptor(symbol_fn, tag_prefix, pins)


def term(terminal_id: str, poles: int = 1, pins: Optional[Tuple[str, ...]] = None) -> TermDescriptor:
    """Create a terminal descriptor."""
    return TermDescriptor(terminal_id, poles, pins)


Descriptor = Union[RefDescriptor, CompDescriptor, TermDescriptor]


def build_from_descriptors(
    state: Any,
    descriptors: List[Descriptor],
    x: float = 0.0,
    y: float = 0.0,
    spacing: float = 80.0,
    count: int = 1,
    wire_labels: Optional[List[str]] = None,
    reuse_tags: Optional[Dict[str, Any]] = None,
    tag_generators: Optional[Dict[str, Callable]] = None,
    start_indices: Optional[Dict[str, int]] = None,
    terminal_start_indices: Optional[Dict[str, int]] = None,
) -> "BuildResult":
    """
    Build a circuit from a list of descriptors.

    Creates a CircuitBuilder internally, calls add_reference/add_component/add_terminal
    for each descriptor, and builds with the given parameters.

    Args:
        state: Autonumbering state.
        descriptors: List of RefDescriptor, CompDescriptor, or TermDescriptor.
        x: Start X position.
        y: Start Y position.
        spacing: Horizontal spacing between instances.
        count: Number of instances to build.
        wire_labels: Wire label strings per instance.
        reuse_tags: Dict mapping tag prefix to BuildResult for tag reuse.
        tag_generators: Custom tag generator functions.
        start_indices: Override tag counters.
        terminal_start_indices: Override terminal pin counters.

    Returns:
        BuildResult with state, circuit, used_terminals, and component_map.
    """
    from pyschemaelectrical.builder import CircuitBuilder

    builder = CircuitBuilder(state)
    builder.set_layout(x=x, y=y, spacing=spacing)

    for desc in descriptors:
        if isinstance(desc, RefDescriptor):
            builder.add_reference(desc.terminal_id)
        elif isinstance(desc, CompDescriptor):
            pins = desc.pins if desc.pins else None
            builder.add_component(desc.symbol_fn, desc.tag_prefix, pins=pins)
        elif isinstance(desc, TermDescriptor):
            builder.add_terminal(desc.terminal_id, poles=desc.poles, pins=desc.pins)

    return builder.build(
        count=count,
        wire_labels=wire_labels,
        reuse_tags=reuse_tags,
        tag_generators=tag_generators,
        start_indices=start_indices,
        terminal_start_indices=terminal_start_indices,
    )
