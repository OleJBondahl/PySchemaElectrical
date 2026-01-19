"""Unit tests for GenerationState."""

import pytest
from pyschemaelectrical.model.state import GenerationState, create_initial_state


def test_create_initial_state():
    """Initial state should have all required keys."""
    state = create_initial_state()
    assert "tags" in state
    assert "terminal_counters" in state
    assert "contact_channels" in state
    assert "terminal_registry" in state
    assert "pin_counter" in state


def test_generation_state_to_dict_round_trip():
    """State should survive dict conversion."""
    gs = GenerationState(tags={"K": 1}, terminal_counters={"X1": 5}, pin_counter=10)
    d = gs.to_dict()

    # Check checks
    gs2 = GenerationState.from_dict(d)
    assert gs2.tags == {"K": 1}
    assert gs2.terminal_counters == {"X1": 5}
    assert gs2.contact_channels == {}
    # terminal_registry defaults to TerminalRegistry() which is comparable to another empty instance
    from pyschemaelectrical.system.connection_registry import TerminalRegistry

    assert gs2.terminal_registry == TerminalRegistry()
    assert gs2.pin_counter == 10
