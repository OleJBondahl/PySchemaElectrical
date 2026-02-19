"""
Tests for the ct_terminals branch in dol_starter().

Covers all code paths within the ct_terminals logic (lines 182-226 and 284-287
of motor.py), including:
- String terminal IDs (physical terminal symbols)
- Terminal objects with reference=True (reference arrow symbols)
- used_terminals accumulation
- Single and multi-instance (count>1) CT handling
- Element count comparison with/without ct_terminals
"""

from pyschemaelectrical.model.primitives import Line
from pyschemaelectrical.std_circuits.motor import dol_starter
from pyschemaelectrical.system.connection_registry import get_registry
from pyschemaelectrical.terminal import Terminal
from pyschemaelectrical.utils.autonumbering import create_autonumberer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_lines(circuit):
    """Count the number of Line elements in a circuit."""
    return sum(1 for e in circuit.elements if isinstance(e, Line))


# ---------------------------------------------------------------------------
# 1. ct_terminals with plain string terminal IDs
# ---------------------------------------------------------------------------

class TestCtTerminalsString:
    """Tests for ct_terminals when passed as plain string IDs."""

    def test_ct_terminals_string_basic(self):
        """dol_starter with ct_terminals as string tuple places terminal symbols."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
        )
        assert len(result.circuit.elements) > 0

    def test_ct_terminals_string_adds_elements(self):
        """Providing ct_terminals should produce more elements than without."""
        state_without = create_autonumberer()
        result_without = dol_starter(
            state_without, 0, 0, tm_top="X1", tm_bot="X2",
        )

        state_with = create_autonumberer()
        result_with = dol_starter(
            state_with, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
        )

        assert len(result_with.circuit.elements) > len(result_without.circuit.elements)

    def test_ct_terminals_string_in_used_terminals(self):
        """String ct_terminals IDs should appear in used_terminals."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3"),
        )
        assert "X3" in result.used_terminals

    def test_ct_terminals_multiple_distinct_in_used_terminals(self):
        """Multiple distinct string ct_terminal IDs all appear in used_terminals."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X4", "X5", "X6"),
        )
        assert "X3" in result.used_terminals
        assert "X4" in result.used_terminals
        assert "X5" in result.used_terminals
        assert "X6" in result.used_terminals

    def test_ct_terminals_string_creates_wire_lines(self):
        """Each ct_terminal should produce a wire (Line) from CT port to terminal."""
        state_without = create_autonumberer()
        result_without = dol_starter(
            state_without, 0, 0, tm_top="X1", tm_bot="X2",
        )

        state_with = create_autonumberer()
        result_with = dol_starter(
            state_with, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
        )

        lines_without = _count_lines(result_without.circuit)
        lines_with = _count_lines(result_with.circuit)
        # Each ct_terminal entry generates one wire Line
        assert lines_with > lines_without

    def test_ct_terminals_string_registers_connections(self):
        """String ct_terminals should register connections in the terminal registry."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
        )
        registry = get_registry(result.state)
        # There should be connections registered for X3
        x3_connections = [
            c for c in registry.connections if c.terminal_tag == "X3"
        ]
        assert len(x3_connections) > 0
        # Each connection should point to a CT-prefixed component
        for conn in x3_connections:
            assert conn.component_tag.startswith("CT")

    def test_ct_terminals_string_partial_pins(self):
        """ct_terminals with fewer entries than ct_pins should only place those."""
        state_full = create_autonumberer()
        result_full = dol_starter(
            state_full, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
        )

        state_partial = create_autonumberer()
        result_partial = dol_starter(
            state_partial, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3"),
        )

        # Partial should have fewer elements than full
        assert len(result_partial.circuit.elements) < len(result_full.circuit.elements)

    def test_ct_terminals_label_positions_alternate(self):
        """Odd-indexed ct_terminals get label_pos='right', even get 'left'.

        This exercises the ``lpos`` logic inside the ct_terminals loop.
        We verify indirectly: with 4 terminals, the function runs without error.
        """
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X4", "X5", "X6"),
        )
        # If label_pos logic were broken, add_symbol would fail
        assert len(result.circuit.elements) > 0


# ---------------------------------------------------------------------------
# 2. ct_terminals with Terminal objects having reference=True
# ---------------------------------------------------------------------------

class TestCtTerminalsReference:
    """Tests for ct_terminals when Terminal objects with reference=True are used."""

    def test_ct_terminals_reference_basic(self):
        """dol_starter with reference Terminal objects places reference symbols."""
        state = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=(plc_ref, plc_ref, plc_ref, plc_ref),
        )
        assert len(result.circuit.elements) > 0

    def test_ct_terminals_reference_adds_elements(self):
        """Reference ct_terminals should produce more elements than without."""
        state_without = create_autonumberer()
        result_without = dol_starter(
            state_without, 0, 0, tm_top="X1", tm_bot="X2",
        )

        state_with = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result_with = dol_starter(
            state_with, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=(plc_ref, plc_ref, plc_ref, plc_ref),
        )

        assert len(result_with.circuit.elements) > len(result_without.circuit.elements)

    def test_ct_terminals_reference_not_in_used_terminals(self):
        """Reference terminals should NOT appear in used_terminals."""
        state = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=(plc_ref, plc_ref),
        )
        # Reference terminals are excluded from used_terminals
        assert "PLC:AI" not in result.used_terminals

    def test_ct_terminals_reference_registers_connections(self):
        """Reference ct_terminals should register connections in the registry."""
        state = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=(plc_ref, plc_ref, plc_ref, plc_ref),
        )
        registry = get_registry(result.state)
        plc_connections = [
            c for c in registry.connections if c.terminal_tag == "PLC:AI"
        ]
        assert len(plc_connections) > 0
        # Connections should reference CT component
        for conn in plc_connections:
            assert conn.component_tag.startswith("CT")

    def test_ct_terminals_reference_creates_wire_lines(self):
        """Reference ct_terminals should also produce wires from CT port to ref."""
        state_without = create_autonumberer()
        result_without = dol_starter(
            state_without, 0, 0, tm_top="X1", tm_bot="X2",
        )

        state_with = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result_with = dol_starter(
            state_with, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=(plc_ref, plc_ref, plc_ref, plc_ref),
        )

        lines_without = _count_lines(result_without.circuit)
        lines_with = _count_lines(result_with.circuit)
        assert lines_with > lines_without


# ---------------------------------------------------------------------------
# 3. Mixed ct_terminals (string + reference)
# ---------------------------------------------------------------------------

class TestCtTerminalsMixed:
    """Tests for ct_terminals with a mix of string IDs and reference Terminals."""

    def test_mixed_string_and_reference(self):
        """ct_terminals can mix plain strings and reference Terminal objects."""
        state = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", plc_ref, "X4", plc_ref),
        )
        assert len(result.circuit.elements) > 0
        # String terminals should be in used_terminals
        assert "X3" in result.used_terminals
        assert "X4" in result.used_terminals
        # Reference terminals should NOT be in used_terminals
        assert "PLC:AI" not in result.used_terminals

    def test_mixed_registers_both_types(self):
        """Both string and reference ct_terminals register connections."""
        state = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", plc_ref, "X4", plc_ref),
        )
        registry = get_registry(result.state)

        x3_conns = [c for c in registry.connections if c.terminal_tag == "X3"]
        x4_conns = [c for c in registry.connections if c.terminal_tag == "X4"]
        plc_conns = [c for c in registry.connections if c.terminal_tag == "PLC:AI"]

        assert len(x3_conns) > 0
        assert len(x4_conns) > 0
        assert len(plc_conns) > 0


# ---------------------------------------------------------------------------
# 4. Multi-count (count > 1) with ct_terminals
# ---------------------------------------------------------------------------

class TestCtTerminalsMultiCount:
    """Tests for ct_terminals with count > 1."""

    def test_ct_terminals_count_2(self):
        """ct_terminals should work correctly when count=2."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
            count=2,
        )
        assert len(result.circuit.elements) > 0

    def test_ct_terminals_count_2_more_elements_than_count_1(self):
        """count=2 with ct_terminals produces more elements than count=1."""
        state1 = create_autonumberer()
        result1 = dol_starter(
            state1, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
            count=1,
        )

        state2 = create_autonumberer()
        result2 = dol_starter(
            state2, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
            count=2,
        )

        assert len(result2.circuit.elements) > len(result1.circuit.elements)

    def test_ct_terminals_count_2_registers_more_connections(self):
        """count=2 with ct_terminals registers connections for both instances."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
            count=2,
        )
        registry = get_registry(result.state)
        x3_conns = [c for c in registry.connections if c.terminal_tag == "X3"]
        # 2 instances x 4 ct_terminals = 8 connections
        assert len(x3_conns) >= 8

    def test_ct_terminals_reference_count_2(self):
        """Reference ct_terminals work correctly with count=2."""
        state = create_autonumberer()
        plc_ref = Terminal("PLC:AI", reference=True)
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=(plc_ref, plc_ref, plc_ref, plc_ref),
            count=2,
        )
        assert len(result.circuit.elements) > 0
        # Reference terminals should still not appear in used_terminals
        assert "PLC:AI" not in result.used_terminals

    def test_ct_terminals_per_instance_bot_terminals(self):
        """ct_terminals work with per-instance tm_bot lists."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot=["X010", "X011"],
            ct_terminals=("X3", "X3", "X3", "X3"),
            count=2,
        )
        assert len(result.circuit.elements) > 0
        assert "X010" in result.used_terminals
        assert "X011" in result.used_terminals
        assert "X3" in result.used_terminals


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------

class TestCtTerminalsEdgeCases:
    """Edge case tests for ct_terminals."""

    def test_ct_terminals_none_is_default(self):
        """When ct_terminals is None (default), no CT-related extras are added."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=None,
        )
        # Just verify it works and only has base terminals
        assert result.used_terminals == ["X1", "X2"]

    def test_ct_terminals_empty_tuple(self):
        """An empty ct_terminals tuple should behave like None."""
        state_none = create_autonumberer()
        result_none = dol_starter(
            state_none, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=None,
        )

        state_empty = create_autonumberer()
        result_empty = dol_starter(
            state_empty, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=(),
        )

        # Both should have the same number of elements
        assert len(result_none.circuit.elements) == len(result_empty.circuit.elements)

    def test_ct_terminals_exceeding_ct_pins(self):
        """ct_terminals longer than ct_pins should be capped at ct_pins length."""
        state = create_autonumberer()
        # Default ct_pins has 4 entries ("1", "2", "3", "4")
        # Provide 6 ct_terminals -- only 4 should be placed
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3", "X3", "X3"),
        )

        state_exact = create_autonumberer()
        result_exact = dol_starter(
            state_exact, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3", "X3", "X3"),
        )

        # Should produce the same number of elements (extra entries ignored)
        assert len(result.circuit.elements) == len(result_exact.circuit.elements)

    def test_ct_terminals_duplicate_not_duplicated_in_used(self):
        """A ct_terminal ID already in used_terminals is not duplicated."""
        state = create_autonumberer()
        # X1 is already tm_top; if ct_terminals also uses X1, it should
        # not appear twice in used_terminals
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X1", "X1"),
        )
        # X1 should appear only once
        assert result.used_terminals.count("X1") == 1

    def test_ct_terminals_with_custom_ct_pins(self):
        """ct_terminals works correctly with custom ct_pins."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_pins=("A", "B"),
            ct_terminals=("X3", "X4"),
        )
        assert len(result.circuit.elements) > 0
        assert "X3" in result.used_terminals
        assert "X4" in result.used_terminals

        # Verify connections reference the custom CT pins
        registry = get_registry(result.state)
        ct_conns = [
            c for c in registry.connections
            if c.terminal_tag in ("X3", "X4")
        ]
        assert len(ct_conns) > 0
        pin_values = {c.component_pin for c in ct_conns}
        # Should use our custom pin IDs, not the defaults
        assert pin_values.issubset({"A", "B"})

    def test_ct_terminals_with_invalid_port_id_skipped(self):
        """ct_pins with a port ID not present on the CT symbol should be skipped."""
        state = create_autonumberer()
        # Use ct_pins where "NONEXISTENT" won't match any port on the CT symbol.
        # The first pin "1" is valid, "NONEXISTENT" is not -> hits the continue branch.
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_pins=("1", "NONEXISTENT", "3", "4"),
            ct_terminals=("X3", "X3", "X3", "X3"),
        )
        # Should not crash; the invalid port is simply skipped
        assert len(result.circuit.elements) > 0


# ---------------------------------------------------------------------------
# 6. BuildResult metadata
# ---------------------------------------------------------------------------

class TestCtTerminalsBuildResult:
    """Verify BuildResult metadata when ct_terminals is used."""

    def test_component_map_includes_ct(self):
        """component_map should include CT tag prefix entries."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3"),
        )
        assert "CT" in result.component_map
        assert len(result.component_map["CT"]) >= 1
        assert result.component_map["CT"][0] == "CT1"

    def test_component_map_ct_count_2(self):
        """With count=2, component_map should have 2 CT entries."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3"),
            count=2,
        )
        assert "CT" in result.component_map
        assert len(result.component_map["CT"]) == 2
        assert result.component_map["CT"][0] == "CT1"
        assert result.component_map["CT"][1] == "CT2"

    def test_state_tag_counter_advances(self):
        """The CT tag counter should advance in the returned state."""
        state = create_autonumberer()
        result = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3"),
        )
        # After creating CT1, the tag counter for CT should be 1
        assert result.state.tags.get("CT", 0) >= 1

    def test_tuple_unpacking_backwards_compat(self):
        """BuildResult supports tuple unpacking (state, circuit, used_terminals)."""
        state = create_autonumberer()
        new_state, circuit, used = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2",
            ct_terminals=("X3", "X3"),
        )
        assert len(circuit.elements) > 0
        assert "X3" in used
