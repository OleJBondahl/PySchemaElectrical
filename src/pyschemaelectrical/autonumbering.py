"""
Autonumbering utilities for component tags and terminal pins.

This module provides functional utilities for automatically numbering components
and terminals in electrical schematics. It uses a counter-based approach that 
generates sequential numbers for tags with the same prefix letter.

Example:
    >>> numberer = create_autonumberer()
    >>> numberer = increment_tag(numberer, "F")
    >>> get_tag_number(numberer, "F")
    1
    >>> numberer = increment_tag(numberer, "F")
    >>> get_tag_number(numberer, "F")
    2
"""

from typing import Dict, Tuple, Any


def create_autonumberer() -> Dict[str, Any]:
    """
    Create a new autonumbering state.
    
    Returns:
        Dict[str, Any]: Dictionary with 'tags' for component numbers and 
                       'pin_counter' for sequential pin numbering.
    """
    return {
        'tags': {},
        'pin_counter': 0,
        'terminal_counters': {}
    }


def get_tag_number(state: Dict[str, Any], prefix: str) -> int:
    """
    Get the current number for a tag prefix.
    
    Args:
        state: The autonumbering state dictionary.
        prefix: The tag prefix (e.g., "F", "Q", "X").
        
    Returns:
        int: The current number for this prefix (0 if not yet used).
    """
    return state['tags'].get(prefix, 0)


def increment_tag(state: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Increment the counter for a tag prefix and return new state.
    
    Args:
        state: The current autonumbering state.
        prefix: The tag prefix to increment.
        
    Returns:
        Dict[str, Any]: New state with incremented counter.
    """
    new_state = state.copy()
    new_state['tags'] = state['tags'].copy()
    new_state['tags'][prefix] = get_tag_number(state, prefix) + 1
    return new_state


def format_tag(prefix: str, number: int) -> str:
    """
    Format a tag with prefix and number.
    
    Args:
        prefix: The tag prefix (e.g., "F", "Q", "X").
        number: The tag number.
        
    Returns:
        str: Formatted tag (e.g., "F1", "Q2", "X3").
    """
    return f"{prefix}{number}"


def next_tag(state: Dict[str, Any], prefix: str) -> Tuple[Dict[str, Any], str]:
    """
    Get the next tag for a prefix and return updated state.
    
    This is a convenience function that combines increment_tag and format_tag.
    
    Args:
        state: The current autonumbering state.
        prefix: The tag prefix.
        
    Returns:
        Tuple[Dict[str, Any], str]: Updated state and formatted tag.
        
    Example:
        >>> state = create_autonumberer()
        >>> state, tag1 = next_tag(state, "F")
        >>> print(tag1)  # "F1"
        >>> state, tag2 = next_tag(state, "F")
        >>> print(tag2)  # "F2"
    """
    new_state = increment_tag(state, prefix)
    tag = format_tag(prefix, get_tag_number(new_state, prefix))
    return new_state, tag


def generate_pin_range(start: int, count: int, skip_odd: bool = False) -> Tuple[str, ...]:
    """
    Generate a range of pin numbers.
    
    Args:
        start: Starting pin number.
        count: Number of pins to generate.
        skip_odd: If True, only generate even numbers (for thermal symbols).
        
    Returns:
        Tuple[str, ...]: Tuple of pin number strings.
        
    Example:
        >>> generate_pin_range(1, 6)
        ('1', '2', '3', '4', '5', '6')
        >>> generate_pin_range(1, 6, skip_odd=True)
        ('', '2', '', '4', '', '6')
    """
    if skip_odd:
        return tuple("" if i % 2 == 1 else str(i) for i in range(start, start + count))
    else:
        return tuple(str(i) for i in range(start, start + count))


def get_pin_counter(state: Dict[str, Any]) -> int:
    """
    Get the current pin counter value.
    
    Args:
        state: The autonumbering state dictionary.
        
    Returns:
        int: Current pin counter value.
    """
    return state['pin_counter']


def next_terminal_pins(
    state: Dict[str, Any], 
    terminal_tag: str,
    poles: int = 3
) -> Tuple[Dict[str, Any], Tuple[str, ...]]:
    """
    Generate sequential terminal pins for a specific terminal strip.
    
    Args:
        state: The current autonumbering state.
        terminal_tag: The tag of the terminal strip (e.g. "X1", "X2").
        poles: Number of poles (default 3 for three-phase).
        
    Returns:
        Tuple containing updated state and pin number tuple.
    """
    # Get current counter for this specific terminal tag
    # Default to 0 if not encountered yet
    counters = state.get('terminal_counters', {})
    current_pin = counters.get(terminal_tag, 0) + 1
    
    # Generate sequential pins: "1", "2", "3"...
    pins_list = []
    for i in range(poles):
        pins_list.append(str(current_pin + i))
    
    pins = tuple(pins_list)
    
    # Update state
    new_counters = counters.copy()
    new_counters[terminal_tag] = current_pin + poles - 1
    
    # Create new state dictionary (shallow copy of parent, deep copy of mutable parts we touch)
    new_state = state.copy()
    new_state['terminal_counters'] = new_counters
    
    return new_state, pins


def auto_terminal_pins(base: int = 1, poles: int = 3) -> Tuple[str, ...]:
    """
    Generate standard terminal pin numbering for multi-pole terminals.
    
    NOTE: This function generates static pin numbers starting from 'base'.
    For auto-incrementing pins across circuits, use next_terminal_pins() instead.
    
    Args:
        base: Base pin number to start from.
        poles: Number of poles (default 3 for three-phase).
        
    Returns:
        Tuple[str, ...]: Pin numbers for top and bottom connections.
        
    Example:
        >>> auto_terminal_pins(1, 3)
        ('1', '2', '3', '4', '5', '6')
    """
    return generate_pin_range(base, poles * 2)


def auto_contact_pins(base: int = 1, poles: int = 3) -> Tuple[str, ...]:
    """
    Generate standard contact pin numbering for multi-pole contacts.
    
    Args:
        base: Base pin number to start from.
        poles: Number of poles (default 3 for three-phase).
        
    Returns:
        Tuple[str, ...]: Pin numbers for input and output connections.
        
    Example:
        >>> auto_contact_pins(1, 3)
        ('1', '2', '3', '4', '5', '6')
    """
    return generate_pin_range(base, poles * 2)


def auto_thermal_pins(base: int = 2, poles: int = 3) -> Tuple[str, ...]:
    """
    Generate thermal overload pin numbering (only even numbers labeled).
    
    Thermal overload symbols typically only label the output pins.
    
    Args:
        base: Base pin number (typically 2 for output side).
        poles: Number of poles (default 3 for three-phase).
        
    Returns:
        Tuple[str, ...]: Pin numbers with odd positions empty.
        
    Example:
        >>> auto_thermal_pins(2, 3)
        ('', '2', '', '4', '', '6')
    """
    return generate_pin_range(base - 1, poles * 2, skip_odd=True)


def auto_coil_pins() -> Tuple[str, str]:
    """
    Generate standard coil pin numbering.
    
    Returns:
        Tuple[str, str]: Standard coil pins ("A1", "A2").
    """
    return ("A1", "A2")
