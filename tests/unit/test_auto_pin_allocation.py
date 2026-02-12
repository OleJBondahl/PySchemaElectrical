"""Tests for auto terminal pin allocation (Task 8A)."""

from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.utils.utils import set_terminal_counter


def test_auto_pin_sequential():
    """Adding terminals without explicit pins should auto-allocate sequential pins."""
    state = create_autonumberer()

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=80)
    builder.add_terminal("X008")
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder.add_terminal("X008")

    result = builder.build(count=3)

    # The terminal counter for X008 should have advanced
    # 3 instances, each with 2 terminals using 1 pin each = 6 pins total
    # Pins: 1, 2, 3, 4, 5, 6 (sequential across instances)
    assert result.state["terminal_counters"]["X008"] == 6


def test_auto_pin_with_seeded_start():
    """Setting terminal counter should affect where auto pins start."""
    state = create_autonumberer()
    state = set_terminal_counter(state, "X008", 5)

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=80)
    builder.add_terminal("X008")
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder.add_terminal("X008")

    result = builder.build(count=1)

    # Pins should start at 6 (counter was 5, next_terminal_pins adds 1)
    assert result.state["terminal_counters"]["X008"] == 7


def test_explicit_pins_override():
    """Explicit pins should be used instead of auto-allocation."""
    state = create_autonumberer()

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=80)
    builder.add_terminal("X008", pins=("42",))
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder.add_terminal("X008")

    result = builder.build(count=1)

    # First terminal used explicit pin "42", so counter should be at 1
    # (only the second terminal auto-allocated pin "1")
    assert result.state["terminal_counters"]["X008"] == 1


def test_auto_pin_across_builds():
    """Auto pins should continue across multiple builds using shared state."""
    state = create_autonumberer()

    # First build: allocates pins 1, 2 for X008
    builder1 = CircuitBuilder(state)
    builder1.set_layout(x=0, y=0, spacing=80)
    builder1.add_terminal("X008")
    builder1.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder1.add_terminal("X008")
    result1 = builder1.build(count=1)

    assert result1.state["terminal_counters"]["X008"] == 2

    # Second build with state from first: should continue from pin 3
    builder2 = CircuitBuilder(result1.state)
    builder2.set_layout(x=0, y=0, spacing=80)
    builder2.add_terminal("X008")
    builder2.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder2.add_terminal("X008")
    result2 = builder2.build(count=1)

    assert result2.state["terminal_counters"]["X008"] == 4


def test_mixed_auto_and_explicit():
    """Mix of auto and explicit pins should not conflict."""
    state = create_autonumberer()

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=80)
    builder.add_terminal("X008")  # auto: pin 1
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder.add_terminal("X008", pins=("99",))  # explicit: pin 99

    result = builder.build(count=1)

    # Auto-allocated only 1 pin, explicit used "99"
    assert result.state["terminal_counters"]["X008"] == 1


def test_auto_pin_different_terminals():
    """Different terminal IDs should have independent pin counters."""
    state = create_autonumberer()

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=80)
    builder.add_terminal("X003")
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    builder.add_terminal("X103")

    result = builder.build(count=3)

    # Each terminal gets 1 pin per instance, 3 instances
    assert result.state["terminal_counters"]["X003"] == 3
    assert result.state["terminal_counters"]["X103"] == 3
