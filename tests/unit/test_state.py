"""Unit tests for GenerationState."""

from pyschemaelectrical.model.state import GenerationState, create_initial_state
from pyschemaelectrical.system.connection_registry import TerminalRegistry


def test_create_initial_state():
    """Initial state should be a GenerationState with default values."""
    state = create_initial_state()
    assert isinstance(state, GenerationState)
    assert state.tags == {}
    assert state.terminal_counters == {}
    assert state.contact_channels == {}
    assert isinstance(state.terminal_registry, TerminalRegistry)
    assert state.pin_counter == 0


def test_generation_state_to_dict_round_trip():
    """State should survive dict conversion."""
    gs = GenerationState(tags={"K": 1}, terminal_counters={"X1": 5}, pin_counter=10)
    d = gs.to_dict()

    # Check checks
    gs2 = GenerationState.from_dict(d)
    assert gs2.tags == {"K": 1}
    assert gs2.terminal_counters == {"X1": 5}
    assert gs2.contact_channels == {}
    # terminal_registry defaults to TerminalRegistry()
    # which is comparable to another empty instance
    assert gs2.terminal_registry == TerminalRegistry()
    assert gs2.pin_counter == 10


def test_generation_state_is_frozen():
    """GenerationState should be immutable (frozen dataclass)."""
    gs = GenerationState()
    try:
        gs.tags = {"K": 1}  # type: ignore[invalid-assignment]
        raise AssertionError("Should have raised FrozenInstanceError")
    except AttributeError:
        pass  # Expected for frozen dataclass
