"""
Unified Circuit Builder.

This module provides a powerful, high-level API for constructing electrical circuits.
It abstracts away the complexity of coordinate management, manual connection registration,
and multi-pole wiring.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pyschemaelectrical.layout.layout import create_horizontal_layout
from pyschemaelectrical.symbols.terminals import (
    terminal_symbol,
    three_pole_terminal_symbol,
)
from pyschemaelectrical.system.connection_registry import register_connection
from pyschemaelectrical.system.system import Circuit, add_symbol, auto_connect_circuit
from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins
from pyschemaelectrical.utils.utils import set_tag_counter, set_terminal_counter


@dataclass(frozen=True)
class LayoutConfig:
    """Configuration for circuit layout."""

    start_x: float
    start_y: float
    spacing: float = 0  # Horizontal spacing between circuit instances
    symbol_spacing: float = 50  # Vertical spacing between components
    label_pos: str = "left"  # Default label position for terminals


@dataclass(frozen=True)
class ComponentSpec:
    """Declarative specification for a component in a circuit."""

    func: Optional[Callable]  # None for terminals
    kind: str = "symbol"  # 'symbol' or 'terminal'
    tag_prefix: Optional[str] = None
    poles: int = 1
    pins: Optional[Union[List[str], Tuple[str, ...]]] = None
    kwargs: Dict[str, Any] = field(default_factory=dict)

    # Layout control
    x_offset: float = 0.0
    y_increment: Optional[float] = None

    # Connection control
    auto_connect_next: bool = True

    # Horizontal placement reference (index of component this was placed_right of)
    placed_right_of: Optional[int] = None

    def get_y_increment(self, default: float) -> float:
        return self.y_increment if self.y_increment is not None else default


@dataclass
class CircuitSpec:
    """Complete specification for a circuit definition."""

    components: List[ComponentSpec] = field(default_factory=list)
    layout: LayoutConfig = field(default_factory=lambda: LayoutConfig(0, 0))
    manual_connections: List[Tuple[int, int, int, int, str, str]] = field(
        default_factory=list
    )
    terminal_map: Dict[str, Any] = field(default_factory=dict)
    # Horizontal matching connections: (idx_a, idx_b, pin_filter, side_a, side_b)
    matching_connections: List[Tuple[int, int, Optional[List[str]], str, str]] = field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# ComponentRef / PortRef — named component references (Task 9A)
# ---------------------------------------------------------------------------


@dataclass
class PortRef:
    """Reference to a specific port on a component."""

    component: "ComponentRef"
    port: Union[str, int]  # Pin name ("L", "A1") or pole index (0, 1, 2)


@dataclass
class ComponentRef:
    """
    Reference to a component in a CircuitBuilder.

    Supports tuple unpacking for backwards compatibility:
        _, idx = builder.add_component(...)   # still works
    """

    _builder: "CircuitBuilder"
    _index: int
    tag_prefix: str = ""

    def pin(self, pin_id: str) -> PortRef:
        """Reference a specific port by pin name."""
        return PortRef(self, pin_id)

    def pole(self, pole_idx: int) -> PortRef:
        """Reference a port by pole index (backwards compatibility)."""
        return PortRef(self, pole_idx)

    def __iter__(self):
        """Support tuple unpacking: _, idx = builder.add_component(...)"""
        return iter((self._builder, self._index))


@dataclass
class BuildResult:
    """Result of a circuit build operation."""

    state: Dict[str, Any]
    circuit: Circuit
    used_terminals: List[Any]
    component_map: Dict[str, List[str]] = field(default_factory=dict)

    def __iter__(self):
        return iter((self.state, self.circuit, self.used_terminals))

    def reuse_tags(self, prefix: str) -> Callable:
        """
        Returns a tag generator that yields tags from this result's component_map.

        Use with the reuse_tags parameter on build():
            result_b = builder_b.build(reuse_tags={"K": result_a})
        """
        tags = iter(self.component_map.get(prefix, []))

        def generator(state):
            from pyschemaelectrical.exceptions import TagReuseExhausted

            try:
                return state, next(tags)
            except StopIteration:
                raise TagReuseExhausted(prefix, list(self.component_map.get(prefix, [])))

        return generator


class CircuitBuilder:
    """
    Unified builder for 1-pole, 2-pole, and 3-pole circuits.
    Now acts as a fluent builder for CircuitSpec.
    """

    def __init__(self, state: Any):
        self._initial_state = state
        self._spec = CircuitSpec()
        # Fixed tag generators added by add_reference()
        self._fixed_tag_generators: Dict[str, Callable] = {}

    def set_layout(
        self, x: float, y: float, spacing: float = 150, symbol_spacing: float = 50
    ) -> "CircuitBuilder":
        """Configure the layout settings."""
        self._spec.layout = LayoutConfig(
            start_x=x, start_y=y, spacing=spacing, symbol_spacing=symbol_spacing
        )
        return self

    def add_terminal(
        self,
        tm_id: Any,
        poles: int = 1,
        pins: Optional[Union[List[str], Tuple[str, ...]]] = None,
        label_pos: Optional[str] = None,
        logical_name: Optional[str] = None,
        x_offset: float = 0.0,
        y_increment: Optional[float] = None,
        auto_connect_next: bool = True,
        **kwargs,
    ) -> "ComponentRef":
        """
        Add a terminal block.

        Returns: ComponentRef (supports tuple unpacking: _, idx = builder.add_terminal(...))
        """
        if logical_name:
            self._spec.terminal_map[logical_name] = tm_id

        spec = ComponentSpec(
            func=None,
            kind="terminal",
            poles=poles,
            pins=pins,
            x_offset=x_offset,
            y_increment=y_increment,
            auto_connect_next=auto_connect_next,
            kwargs={
                "tm_id": tm_id,
                "label_pos": label_pos,
                "logical_name": logical_name,
                **kwargs,
            },
        )
        self._spec.components.append(spec)
        idx = len(self._spec.components) - 1
        return ComponentRef(self, idx, str(tm_id))

    def add_component(
        self,
        symbol_func: Callable,
        tag_prefix: str,
        poles: int = 1,
        pins: Optional[Union[List[str], Tuple[str, ...]]] = None,
        x_offset: float = 0.0,
        y_increment: Optional[float] = None,
        auto_connect_next: bool = True,
        **kwargs,
    ) -> "ComponentRef":
        """
        Add a generic component/symbol.

        Returns: ComponentRef (supports tuple unpacking: _, idx = builder.add_component(...))
        """
        spec = ComponentSpec(
            func=symbol_func,
            tag_prefix=tag_prefix,
            kind="symbol",
            poles=poles,
            pins=pins,
            x_offset=x_offset,
            y_increment=y_increment,
            auto_connect_next=auto_connect_next,
            kwargs=kwargs,
        )
        self._spec.components.append(spec)
        idx = len(self._spec.components) - 1
        return ComponentRef(self, idx, tag_prefix)

    def add_reference(
        self,
        ref_id: str,
        x_offset: float = 0.0,
        y_increment: Optional[float] = None,
        auto_connect_next: bool = True,
        **kwargs,
    ) -> "ComponentRef":
        """
        Add a reference symbol (e.g., PLC:DO, PLC:AI).

        Reference symbols always use their ID as the tag (not auto-numbered).
        No manual tag_generators setup needed.

        Args:
            ref_id: The reference identifier (e.g., "PLC:DO").
            x_offset: Horizontal offset.
            y_increment: Vertical spacing override.
            auto_connect_next: Whether to auto-connect to next component.

        Returns: ComponentRef
        """
        from pyschemaelectrical.symbols.references import ref_symbol

        # Register a fixed tag generator for this reference ID
        def fixed_gen(state):
            return state, ref_id

        self._fixed_tag_generators[ref_id] = fixed_gen

        return self.add_component(
            ref_symbol,
            tag_prefix=ref_id,
            x_offset=x_offset,
            y_increment=y_increment,
            auto_connect_next=auto_connect_next,
            **kwargs,
        )

    def place_right(
        self,
        ref: "ComponentRef",
        symbol_func: Callable,
        tag_prefix: str,
        pins: Optional[Union[List[str], Tuple[str, ...]]] = None,
        spacing: float = 40.0,
        poles: int = 1,
        auto_connect_next: bool = False,
        **kwargs,
    ) -> "ComponentRef":
        """
        Place a component to the right of an existing one at the same Y position.

        Does NOT advance the vertical stack pointer. The next add_component()
        will be placed below the last vertically-added component, not below this one.

        Args:
            ref: ComponentRef of the component to place next to.
            symbol_func: Symbol factory function.
            tag_prefix: Tag prefix for autonumbering.
            pins: Pin names.
            spacing: Horizontal distance from ref component.
            poles: Number of poles.
            auto_connect_next: Whether to auto-connect to next component (default False).

        Returns: ComponentRef for the new component.
        """
        ref_idx = ref._index

        spec = ComponentSpec(
            func=symbol_func,
            tag_prefix=tag_prefix,
            kind="symbol",
            poles=poles,
            pins=pins,
            x_offset=spacing,  # x_offset relative to the reference component
            y_increment=0,  # Don't advance vertical stack
            auto_connect_next=auto_connect_next,
            kwargs=kwargs,
            placed_right_of=ref_idx,
        )
        self._spec.components.append(spec)
        idx = len(self._spec.components) - 1
        return ComponentRef(self, idx, tag_prefix)

    def connect_matching(
        self,
        ref_a: "ComponentRef",
        ref_b: "ComponentRef",
        pins: Optional[List[str]] = None,
        side_a: str = "right",
        side_b: str = "left",
    ) -> "CircuitBuilder":
        """
        Connect two components horizontally on pins that share the same name.

        Draws horizontal wires between matching pin pairs. Only pins with
        identical names on both components are connected.

        Args:
            ref_a: First component reference.
            ref_b: Second component reference.
            pins: Explicit pin filter. If None, connects all matching pins.
            side_a: Connection side on ref_a (default "right").
            side_b: Connection side on ref_b (default "left").

        Returns: self for chaining.
        """
        self._spec.matching_connections.append(
            (ref_a._index, ref_b._index, pins, side_a, side_b)
        )
        return self

    def connect(
        self,
        a: PortRef,
        b: PortRef,
        side_a: Optional[str] = None,
        side_b: Optional[str] = None,
    ) -> "CircuitBuilder":
        """
        Connect two ports by pin name or pole index.

        This is the pin-based connection API that coexists with add_connection().

        Args:
            a: Source port reference (e.g., tm.pin("1") or cb.pole(0)).
            b: Target port reference (e.g., cb.pin("1") or psu.pin("L")).
            side_a: Connection side on component a. If None, inferred.
            side_b: Connection side on component b. If None, inferred.

        Returns: self for chaining.
        """
        # Resolve pin names to pole indices
        idx_a = a.component._index
        idx_b = b.component._index
        pole_a = self._resolve_port_ref_to_pole(a)
        pole_b = self._resolve_port_ref_to_pole(b)

        # Default sides
        if side_a is None:
            side_a = "bottom"
        if side_b is None:
            side_b = "top"

        return self.add_connection(idx_a, pole_a, idx_b, pole_b, side_a, side_b)

    def _resolve_port_ref_to_pole(self, port_ref: PortRef) -> int:
        """Resolve a PortRef to a pole index."""
        if isinstance(port_ref.port, int):
            return port_ref.port

        # It's a pin name — find the pole index
        idx = port_ref.component._index
        spec = self._spec.components[idx]

        if spec.pins:
            pins_list = list(spec.pins)
            # Check for interleaved In/Out pairs (poles * 2 pins)
            if len(pins_list) == spec.poles * 2:
                # Find the pin in the interleaved list, convert to pole
                for i, pin in enumerate(pins_list):
                    if pin == port_ref.port:
                        return i // 2 if spec.kind == "symbol" else i // 2
                # Also check direct index
                try:
                    return pins_list.index(port_ref.port)
                except ValueError:
                    pass
            else:
                # Direct indexing
                try:
                    return pins_list.index(port_ref.port)
                except ValueError:
                    pass

        from pyschemaelectrical.exceptions import PortNotFoundError

        available = list(spec.pins) if spec.pins else []
        tag = spec.tag_prefix or spec.kwargs.get("tm_id", "unknown")
        raise PortNotFoundError(str(tag), str(port_ref.port), available)

    def add_connection(
        self,
        comp_idx_a: int,
        pole_idx_a: int,
        comp_idx_b: int,
        pole_idx_b: int,
        side_a: str = "bottom",
        side_b: str = "top",
    ) -> "CircuitBuilder":
        """
        Add an explicit connection between components (by index in builder list).
        Indices are 0-based.
        """
        self._spec.manual_connections.append(
            (comp_idx_a, pole_idx_a, comp_idx_b, pole_idx_b, side_a, side_b)
        )
        return self

    def _validate_connections(self) -> None:
        """
        Validate all connections before building.

        Raises:
            ComponentNotFoundError: If a connection references invalid component index
            PortNotFoundError: If a connection references invalid port
        """
        from pyschemaelectrical.exceptions import ComponentNotFoundError

        max_idx = len(self._spec.components) - 1

        for idx_a, p_a, idx_b, p_b, side_a, side_b in self._spec.manual_connections:
            if idx_a > max_idx:
                raise ComponentNotFoundError(idx_a, max_idx)
            if idx_b > max_idx:
                raise ComponentNotFoundError(idx_b, max_idx)

    def build(
        self,
        count: int = 1,
        start_indices: Optional[Dict[str, int]] = None,
        terminal_start_indices: Optional[Dict[str, int]] = None,
        tag_generators: Optional[Dict[str, Callable]] = None,
        terminal_maps: Optional[Dict[str, Any]] = None,
        reuse_tags: Optional[Dict[str, "BuildResult"]] = None,
        wire_labels: Optional[List[str]] = None,
    ) -> BuildResult:
        """
        Generate the circuits.

        Args:
            count: Number of circuit instances to create.
            start_indices: Override tag counters (e.g., {"K": 3}).
            terminal_start_indices: Override terminal pin counters.
            tag_generators: Custom tag generator functions.
            terminal_maps: Terminal ID overrides by logical name.
            reuse_tags: Dict mapping tag prefix to BuildResult whose tags to reuse.
                        e.g., {"K": coil_result} reuses K tags from coil_result.
            wire_labels: Wire label strings to apply to vertical wires.
                         Applied per instance (cycled if count > 1).

        Returns:
            BuildResult with state, circuit, used_terminals, and component_map.
        """
        self._validate_connections()
        state = self._initial_state

        # Apply override counters
        if start_indices:
            for prefix, val in start_indices.items():
                state = set_tag_counter(state, prefix, val)
        if terminal_start_indices:
            for t_id, val in terminal_start_indices.items():
                state = set_terminal_counter(state, t_id, val)

        # Build effective tag_generators by merging fixed generators,
        # reuse_tags generators, and explicit tag_generators.
        effective_generators = self._fixed_tag_generators.copy()
        if reuse_tags:
            for prefix, source_result in reuse_tags.items():
                if isinstance(source_result, BuildResult):
                    effective_generators[prefix] = source_result.reuse_tags(prefix)
                elif callable(source_result):
                    effective_generators[prefix] = source_result
        if tag_generators:
            effective_generators.update(tag_generators)

        final_tag_generators = effective_generators if effective_generators else None

        captured_tags: Dict[str, List[str]] = {}

        def single_instance_gen(s, x, y, gens, tm):
            res = _create_single_circuit_from_spec(s, x, y, self._spec, gens, tm)
            # res is (state, elements, instance_tags)
            # Update captured tags
            for prefix, tag_val in res[2].items():
                if prefix not in captured_tags:
                    captured_tags[prefix] = []
                captured_tags[prefix].append(tag_val)
            return res[0], res[1]

        # Use generic layout
        final_state, elements = create_horizontal_layout(
            state=state,
            start_x=self._spec.layout.start_x,
            start_y=self._spec.layout.start_y,
            count=count,
            spacing=self._spec.layout.spacing,
            generator_func_single=lambda s,
            x,
            y,
            gens,
            tm,
            instance: single_instance_gen(s, x, y, gens, tm),
            default_tag_generators={},
            tag_generators=final_tag_generators,
            terminal_maps=terminal_maps,
        )

        c = Circuit(elements=elements)

        # Apply wire labels if provided
        if wire_labels is not None:
            from pyschemaelectrical.layout.wire_labels import add_wire_labels_to_circuit

            c = add_wire_labels_to_circuit(c, wire_labels)

        # Extract used terminals
        used_terminals = []
        for comp in self._spec.components:
            if comp.kind == "terminal":
                tid = comp.kwargs.get("tm_id")
                lname = comp.kwargs.get("logical_name")
                if lname and lname in self._spec.terminal_map:
                    tid = self._spec.terminal_map[lname]
                if tid not in used_terminals:
                    used_terminals.append(tid)

        return BuildResult(
            state=final_state,
            circuit=c,
            used_terminals=used_terminals,
            component_map=captured_tags,
        )


def _create_single_circuit_from_spec(
    state,
    x,
    y,
    spec: CircuitSpec,
    tag_generators: Optional[Dict] = None,
    terminal_maps: Optional[Dict] = None,
) -> Tuple[Any, List[Any], Dict[str, str]]:
    """
    Pure functional core to create a single instance from a spec.
    Returns: (new_state, elements, map_of_tags_for_this_instance)
    """
    c = Circuit()
    instance_tags = {}

    realized_components = []
    current_y = y

    # Track the last vertically-added component's Y for place_right support
    last_vertical_y = y

    # --- Phase 1: State Mutation & Tagging ---
    for comp_idx, component_spec in enumerate(spec.components):
        tag = None
        pins = []

        if component_spec.kind == "terminal":
            tid = component_spec.kwargs["tm_id"]
            lname = component_spec.kwargs.get("logical_name")

            # Resolve Terminal ID
            # 1. Check passed terminal_maps (runtime override)
            if terminal_maps and lname and lname in terminal_maps:
                tid = terminal_maps[lname]
            # 2. Check spec terminal_map (default/configured)
            elif lname and lname in spec.terminal_map:
                tid = spec.terminal_map[lname]

            if component_spec.pins:
                pins = list(component_spec.pins)
            else:
                state, pins = next_terminal_pins(state, tid, component_spec.poles)
            tag = str(tid)

        elif component_spec.kind == "symbol":
            # Tag generation
            # 1. Check tag_generators
            prefix = component_spec.tag_prefix
            if tag_generators and prefix and prefix in tag_generators:
                # Generator signature: s -> (s, tag)
                state, tag = tag_generators[prefix](state)
            else:
                state, tag = next_tag(state, prefix)
            instance_tags[prefix] = tag

            if component_spec.pins:
                pins = list(component_spec.pins)

        # Handle Y position for placed_right_of components
        if component_spec.placed_right_of is not None:
            # Use the Y of the reference component, not the current stack pointer
            ref_rc = realized_components[component_spec.placed_right_of]
            comp_y = ref_rc["y"]
        else:
            comp_y = current_y
            # Only advance vertical stack for normally-placed components
            y_inc = component_spec.get_y_increment(spec.layout.symbol_spacing)
            current_y += y_inc

        realized_components.append(
            {"spec": component_spec, "tag": tag, "pins": pins, "y": comp_y}
        )

    # --- Phase 2: Connection Registration ---
    # 1. Automatic Linear Connections
    for i in range(len(realized_components) - 1):
        curr = realized_components[i]
        next_comp = realized_components[i + 1]

        if not curr["spec"].auto_connect_next:
            continue

        # Skip auto-connect for place_right components
        if next_comp["spec"].placed_right_of is not None:
            continue

        poles = min(curr["spec"].poles, next_comp["spec"].poles)

        for p in range(poles):
            curr_pin = _resolve_pin(curr, p, is_input=False)
            next_pin = _resolve_pin(next_comp, p, is_input=True)

            if curr["spec"].kind == "terminal" and next_comp["spec"].kind == "symbol":
                # Current is Terminal: Use registry pin for Terminal
                reg_pin_curr = _resolve_registry_pin(curr, p)
                state = register_connection(
                    state,
                    curr["tag"],
                    reg_pin_curr,
                    next_comp["tag"],
                    next_pin,
                    side="bottom",
                )
            elif curr["spec"].kind == "symbol" and next_comp["spec"].kind == "terminal":
                # Next is Terminal: Use registry pin for Terminal
                reg_pin_next = _resolve_registry_pin(next_comp, p)
                state = register_connection(
                    state,
                    next_comp["tag"],
                    reg_pin_next,
                    curr["tag"],
                    curr_pin,
                    side="top",
                )

    # 2. Manual Connections
    for idx_a, p_a, idx_b, p_b, side_a, side_b in spec.manual_connections:
        if idx_a >= len(realized_components) or idx_b >= len(realized_components):
            continue

        comp_a = realized_components[idx_a]
        comp_b = realized_components[idx_b]

        pin_a = _resolve_pin(comp_a, p_a, is_input=(side_a == "top"))
        pin_b = _resolve_pin(comp_b, p_b, is_input=(side_b == "top"))

        if comp_a["spec"].kind == "terminal" and comp_b["spec"].kind == "symbol":
            reg_pin_a = _resolve_registry_pin(comp_a, p_a)
            state = register_connection(
                state, comp_a["tag"], reg_pin_a, comp_b["tag"], pin_b, side=side_a
            )
        elif comp_a["spec"].kind == "symbol" and comp_b["spec"].kind == "terminal":
            reg_pin_b = _resolve_registry_pin(comp_b, p_b)
            state = register_connection(
                state, comp_b["tag"], reg_pin_b, comp_a["tag"], pin_a, side=side_b
            )

    # --- Phase 3: Instantiation ---
    from pyschemaelectrical.model.parts import standard_style
    from pyschemaelectrical.model.primitives import Line

    for comp_idx, rc in enumerate(realized_components):
        component_spec = rc["spec"]
        tag = rc["tag"]

        # Calculate X position
        if component_spec.placed_right_of is not None:
            ref_rc = realized_components[component_spec.placed_right_of]
            ref_x_offset = ref_rc["spec"].x_offset
            if ref_rc["spec"].placed_right_of is not None:
                # Chain: this is placed right of something also placed right
                # Walk back to get the absolute x offset
                ref_x_offset = _get_absolute_x_offset(realized_components, component_spec.placed_right_of)
            final_x = x + ref_x_offset + component_spec.x_offset
        else:
            final_x = x + component_spec.x_offset

        sym = None
        if component_spec.kind == "terminal":
            lpos = component_spec.kwargs.get("label_pos")
            if component_spec.poles == 3:
                sym = three_pole_terminal_symbol(tag, pins=rc["pins"], label_pos=lpos)
            else:
                sym = terminal_symbol(tag, pins=rc["pins"], label_pos=lpos)

        elif component_spec.kind == "symbol":
            kwargs = component_spec.kwargs.copy()
            if rc["pins"]:
                # Explicitly pass resolved pins to the symbol factory so it can render labels
                sym = component_spec.func(tag, pins=rc["pins"], **kwargs)
            else:
                sym = component_spec.func(tag, **kwargs)

        if sym:
            # Respect auto_connect configuration
            if not component_spec.auto_connect_next:
                # Since Symbol is frozen, use replace
                from dataclasses import replace

                sym = replace(sym, skip_auto_connect=True)

            placed_sym = add_symbol(c, sym, final_x, rc["y"])
            rc["symbol"] = placed_sym  # Store placed symbol for manual connection phase

    # --- Phase 4: Graphics ---
    # 1. Manual Connections Rendering
    style = standard_style()
    for idx_a, p_a, idx_b, p_b, side_a, side_b in spec.manual_connections:
        if idx_a >= len(realized_components) or idx_b >= len(realized_components):
            continue

        comp_a = realized_components[idx_a]
        comp_b = realized_components[idx_b]

        if "symbol" not in comp_a or "symbol" not in comp_b:
            continue

        sym_a = comp_a["symbol"]
        sym_b = comp_b["symbol"]

        pin_a = _resolve_pin(comp_a, p_a, is_input=(side_a == "top"))
        pin_b = _resolve_pin(comp_b, p_b, is_input=(side_b == "top"))

        port_a = sym_a.ports.get(pin_a)
        port_b = sym_b.ports.get(pin_b)

        if port_a and port_b:
            # Draw direct line
            line = Line(port_a.position, port_b.position, style)
            c.elements.append(line)

    # 2. Matching Connections Rendering (connect_matching)
    for idx_a, idx_b, pin_filter, side_a, side_b in spec.matching_connections:
        if idx_a >= len(realized_components) or idx_b >= len(realized_components):
            continue

        comp_a = realized_components[idx_a]
        comp_b = realized_components[idx_b]

        if "symbol" not in comp_a or "symbol" not in comp_b:
            continue

        sym_a = comp_a["symbol"]
        sym_b = comp_b["symbol"]

        # Find matching pin names
        pins_a = set(comp_a["pins"]) if comp_a["pins"] else set()
        pins_b = set(comp_b["pins"]) if comp_b["pins"] else set()
        common_pins = pins_a & pins_b

        if pin_filter is not None:
            common_pins = common_pins & set(pin_filter)

        # Draw horizontal wires for each matching pin
        for pin_name in common_pins:
            port_a = sym_a.ports.get(pin_name)
            port_b = sym_b.ports.get(pin_name)
            if port_a and port_b:
                line = Line(port_a.position, port_b.position, style)
                c.elements.append(line)

    # 3. Auto Connections
    auto_connect_circuit(c)

    return state, c.elements, instance_tags


def _get_absolute_x_offset(realized_components, comp_idx):
    """Walk back through place_right chain to compute absolute x offset."""
    rc = realized_components[comp_idx]
    x_offset = rc["spec"].x_offset
    if rc["spec"].placed_right_of is not None:
        x_offset += _get_absolute_x_offset(realized_components, rc["spec"].placed_right_of)
    return x_offset


def _resolve_pin(component_data, pole_idx, is_input):
    """
    Resolve the internal port/pin ID for a component based on pole index and side.

    This function uses several heuristics to determine the correct port ID:

    1. Terminals (kind="terminal"):
       - Always use fixed port IDs based on pole index: (pole * 2) + (1 for input, 2 for output).
       - Examples: Pole 0 -> In="1", Out="2". Pole 1 -> In="3", Out="4".

    2. Symbols (kind="symbol") with explicit 'pins' list:
       - If 'pins' length is exactly (poles * 2): Assumes interleaved In/Out pairs.
           - Pole 0 -> In=pins[0], Out=pins[1]
           - Pole 1 -> In=pins[2], Out=pins[3]
       - Otherwise: Assumes 'pins' maps directly to poles, regardless of input/output (Direct Indexing).
           - Pole 0 -> pins[0]
           - Pole 1 -> pins[1]
           - This is used for components with named ports like ["L", "N", "PE"].

    3. Symbols without explicit 'pins' (Fallback):
       - Generates numeric IDs assuming 1,2 pairs:
           - Pole 0 -> In="1", Out="2"
           - Pole 1 -> In="3", Out="4"
    """
    spec = component_data["spec"]

    # CASE 1: Terminals
    # Terminals have fixed port IDs regardless of custom pin labels.
    # For a 3-pole terminal: ports "1", "2", "3", "4", "5", "6"
    # Each pole has 2 ports: input (odd) and output (even)
    # Pole 0: ports "1" (input), "2" (output)
    # Pole 1: ports "3" (input), "4" (output)
    # Pole 2: ports "5" (input), "6" (output)
    if spec.kind == "terminal":
        # Calculate port ID based on pole index and side
        # Formula: (pole_idx * 2) + 1 + (0 if input else 1)
        # Simplified: (pole_idx * 2) + (1 if input else 2)
        port_num = (pole_idx * 2) + (1 if is_input else 2)
        return str(port_num)

    # CASE 2: Symbols
    # Use explicit pins if provided (Mapping label to Port ID)
    if component_data["pins"]:
        # Logic: If provided pins list is large enough to cover distinct In/Out pins per pole
        # e.g. ["A1", "A2"] for 1 pole -> In=A1, Out=A2
        # e.g. ["1", "2", "3", "4"] for 2 pole -> In1=1, Out1=2, In2=3, Out2=4
        if len(component_data["pins"]) == spec.poles * 2:
            idx = (pole_idx * 2) + (0 if is_input else 1)
            if idx < len(component_data["pins"]):
                return component_data["pins"][idx]

        # For symbols with custom named ports (e.g. PSU with ["L", "N", "PE", "24V", "GND"])
        # Or short pins list - use pole_idx directly
        if pole_idx < len(component_data["pins"]):
            return component_data["pins"][pole_idx]

    # Fallback/Heuristic for Symbols without explicit pins
    # Assumes standard 1/2, 3/4 pairing port naming
    base_idx = pole_idx * 2
    offset = 0 if is_input else 1
    return str(base_idx + offset + 1)


def _resolve_registry_pin(component_data, pole_idx):
    """
    Resolve the physical pin number (label) for the registry.

    For Terminals: Returns the assigned terminal number (e.g. "42"), not the internal port ID.
    For Symbols: Returns the pin label (e.g. "A1"), ensuring consistency with _resolve_pin.
    """
    spec = component_data["spec"]

    # CASE 1: Terminals
    if spec.kind == "terminal":
        # Usually 1 pin label per pole (the terminal number)
        # component_data["pins"] should contain these labels.
        if component_data["pins"] and pole_idx < len(component_data["pins"]):
            return component_data["pins"][pole_idx]

        # Fallback: if no explicit pins provided, maybe we rely on a default counter?
        # But here we just want a logical ID.
        # For a 1-pole terminal without explicit pins, we might assume it is "1", "2"...
        # relative to the start of the block?
        # Actually, standard behavior without pins is undefined for registry if we want accurate numbering.
        # But let's fallback to returning a 1-based index based on pole.
        return str(pole_idx + 1)

    # CASE 2: Symbols
    # For symbols, the "Pin" in registry is usually the specific port label (e.g. "A1").
    # Note: Registry doesn't strictly care about Input/Output distinction in the *name* of the pin,
    # it cares about the *label* of the pin we connect to.

    # We must determine which pin (Input or Output side) we are talking about.
    # _resolve_registry_pin is ambiguous if we don't know the side.
    # BUT, actually register_connection takes `terminal_pin` and `component_pin`.
    # For Terminals, `terminal_pin` is the Slice ID ("5"). 'side' handles Top/Bottom.
    # For Components, `component_pin` IS the port label ("A1").

    # So we can't implement this universally without knowing 'is_input'.
    # But wait, the problematic case is ONLY Terminals.
    # For Symbols, `_resolve_pin` logic (returning "A1" or "A2") is exactly what we want.

    return None  # Should use _resolve_pin for symbols
