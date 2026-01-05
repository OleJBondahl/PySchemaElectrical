from typing import Dict, Optional
from ..core import Point, Vector, Port, Symbol, Style
from ..parts import terminal_circle, standard_text, create_pin_labels, three_pole_factory
from ..primitives import Text

def terminal(label: str = "", pins: tuple = ()) -> Symbol:
    """IEC 60617 Terminal symbol."""
    
    # Center at (0,0)
    c = terminal_circle(Point(0,0))
    
    elements = [c]
    if label:
        elements.append(standard_text(label, Point(0, 0)))
    
    # Ports
    ports = {
        "1": Port("1", Point(0, 0), Vector(0, -1)),
        "2": Port("2", Point(0, 0), Vector(0, 1))
    }
    
    if pins:
        # User Requirement: "only have a pin number at the bottom"
        # We assume the first pin in the tuple is the terminal number.
        # We attach it to Port "2" (Bottom/Down).
        
        # We use a temporary dict to force the function to label only Port "2"
        # and we pass only the first pin label.
        elements.extend(create_pin_labels(
            ports={"2": ports["2"]}, 
            pins=(pins[0],)
        ))

    return Symbol(elements=elements, ports=ports, label=label)

def three_pole_terminal(label: str = "", pins: tuple = ("1", "2", "3", "4", "5", "6")) -> Symbol:
    """Three pole terminal block."""
    return three_pole_factory(terminal, label, pins)
