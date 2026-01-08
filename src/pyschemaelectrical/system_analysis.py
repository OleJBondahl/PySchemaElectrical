from typing import List, Dict, Tuple, Optional, Any, Set, Iterator
from dataclasses import dataclass
import csv
from functools import reduce
from .core import Element, Symbol, Point
from .primitives import Line
from .symbols.terminals import Terminal, TerminalBlock

# Tolerance for connection (should match layout.py)
TOLERANCE = 0.1

def _point_key(p: Point) -> Tuple[float, float]:
    # Round to 1 decimal place to match tolerance
    return (round(p.x, 1), round(p.y, 1))

@dataclass
class ConnectionNode:
    point: Point
    connected_lines: List[Line]
    connected_ports: List[Tuple[Symbol, str]] # Symbol, PortID

def build_connectivity_graph(elements: List[Element]) -> Dict[Tuple[float, float], ConnectionNode]:
    nodes: Dict[Tuple[float, float], ConnectionNode] = {}
    
    def get_node(p: Point) -> ConnectionNode:
        k = _point_key(p)
        if k not in nodes:
            nodes[k] = ConnectionNode(p, [], [])
        return nodes[k]

    for el in elements:
        if isinstance(el, Line):
            n1 = get_node(el.start)
            n2 = get_node(el.end)
            n1.connected_lines.append(el)
            n2.connected_lines.append(el)
        elif isinstance(el, Symbol):
            for pid, port in el.ports.items():
                node = get_node(port.position)
                node.connected_ports.append((el, pid))
        
    return nodes

def _find_connected_symbol(node: ConnectionNode, start_symbol: Symbol) -> Optional[Tuple[Symbol, str]]:
    """Check if this node has ports from other symbols."""
    for sym, pid in node.connected_ports:
        if sym != start_symbol:
            return sym, pid
    return None

def _is_valid_direction(p_node: Point, p_other: Point, direction_filter: Optional[Any]) -> bool:
    """Check if the line direction matches the filter."""
    if not direction_filter:
        return True
    
    dx = p_other.x - p_node.x
    dy = p_other.y - p_node.y
    # Dot product
    dot = dx * direction_filter.dx + dy * direction_filter.dy
    # If dot product is <= 0 (orthogonal or opposite), skip
    # We want lines going "out" in the direction of the port
    return dot > 0.001

def trace_connection(
    node: ConnectionNode, 
    graph: Dict[Tuple[float, float], ConnectionNode], 
    visited_lines: Set[int],
    start_symbol: Symbol,
    direction_filter: Optional[Any] = None # Vector
) -> Tuple[Optional[Symbol], Optional[str]]:
    
    # Check if this node has ports from other symbols
    found_symbol = _find_connected_symbol(node, start_symbol)
    if found_symbol:
        return found_symbol

    # Traverse lines
    for line in node.connected_lines:
        if id(line) in visited_lines:
            continue
        
        p_node = node.point
        p_other = line.end if _point_key(line.start) == _point_key(p_node) else line.start
            
        if not _is_valid_direction(p_node, p_other, direction_filter):
            continue

        visited_lines.add(id(line))
        next_node_key = _point_key(p_other)
        
        if next_node_key in graph:
            # Recursive call - clear direction filter for subsequent steps
            res = trace_connection(graph[next_node_key], graph, visited_lines, start_symbol, None)
            if res[0]:
                return res
                
    return None, None

def _get_terminal_channels(term: Element) -> List[Dict[str, str]]:
    """Extract channels (pin, from_port, to_port) from a terminal element."""
    channels = []
    if isinstance(term, Terminal):
        channels.append({
            "pin": term.terminal_number or "",
            "from_port": "1",
            "to_port": "2"
        })
    elif isinstance(term, TerminalBlock) and term.channel_map:
        for (up_p, down_p), pin_num in term.channel_map.items():
            channels.append({
                "pin": pin_num or "",
                "from_port": up_p,
                "to_port": down_p
            })
    return channels

def _trace_port_connection(
    term: Symbol, 
    port_id: str, 
    graph: Dict[Tuple[float, float], ConnectionNode]
) -> Tuple[str, str]:
    """Trace a connection from a specific port of a terminal."""
    if port_id not in term.ports:
        return "", ""
        
    port = term.ports[port_id]
    node = graph.get(_point_key(port.position))
    
    if node:
        comp, pin = trace_connection(node, graph, set(), term, port.direction)
        return (comp.label if comp and comp.label else "", pin if pin else "")
        
    return "", ""

def _create_terminal_row(term: Symbol, channel: Dict[str, str], graph: Dict) -> List[str]:
    """Create a CSV row for a single terminal channel."""
    comp_from, pin_from = _trace_port_connection(term, channel["from_port"], graph)
    comp_to, pin_to = _trace_port_connection(term, channel["to_port"], graph)
    
    return [
        comp_from,
        pin_from,
        term.label if term.label else "",
        channel["pin"],
        comp_to,
        pin_to
    ]

def export_terminals_to_csv(elements: List[Element], filename: str):
    """
    Export all terminals in the system to a CSV file.
    
    Format:
    component from, pin from, terminal tag, terminal pin, component to, pin to
    
    From side is typically the TOP port (Input).
    To side is typically the BOTTOM port (Output).
    """
    graph = build_connectivity_graph(elements)
    
    terminals = [e for e in elements if isinstance(e, (Terminal, TerminalBlock))]
    terminals.sort(key=lambda t: t.label if t.label else "")
    
    rows = []
    for term in terminals:
        channels = _get_terminal_channels(term)
        for ch in channels:
            rows.append(_create_terminal_row(term, ch, graph))
            
    # Write CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Component From", "Pin From", "Terminal Tag", "Terminal Pin", "Component To", "Pin To"])
        writer.writerows(rows)
