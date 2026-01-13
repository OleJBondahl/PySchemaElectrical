from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import csv

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
        
    # Sort keys
    def sort_key(k):
        t, p = k
        try: return (t, int(p))
        except: return (t, p)
        
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
