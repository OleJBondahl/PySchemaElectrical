"""Unit tests for system module."""

import pytest
from pyschemaelectrical.system.system import Circuit, merge_circuits


def test_merge_circuits_returns_new_circuit():
    """merge_circuits should return a new Circuit, not mutate."""
    c1 = Circuit(symbols=[], elements=["a", "b"])
    c2 = Circuit(symbols=[], elements=["c", "d"])

    result = merge_circuits(c1, c2)

    # Result is a new circuit
    assert result is not c1
    assert result is not c2

    # Original circuits unchanged
    assert c1.elements == ["a", "b"]
    assert c2.elements == ["c", "d"]

    # Merged result correct
    assert result.elements == ["a", "b", "c", "d"]
