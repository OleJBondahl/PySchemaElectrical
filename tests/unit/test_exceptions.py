"""Tests for custom exception classes (Task 10A)."""

import pytest

from pyschemaelectrical.exceptions import (
    CircuitValidationError,
    ComponentNotFoundError,
    PortNotFoundError,
    TagReuseExhausted,
    WireLabelCountMismatch,
)


def test_port_not_found_includes_available():
    """PortNotFoundError should include component tag, port, and available ports."""
    err = PortNotFoundError("F1", "PE", ["1", "2", "3", "4"])
    assert "PE" in str(err)
    assert "F1" in str(err)
    assert "['1', '2', '3', '4']" in str(err)
    assert err.component_tag == "F1"
    assert err.port_id == "PE"
    assert err.available_ports == ["1", "2", "3", "4"]


def test_component_not_found_message():
    """ComponentNotFoundError should include index and valid range."""
    err = ComponentNotFoundError(5, 3)
    assert "5" in str(err)
    assert "0-3" in str(err)


def test_tag_reuse_exhausted_message():
    """TagReuseExhausted should include prefix and source tags."""
    err = TagReuseExhausted("K", ["K1", "K2"])
    assert "K" in str(err)
    assert "K1" in str(err)
    assert "K2" in str(err)
    assert "2 tags" in str(err)
    assert err.prefix == "K"
    assert err.available_tags == ["K1", "K2"]


def test_wire_label_count_mismatch_message():
    """WireLabelCountMismatch should include expected/actual counts."""
    err = WireLabelCountMismatch(expected=5, actual=3, circuit_key="pumps")
    assert "5" in str(err)
    assert "3" in str(err)
    assert "pumps" in str(err)
    assert err.expected == 5
    assert err.actual == 3


def test_wire_label_count_mismatch_no_circuit_key():
    """WireLabelCountMismatch should work without circuit_key."""
    err = WireLabelCountMismatch(expected=5, actual=3)
    assert "5" in str(err)
    assert "3" in str(err)


def test_all_inherit_from_circuit_validation_error():
    """All custom exceptions should inherit from CircuitValidationError."""
    assert issubclass(PortNotFoundError, CircuitValidationError)
    assert issubclass(ComponentNotFoundError, CircuitValidationError)
    assert issubclass(TagReuseExhausted, CircuitValidationError)
    assert issubclass(WireLabelCountMismatch, CircuitValidationError)


def test_circuit_validation_error_is_exception():
    """CircuitValidationError should be a standard Exception."""
    assert issubclass(CircuitValidationError, Exception)
    with pytest.raises(CircuitValidationError):
        raise CircuitValidationError("test error")
