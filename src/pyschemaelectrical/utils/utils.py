"""
Utility functions for circuit generation and state management.
Contains helpers for tag counters and contact pin management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyschemaelectrical.model.state import GenerationState


def set_tag_counter(
    state: dict[str, Any] | GenerationState, prefix: str, value: int
) -> dict[str, Any]:
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
    state: dict[str, Any] | GenerationState, terminal_tag: str, value: int
) -> dict[str, Any]:
    """
    Sets the pin counter for a specific terminal tag.
    The next call to next_terminal_pins() will start from value + 1.
    """
    new_state = state.copy()
    # State key for terminal pin counters
    new_state["terminal_counters"] = state.get("terminal_counters", {}).copy()
    new_state["terminal_counters"][terminal_tag] = value
    return new_state


def next_contact_pins(
    state: dict[str, Any] | GenerationState, tag: str
) -> tuple[dict[str, Any], tuple[str, str, str]]:
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


def get_terminal_counter(
    state: dict[str, Any] | GenerationState, terminal_tag: str
) -> int:
    """
    Get the current pin counter for a terminal (0 if unused).

    Args:
        state: The autonumbering state.
        terminal_tag: The terminal tag to query.

    Returns:
        Current pin counter value for this terminal.
    """
    return state.get("terminal_counters", {}).get(str(terminal_tag), 0)


def apply_start_indices(
    state: dict[str, Any] | GenerationState,
    start_indices: dict[str, int] | None = None,
) -> dict[str, Any]:
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


def merge_terminals(target: list, source: list) -> list:
    """
    Merge two terminal lists, returning a new combined list.

    Args:
        target: The first terminal list
        source: The second terminal list to append

    Returns:
        A new list containing all items from both lists.
    """
    return target + source
