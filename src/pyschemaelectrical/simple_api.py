"""
Simple API for PySchemaElectrical

This module provides a simplified, high-level interface for creating electrical schematics.
Components are automatically positioned vertically and can be easily connected and rendered.

Example:
    ```python
    from pyschemaelectrical.simple_api import Circuit, Terminal, Contact, Coil
    
    circuit = Circuit()
    circuit.add(Terminal("X1"))
    circuit.add(Contact.NO("S1"))
    circuit.add(Coil("K1"))
    circuit.render("output.svg")
    ```
"""

from typing import List, Optional, Tuple
from .core import Symbol
from .symbols.terminals import terminal, three_pole_terminal
from .symbols.contacts import normally_open, normally_closed, spdt_contact
from .symbols.coils import coil
from .symbols.assemblies import emergency_stop_assembly, contactor
from .symbols.breakers import three_pole_circuit_breaker
from .symbols.protection import three_pole_thermal_overload
from .transform import translate
from .layout import auto_connect
from .renderer import render_to_svg
from .constants import GRID_SIZE


class Circuit:
    """
    A simplified circuit builder that automatically handles component layout and rendering.
    
    Components are positioned vertically with automatic spacing. The circuit maintains
    state internally and provides a simple add() and render() interface.
    
    Attributes:
        start_x (float): Starting x position for the circuit
        start_y (float): Starting y position for the circuit
        spacing (float): Vertical spacing between components (in mm)
    """
    
    def __init__(self, start_x: float = 50, start_y: float = 50, spacing: float = 10 * GRID_SIZE):
        """
        Initialize a new circuit.
        
        Args:
            start_x: X coordinate for the circuit (default: 50mm)
            start_y: Y coordinate for the circuit (default: 50mm)
            spacing: Vertical spacing between components (default: 50mm)
        """
        self.start_x = start_x
        self.start_y = start_y
        self.spacing = spacing
        self._current_y = start_y
        self._symbols: List[Symbol] = []
        self._elements: List = []
    
    def add(self, symbol: Symbol) -> 'Circuit':
        """
        Add a component to the circuit at the current position.
        
        The component is automatically positioned and vertically spaced from the previous component.
        
        Args:
            symbol: The symbol to add
            
        Returns:
            self for method chaining
        """
        # Translate symbol to current position
        positioned = translate(symbol, self.start_x, self._current_y)
        
        # Auto-connect to previous symbol if one exists
        if self._symbols:
            self._elements.extend(auto_connect(self._symbols[-1], positioned))
        
        self._symbols.append(positioned)
        self._current_y += self.spacing
        
        return self
    
    def render(self, filename: str, width: str = "210mm", height: str = "297mm") -> None:
        """
        Render the circuit to an SVG file.
        
        Args:
            filename: Output SVG filename
            width: SVG canvas width (default: A4 width)
            height: SVG canvas height (default: A4 height)
        """
        # Collect all symbols as elements
        all_elements = self._symbols + self._elements
        render_to_svg(all_elements, filename, width=width, height=height)
    
    def get_elements(self) -> List:
        """
        Get all elements (symbols + connecting wires) in the circuit.
        
        Returns:
            List of all elements
        """
        return self._symbols + self._elements


# Component wrapper classes/functions
class Terminal:
    """Factory for terminal symbols."""
    
    @staticmethod
    def single(tag: str, pins: Tuple[str, ...] = ("1",)) -> Symbol:
        """
        Create a single-pole terminal.
        
        Args:
            tag: Terminal designation (e.g., "X1")
            pins: Pin numbers (default: ("1",))
            
        Returns:
            Terminal symbol
        """
        return terminal(tag, pins)
    
    @staticmethod
    def three_pole(tag: str, pins: Tuple[str, ...] = ("1", "2", "3", "4", "5", "6")) -> Symbol:
        """
        Create a three-pole terminal block.
        
        Args:
            tag: Terminal designation (e.g., "X1")
            pins: Pin numbers for all three poles (default: ("1", "2", "3", "4", "5", "6"))
            
        Returns:
            Three-pole terminal symbol
        """
        return three_pole_terminal(tag, pins)
    
    def __new__(cls, tag: str, pins: Tuple[str, ...] = ("1",)) -> Symbol:
        """Default constructor creates a single-pole terminal."""
        return cls.single(tag, pins)


class Contact:
    """Factory for contact symbols."""
    
    @staticmethod
    def NO(tag: str, pins: Tuple[str, ...] = ("13", "14")) -> Symbol:
        """
        Create a Normally Open (NO) contact.
        
        Args:
            tag: Component tag (e.g., "S1")
            pins: Pin numbers (default: ("13", "14"))
            
        Returns:
            NO contact symbol
        """
        return normally_open(tag, pins)
    
    @staticmethod
    def NC(tag: str, pins: Tuple[str, ...] = ("21", "22")) -> Symbol:
        """
        Create a Normally Closed (NC) contact.
        
        Args:
            tag: Component tag (e.g., "S1")
            pins: Pin numbers (default: ("21", "22"))
            
        Returns:
            NC contact symbol
        """
        return normally_closed(tag, pins)
    
    @staticmethod
    def SPDT(tag: str, pins: Tuple[str, ...] = ("11", "12", "14")) -> Symbol:
        """
        Create a Single Pole Double Throw (SPDT) contact.
        
        Args:
            tag: Component tag (e.g., "S1")
            pins: Pin numbers for Common, NC, NO (default: ("11", "12", "14"))
            
        Returns:
            SPDT contact symbol
        """
        return spdt_contact(tag, pins)
    
    def __new__(cls, contact_type: str, tag: str, pins: Optional[Tuple[str, ...]] = None) -> Symbol:
        """
        Create a contact with specified type.
        
        Args:
            contact_type: "NO", "NC", or "SPDT"
            tag: Component tag
            pins: Pin numbers (uses defaults if None)
            
        Returns:
            Contact symbol
        """
        contact_type = contact_type.upper()
        if contact_type == "NO":
            return cls.NO(tag, pins or ("13", "14"))
        elif contact_type == "NC":
            return cls.NC(tag, pins or ("21", "22"))
        elif contact_type == "SPDT":
            return cls.SPDT(tag, pins or ("11", "12", "14"))
        else:
            raise ValueError(f"Invalid contact type: {contact_type}. Must be NO, NC, or SPDT")


class Coil:
    """Factory for coil symbols."""
    
    def __new__(cls, tag: str, pins: Tuple[str, ...] = ("A1", "A2")) -> Symbol:
        """
        Create a coil symbol.
        
        Args:
            tag: Component tag (e.g., "K1")
            pins: Pin numbers (default: ("A1", "A2"))
            
        Returns:
            Coil symbol
        """
        return coil(tag, pins)


class Breaker:
    """Factory for circuit breaker symbols."""
    
    @staticmethod
    def three_pole(tag: str, pins: Tuple[str, ...] = ("1", "2", "3", "4", "5", "6")) -> Symbol:
        """
        Create a three-pole circuit breaker.
        
        Args:
            tag: Component tag (e.g., "Q1")
            pins: Pin numbers for all three poles (default: ("1", "2", "3", "4", "5", "6"))
            
        Returns:
            Three-pole breaker symbol
        """
        return three_pole_circuit_breaker(tag, pins)
    
    def __new__(cls, tag: str, pins: Tuple[str, ...] = ("1", "2", "3", "4", "5", "6")) -> Symbol:
        """Default constructor creates a three-pole breaker."""
        return cls.three_pole(tag, pins)


class Protection:
    """Factory for protection device symbols."""
    
    @staticmethod
    def thermal_overload(tag: str, pins: Tuple[str, ...] = ("1", "2", "3", "4", "5", "6")) -> Symbol:
        """
        Create a three-pole thermal overload relay.
        
        Args:
            tag: Component tag (e.g., "F1")
            pins: Pin numbers for all three poles (default: ("1", "2", "3", "4", "5", "6"))
            
        Returns:
            Thermal overload symbol
        """
        return three_pole_thermal_overload(tag, pins)
    
    def __new__(cls, tag: str, pins: Tuple[str, ...] = ("1", "2", "3", "4", "5", "6")) -> Symbol:
        """Default constructor creates a thermal overload relay."""
        return cls.thermal_overload(tag, pins)


class Assembly:
    """Factory for assembly symbols (composite components)."""
    
    @staticmethod
    def emergency_stop(tag: str) -> Symbol:
        """
        Create an emergency stop assembly (button + NC contact).
        
        Args:
            tag: Component tag (e.g., "S0")
            
        Returns:
            Emergency stop assembly symbol
        """
        return emergency_stop_assembly(tag)
    
    @staticmethod
    def contactor(tag: str, poles: int = 3) -> Symbol:
        """
        Create a contactor assembly.
        
        Args:
            tag: Component tag (e.g., "K1")
            poles: Number of poles (default: 3)
            
        Returns:
            Contactor assembly symbol
        """
        return contactor(tag, poles)


# Convenience exports
__all__ = [
    'Circuit',
    'Terminal',
    'Contact',
    'Coil',
    'Breaker',
    'Protection',
    'Assembly',
]
