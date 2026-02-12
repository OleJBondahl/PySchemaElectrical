"""
Utility functions for circuit generation and state management.
Contains helpers for tag counters and contact pin management.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pyschemaelectrical.model.state import GenerationState


def set_tag_counter(
    state: Union[Dict[str, Any], GenerationState], prefix: str, value: int
) -> Dict[str, Any]:
    """
    Sets the counter for a specific tag prefix to a given value.
    The next call to next_tag() will return value + 1.

    Args:
        state: The autonumbering state.
        prefix: The tag prefix to set (e.g. "Q").
        value: The value to set the counter to.

    Returns:
        Updated state.
    """
    new_state = state.copy()
    new_state["tags"] = state.get("tags", {}).copy()
    new_state["tags"][prefix] = value
    return new_state


def set_terminal_counter(
    state: Union[Dict[str, Any], GenerationState], terminal_tag: str, value: int
) -> Dict[str, Any]:
    """
    Sets the pin counter for a specific terminal tag.
    The next call to next_terminal_pins() will start from value + 1.
    """
    new_state = state.copy()
    # Pyschemaelectrical likely uses 'terminal_counters' based on debug output
    new_state["terminal_counters"] = state.get("terminal_counters", {}).copy()
    new_state["terminal_counters"][terminal_tag] = value
    return new_state


def next_contact_pins(
    state: Union[Dict[str, Any], GenerationState], tag: str
) -> Tuple[Dict[str, Any], Tuple[str, str, str]]:
    """
    Get the next set of pins for a contact (SPDT/Changeover) for a given tag.
    Increments the channel counter for that tag.

    Pins are generated as: (X1, X2, X4) where X is the channel number.
    e.g. Channel 1: ("11", "12", "14")
         Channel 2: ("21", "22", "24")

    Args:
        state: The autonumbering state.
        tag: The component tag (e.g. "K1").

    Returns:
        (updated_state, (pin_com, pin_nc, pin_no))
    """
    # Use a new 'contact_channels' dict in state to track usage
    channel_map = state.get("contact_channels", {})
    current_channel = channel_map.get(tag, 0) + 1

    # Generate pins
    pins = (f"{current_channel}1", f"{current_channel}2", f"{current_channel}4")

    # Update state
    new_state = state.copy()
    new_channel_map = channel_map.copy()
    new_channel_map[tag] = current_channel
    new_state["contact_channels"] = new_channel_map

    return new_state, pins


def apply_start_indices(
    state: Union[Dict[str, Any], GenerationState],
    start_indices: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Apply start indices to tag counters.

    Args:
        state: Current autonumbering state
        start_indices: Dict of {prefix: start_value}

    Returns:
        Updated state
    """
    if not start_indices:
        return state
    for prefix, value in start_indices.items():
        state = set_tag_counter(state, prefix, value)
    return state


def create_fixed_tag_generator(tag: str) -> Callable[[Any], Tuple[Any, str]]:
    """
    Create a generator that always returns a fixed tag.

    Args:
        tag: The fixed tag to return (e.g., "K2", "K3")

    Returns:
        A lambda function that returns (state, tag)
    """
    return lambda s: (s, tag)


def merge_terminals(target: List, source: List) -> None:
    """
    Merge terminal lists (mutates target).

    Args:
        target: The target terminal list
        source: The source terminal list to append
    """
    target.extend(source)
