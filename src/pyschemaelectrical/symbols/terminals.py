from dataclasses import dataclass, replace
from typing import Dict, Optional, List, Tuple
from ..core import Point, Vector, Port, Symbol, Element
from ..parts import terminal_circle, standard_text, create_pin_labels
from ..constants import DEFAULT_POLE_SPACING
from ..transform import translate

"""
IEC 60617 Terminal Symbols.
"""

@dataclass(frozen=True)
class Terminal(Symbol):
    """
    Specific symbol type for Terminals.
    Distinct from generic Symbols to allow for specialized system-level processing (e.g., CSV export).
    
    Attributes:
        terminal_number (Optional[str]): The specifically assigned terminal number.
    """
    terminal_number: Optional[str] = None

@dataclass(frozen=True)
class TerminalBlock(Symbol):
    """
    Symbol representing a block of terminals (e.g. 3-pole).
    Contains mapping of ports to terminal numbers.
    
    Attributes:
        channel_map (Dict[Tuple[str, str], str]): Map of (up_port_id, down_port_id) -> terminal_number.
    """
    # Map of (up_port_id, down_port_id) -> terminal_number
    channel_map: Optional[Dict[Tuple[str, str], str]] = None

def terminal(label: str = "", pins: tuple = ()) -> Terminal:
    """
    Create an IEC 60617 Terminal symbol.
    
    Symbol Layout:
       O
       
    Args:
        label (str): The tag of the terminal strip (e.g. "X1").
        pins (tuple): Tuple of pin numbers. Only the first one is used as the terminal number.
                      It is displayed at the bottom port.
                      
    Returns:
        Terminal: The terminal symbol.
    """
    
    # Center at (0,0)
    c = terminal_circle(Point(0,0))
    
    elements: List[Element] = [c]
    if label:
        elements.append(standard_text(label, Point(0, 0)))
    
    # Port 1: Up (Input/From)
    # Port 2: Down (Output/To)
    ports = {
        "1": Port("1", Point(0, 0), Vector(0, -1)),
        "2": Port("2", Point(0, 0), Vector(0, 1))
    }
    
    term_num = None
    if pins:
        # User Requirement: "only have a pin number at the bottom"
        # We take the first pin as the terminal number.
        term_num = pins[0]
        
        # We attach it to Port "2" (Bottom/Down).
        # We use a temporary dict to force the function to label only Port "2"
        elements.extend(create_pin_labels(
            ports={"2": ports["2"]}, 
            pins=(term_num,)
        ))

    return Terminal(elements=elements, ports=ports, label=label, terminal_number=term_num)

def three_pole_terminal(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> TerminalBlock:
    """
    Create a 3-pole terminal block.
    
    Args:
        label (str): The tag of the terminal strip.
        pins (tuple): A tuple of 6 pin numbers. 
                      Since terminals take 2 pins but use 1, this needs careful mapping.
                      Current logic uses pairs: (pin[0], pin[1]) -> pin[0] is term num?
                      Wait, logic in 'terminal' uses pin[0].
                      'three_pole_terminal' calls 'terminal' with pairs.
                      So for pins=("1","2", "3","4", "5","6"),
                      Pole 1 gets ("1","2") -> Term num "1".
                      Pole 2 gets ("3","4") -> Term num "3".
                      Pole 3 gets ("5","6") -> Term num "5".
                      
    Returns:
        TerminalBlock: The 3-pole terminal block.
    """
    
    # Logic similar to three_pole_factory but specific for TerminalBlock construction
    
    if len(pins) != 6:
        # If pins tuple is incomplete, we could pad it or error. 
        # Using slice/pad for safety if needed, but assuming 6 as per signature default
        pass
    
    # Create poles
    # Pole 1
    p1 = terminal(label=label, pins=(pins[0], pins[1]))
    # Pole 2
    p2 = terminal(label="", pins=(pins[2], pins[3]))
    p2 = translate(p2, DEFAULT_POLE_SPACING, 0)
    # Pole 3
    p3 = terminal(label="", pins=(pins[4], pins[5]))
    p3 = translate(p3, DEFAULT_POLE_SPACING * 2, 0)
    
    all_elements = p1.elements + p2.elements + p3.elements
    
    new_ports = {}
    channel_map = {}
    
    # Remap ports.
    # Note: Terminal returns ports "1" and "2".
    # Pole 1: 1, 2 -> 1, 2
    if "1" in p1.ports: new_ports["1"] = replace(p1.ports["1"], id="1")
    if "2" in p1.ports: new_ports["2"] = replace(p1.ports["2"], id="2")
    channel_map[("1", "2")] = p1.terminal_number

    # Pole 2: 1, 2 -> 3, 4
    if "1" in p2.ports: new_ports["3"] = replace(p2.ports["1"], id="3")
    if "2" in p2.ports: new_ports["4"] = replace(p2.ports["2"], id="4")
    channel_map[("3", "4")] = p2.terminal_number

    # Pole 3: 1, 2 -> 5, 6
    if "1" in p3.ports: new_ports["5"] = replace(p3.ports["1"], id="5")
    if "2" in p3.ports: new_ports["6"] = replace(p3.ports["2"], id="6")
    channel_map[("5", "6")] = p3.terminal_number

    return TerminalBlock(elements=all_elements, ports=new_ports, label=label, channel_map=channel_map)
