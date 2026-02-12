import csv
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class Connection:
    """
    Represents a connection between a terminal pin and a component pin.
    """
    terminal_tag: str
    terminal_pin: str
    component_tag: str
    component_pin: str
    side: str  # 'top' or 'bottom'

@dataclass(frozen=True)
class TerminalRegistry:
    """
    Immutable registry for terminal connections.
    """
    connections: Tuple[Connection, ...] = field(default_factory=tuple)

    def add_connection(self, terminal_tag: str, terminal_pin: str,
                       component_tag: str, component_pin: str, side: str) -> 'TerminalRegistry':
        """
        Returns a new TerminalRegistry with the added connection.
        """
        new_conn = Connection(terminal_tag, terminal_pin, component_tag, component_pin, side)
        return TerminalRegistry(self.connections + (new_conn,))

    def add_connections(self, conns: List[Connection]) -> 'TerminalRegistry':
        return TerminalRegistry(self.connections + tuple(conns))

def get_registry(state: Dict[str, Any]) -> TerminalRegistry:
    """Retreives or creates the TerminalRegistry from the state."""
    return state.get('terminal_registry', TerminalRegistry())

def update_registry(state: Dict[str, Any], registry: TerminalRegistry) -> Dict[str, Any]:
    """Updates the state with the new registry."""
    new_state = state.copy()
    new_state['terminal_registry'] = registry
    return new_state

def register_connection(state: Dict[str, Any],
                        terminal_tag: str, terminal_pin: str,
                        component_tag: str, component_pin: str,
                        side: str = 'bottom') -> Dict[str, Any]:
    """
    Functional helper to register a connection in the state.
    """
    reg = get_registry(state)
    new_reg = reg.add_connection(terminal_tag, terminal_pin, component_tag, component_pin, side)
    return update_registry(state, new_reg)


def register_3phase_connections(
    state: Dict[str, Any],
    terminal_tag: str,
    terminal_pins: Tuple[str, ...],
    component_tag: str,
    component_pins: Tuple[str, ...],
    side: str = 'bottom'
) -> Dict[str, Any]:
    """
    Register all 3 phase connections between a terminal and a component.

    This is a convenience function for 3-phase circuits that need to register
    all L1, L2, L3 connections at once.

    Args:
        state: The current autonumbering state
        terminal_tag: The terminal block tag (e.g., "X001")
        terminal_pins: Sequential terminal pins (e.g., ("1", "2", "3"))
        component_tag: The component tag (e.g., "F1")
        component_pins: Component pins for each phase (e.g., ("1", "3", "5"))
        side: Connection side ('top' or 'bottom')

    Returns:
        Updated state with all connections registered.

    Example:
        >>> # Register breaker F1 to input terminal X001
        >>> state = register_3phase_connections(
        ...     state, "X001", ("1", "2", "3"),
        ...     "F1", ("1", "3", "5"), side='bottom'
        ... )
    """
    for i in range(min(3, len(terminal_pins), len(component_pins))):
        state = register_connection(
            state, terminal_tag, terminal_pins[i],
            component_tag, component_pins[i], side
        )
    return state


def register_3phase_input(
    state: Dict[str, Any],
    terminal_tag: str,
    terminal_pins: Tuple[str, ...],
    component_tag: str,
    component_pins: Tuple[str, ...] = ("1", "3", "5"),
) -> Dict[str, Any]:
    """
    Register 3-phase input connections (terminal to component input pins).

    Standard 3-phase component input pins are 1, 3, 5 (L1, L2, L3).

    Args:
        state: The current autonumbering state
        terminal_tag: The terminal block tag (e.g., "X001")
        terminal_pins: Sequential terminal pins from next_terminal_pins
        component_tag: The component tag (e.g., "F1")
        component_pins: Component input pins (default: ("1", "3", "5"))

    Returns:
        Updated state with all connections registered.
    """
    return register_3phase_connections(
        state, terminal_tag, terminal_pins,
        component_tag, component_pins, side='bottom'
    )


def register_3phase_output(
    state: Dict[str, Any],
    terminal_tag: str,
    terminal_pins: Tuple[str, ...],
    component_tag: str,
    component_pins: Tuple[str, ...] = ("2", "4", "6"),
) -> Dict[str, Any]:
    """
    Register 3-phase output connections (component output pins to terminal).

    Standard 3-phase component output pins are 2, 4, 6 (T1, T2, T3).

    Args:
        state: The current autonumbering state
        terminal_tag: The terminal block tag (e.g., "X201")
        terminal_pins: Sequential terminal pins from next_terminal_pins
        component_tag: The component tag (e.g., "Q1")
        component_pins: Component output pins (default: ("2", "4", "6"))

    Returns:
        Updated state with all connections registered.
    """
    return register_3phase_connections(
        state, terminal_tag, terminal_pins,
        component_tag, component_pins, side='top'
    )

def export_registry_to_csv(registry: TerminalRegistry, filepath: str):
    """
    Exports the registry to the expected CSV format.
    Refactored to group by Terminal Tag + Pin.
    """
    # Group by (Tag, Pin)
    # Result: Map[(Tag, Pin), {'top': [], 'bottom': []}]
    from collections import defaultdict
    grouped = defaultdict(lambda: {'top': [], 'bottom': []})

    for conn in registry.connections:
        key = (conn.terminal_tag, conn.terminal_pin)
        grouped[key][conn.side].append(conn)

    # Sort keys - handle mixed int/string pins by using tuple with explicit type handling
    def sort_key(k):
        t, p = k
        try:
            return (t, 0, int(p), str(p))  # Numeric pins sort first
        except (ValueError, TypeError):
            return (t, 1, 0, str(p))  # Non-numeric pins sort after numeric

    sorted_keys = sorted(grouped.keys(), key=sort_key)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Component From", "Pin From", "Terminal Tag", "Terminal Pin", "Component To", "Pin To"])

        for t_tag, t_pin in sorted_keys:
            data = grouped[(t_tag, t_pin)]

            # Format Top side (usually "From")
            # Usually 'top' connections go to components inside the panel
            top_conns = data['top']
            from_comp = " / ".join(c.component_tag for c in top_conns)
            from_pin = " / ".join(c.component_pin for c in top_conns)

            # Format Bottom side (usually "To")
            # Usually 'bottom' connections go to field
            bot_conns = data['bottom']
            to_comp = " / ".join(c.component_tag for c in bot_conns)
            to_pin = " / ".join(c.component_pin for c in bot_conns)

            writer.writerow([from_comp, from_pin, t_tag, t_pin, to_comp, to_pin])
