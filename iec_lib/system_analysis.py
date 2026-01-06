from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass
import csv
from .core import Element, Symbol, Point
from .primitives import Line
from .library.terminals import Terminal, TerminalBlock

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

def trace_connection(
    node: ConnectionNode, 
    graph: Dict[Tuple[float, float], ConnectionNode], 
    visited_lines: Set[int],
    start_symbol: Symbol,
    direction_filter: Optional[Any] = None # Vector
) -> Tuple[Optional[Symbol], Optional[str]]:
    
    # Check if this node has ports from other symbols
    for sym, pid in node.connected_ports:
        if sym != start_symbol:
            return sym, pid
            
    # Traverse lines
    for line in node.connected_lines:
        line_id = id(line)
        if line_id in visited_lines:
            continue
        
        # Determine line vector from node
        p_node = node.point
        # Identify other end
        if _point_key(line.start) == _point_key(p_node):
            p_other = line.end
        else:
            p_other = line.start
            
        # Check direction filter
        if direction_filter:
             dx = p_other.x - p_node.x
             dy = p_other.y - p_node.y
             # Dot product
             dot = dx * direction_filter.dx + dy * direction_filter.dy
             # If dot product is <= 0 (orthogonal or opposite), skip
             # We want lines going "out" in the direction of the port
             if dot <= 0.001:
                 continue

        visited_lines.add(line_id)
        
        next_node_key = _point_key(p_other)
        
        if next_node_key in graph:
            # Recursive call - clear direction filter for subsequent steps, usually we just follow the line
            res = trace_connection(graph[next_node_key], graph, visited_lines, start_symbol, None)
            if res[0]:
                return res
                
    return None, None

def export_terminals_to_csv(elements: List[Element], filename: str):
    """
    Export all terminals in the system to a CSV file.
    
    Format:
    component from, pin from, terminal tag, terminal pin, component to, pin to
    
    From side is typically the TOP port (Input).
    To side is typically the BOTTOM port (Output).
    """
    graph = build_connectivity_graph(elements)
    
    rows = []
    
    # Identify terminals
    terminals = [e for e in elements if isinstance(e, (Terminal, TerminalBlock))]
    
    # Sort Terminals by label
    terminals.sort(key=lambda t: t.label if t.label else "")
    
    for term in terminals:
        # Determine channels (pin number -> port pairs)
        channels = []
        
        if isinstance(term, Terminal):
            # Single terminal. Ports "1" (Up) and "2" (Down).
            # Pin number is term.terminal_number
            channels.append({
                "pin": term.terminal_number or "",
                "from_port": "1",
                "to_port": "2"
            })
            
        elif isinstance(term, TerminalBlock):
            # Iterate through channel_map
            # channel_map: Dict[Tuple[str, str], str] (Up, Down) -> Pin
            if term.channel_map:
                for (up_p, down_p), pin_num in term.channel_map.items():
                    channels.append({
                        "pin": pin_num or "",
                        "from_port": up_p,
                        "to_port": down_p
                    })

        for ch in channels:
            pin = ch["pin"]
            from_port_id = ch["from_port"] # Up
            to_port_id = ch["to_port"]     # Down
            
            # Trace From (Up)
            comp_from, pin_from = None, None
            if from_port_id in term.ports:
                port = term.ports[from_port_id]
                p_pos = port.position
                node = graph.get(_point_key(p_pos))
                if node:
                    # Use port direction to filter initial line
                    comp_from, pin_from = trace_connection(node, graph, set(), term, port.direction)
            
            # Trace To (Down)
            comp_to, pin_to = None, None
            if to_port_id in term.ports:
                port = term.ports[to_port_id]
                p_pos = port.position
                node = graph.get(_point_key(p_pos))
                if node:
                    comp_to, pin_to = trace_connection(node, graph, set(), term, port.direction)
            
            # Format row
            # component from, pin from, terminal tag, terminal pin, component to, pin to
            row = [
                comp_from.label if comp_from and comp_from.label else "",
                pin_from if pin_from else "",
                term.label if term.label else "",
                pin,
                comp_to.label if comp_to and comp_to.label else "",
                pin_to if pin_to else ""
            ]
            rows.append(row)
            
    # Write CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Component From", "Pin From", "Terminal Tag", "Terminal Pin", "Component To", "Pin To"])
        writer.writerows(rows)
