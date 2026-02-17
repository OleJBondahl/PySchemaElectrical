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

from typing import Any

from pyschemaelectrical.model.state import GenerationState, create_initial_state


def create_autonumberer() -> dict[str, Any]:
    """
    Create a new autonumbering state.

    Returns:
        dict[str, Any]: Dictionary with 'tags' for component numbers and
                       'pin_counter' for sequential pin numbering.
    """
    return create_initial_state()


def get_tag_number(state: dict[str, Any] | GenerationState, prefix: str) -> int:
    """
    Get the current number for a tag prefix.

    Args:
        state: The autonumbering state dictionary.
        prefix: The tag prefix (e.g., "F", "Q", "X").

    Returns:
        int: The current number for this prefix (0 if not yet used).
    """
    return state["tags"].get(prefix, 0)


def _increment_tag(
    state: dict[str, Any] | GenerationState, prefix: str
) -> dict[str, Any]:
    """
    Increment the counter for a tag prefix and return new state.

    Args:
        state: The current autonumbering state.
        prefix: The tag prefix to increment.

    Returns:
        dict[str, Any]: New state with incremented counter.
    """
    new_state = state.copy()
    new_state["tags"] = state["tags"].copy()
    new_state["tags"][prefix] = get_tag_number(state, prefix) + 1
    return new_state


def _format_tag(prefix: str, number: int) -> str:
    """
    Format a tag with prefix and number.

    Args:
        prefix: The tag prefix (e.g., "F", "Q", "X").
        number: The tag number.

    Returns:
        str: Formatted tag (e.g., "F1", "Q2", "X3").
    """
    return f"{prefix}{number}"


def next_tag(
    state: dict[str, Any] | GenerationState, prefix: str
) -> tuple[dict[str, Any], str]:
    """
    Get the next tag for a prefix and return updated state.

    This is a convenience function that combines increment_tag and format_tag.

    Args:
        state: The current autonumbering state.
        prefix: The tag prefix.

    Returns:
        tuple[dict[str, Any], str]: Updated state and formatted tag.

    Example:
        >>> state = create_autonumberer()
        >>> state, tag1 = next_tag(state, "F")
        >>> print(tag1)  # "F1"
        >>> state, tag2 = next_tag(state, "F")
        >>> print(tag2)  # "F2"
    """
    new_state = _increment_tag(state, prefix)
    tag = _format_tag(prefix, get_tag_number(new_state, prefix))
    return new_state, tag


def get_pin_counter(state: dict[str, Any] | GenerationState) -> int:
    """
    Get the current pin counter value.

    Args:
        state: The autonumbering state dictionary.

    Returns:
        int: Current pin counter value.
    """
    return state["pin_counter"]


def next_terminal_pins(
    state: dict[str, Any] | GenerationState,
    terminal_tag: str,
    poles: int = 3,
    pin_prefixes: tuple[str, ...] | None = None,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """
    Generate sequential terminal pins for a specific terminal strip.

    When ``pin_prefixes`` are available (either passed explicitly or read
    from a :class:`Terminal` object's ``pin_prefixes`` attribute), pins are
    formatted as ``"<prefix>:<group_number>"`` and the counter advances by
    1 per allocation (group-based).  Otherwise plain sequential numbers are
    generated and the counter advances by *poles*.

    Args:
        state: The current autonumbering state.
        terminal_tag: The tag of the terminal strip (e.g. "X1", "X2").
            May be a :class:`Terminal` instance carrying ``pin_prefixes``.
        poles: Number of poles (default 3 for three-phase).
        pin_prefixes: Optional explicit prefixes that override the attribute
            on *terminal_tag*.

    Returns:
        Tuple containing updated state and pin number tuple.
    """
    prefixes = pin_prefixes or getattr(terminal_tag, "pin_prefixes", None)

    counters = state.get("terminal_counters", {})
    tag_key = str(terminal_tag)

    if prefixes and len(prefixes) >= poles:
        # Group-based: counter advances by 1 per allocation
        current_num = counters.get(tag_key, 0) + 1
        pins = tuple(f"{prefixes[i]}:{current_num}" for i in range(poles))
        new_counter_val = current_num
    else:
        # Original behaviour: counter advances by number of poles
        current_pin = counters.get(tag_key, 0) + 1
        pins = tuple(str(current_pin + i) for i in range(poles))
        new_counter_val = current_pin + poles - 1

    new_state = state.copy()
    new_counters = counters.copy()
    new_counters[tag_key] = new_counter_val
    new_state["terminal_counters"] = new_counters

    return new_state, pins


# ---------------------------------------------------------------------------
# Public aliases for private helpers
# ---------------------------------------------------------------------------

def increment_tag(
    state: dict[str, Any] | GenerationState, prefix: str
) -> dict[str, Any]:
    """Increment the counter for a tag prefix and return new state."""
    return _increment_tag(state, prefix)


def format_tag(prefix: str, number: int) -> str:
    """Format a tag with prefix and number."""
    return _format_tag(prefix, number)


# ---------------------------------------------------------------------------
# Pin-range helpers
# ---------------------------------------------------------------------------

def generate_pin_range(
    start: int, count: int, skip_odd: bool = False
) -> tuple[str, ...]:
    """Generate a sequential range of pin number strings.

    Args:
        start: First pin number in the range.
        count: How many pins to generate.
        skip_odd: If True, odd-numbered pins are replaced with "".

    Returns:
        Tuple of pin strings.
    """
    pins: list[str] = []
    for i in range(count):
        pin_num = start + i
        if skip_odd and pin_num % 2 != 0:
            pins.append("")
        else:
            pins.append(str(pin_num))
    return tuple(pins)


def auto_coil_pins() -> tuple[str, str]:
    """Return the standard IEC coil pin pair."""
    return ("A1", "A2")


def auto_contact_pins(start: int, poles: int) -> tuple[str, ...]:
    """Generate contact pins (2 pins per pole, sequential)."""
    return generate_pin_range(start, poles * 2)


def auto_terminal_pins(start: int, poles: int) -> tuple[str, ...]:
    """Generate terminal pins (2 pins per pole, sequential)."""
    return generate_pin_range(start, poles * 2)


def auto_thermal_pins(start: int, poles: int) -> tuple[str, ...]:
    """Generate thermal-overload pins (skip-odd pattern, 2 pins per pole)."""
    return generate_pin_range(start - 1, poles * 2, skip_odd=True)
