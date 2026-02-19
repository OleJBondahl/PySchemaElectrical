"""
Unit tests for the field_devices module.

Tests cover the PinDef, DeviceTemplate, and generate_field_connections()
function with all three pin numbering modes: sequential, prefixed, and fixed.
"""

import pytest

from pyschemaelectrical.terminal import Terminal
from pyschemaelectrical.field_devices import (
    ConnectionRow,
    DeviceEntry,
    DeviceTemplate,
    PinDef,
    generate_field_connections,
)


# ---------------------------------------------------------------------------
# Fixtures: reusable terminals and templates
# ---------------------------------------------------------------------------


@pytest.fixture
def signal_terminal():
    return Terminal("X100", "Signal terminal")


@pytest.fixture
def power_terminal():
    return Terminal("X200", "Power terminal", pin_prefixes=("L1", "L2", "L3", "N"))


@pytest.fixture
def plc_ai():
    return Terminal("PLC:AI", "PLC Analog Input", reference=True)


@pytest.fixture
def plc_di():
    return Terminal("PLC:DI", "PLC Digital Input", reference=True)


@pytest.fixture
def ext_gnd():
    return Terminal("X300", "External GND")


# ---------------------------------------------------------------------------
# PinDef / DeviceTemplate construction
# ---------------------------------------------------------------------------


class TestPinDef:
    """Tests for the PinDef frozen dataclass."""

    def test_defaults(self):
        pin = PinDef("Sig+")
        assert pin.device_pin == "Sig+"
        assert pin.terminal is None
        assert pin.plc is None
        assert pin.terminal_pin == ""
        assert pin.pin_prefix == ""

    def test_with_terminal_and_plc(self, signal_terminal, plc_ai):
        pin = PinDef("Sig+", signal_terminal, plc_ai)
        assert pin.terminal is signal_terminal
        assert pin.plc is plc_ai

    def test_with_fixed_pin(self):
        pin = PinDef("U1", terminal_pin="L1")
        assert pin.terminal_pin == "L1"

    def test_with_prefix(self):
        pin = PinDef("L1", pin_prefix="L1")
        assert pin.pin_prefix == "L1"

    def test_frozen(self, signal_terminal):
        pin = PinDef("Sig+", signal_terminal)
        with pytest.raises(AttributeError):
            pin.device_pin = "GND"  # type: ignore[misc]


class TestDeviceTemplate:
    """Tests for the DeviceTemplate frozen dataclass."""

    def test_construction(self, signal_terminal, plc_ai):
        template = DeviceTemplate(
            mpn="4-20mA Sensor",
            pins=(
                PinDef("Sig+", signal_terminal, plc_ai),
                PinDef("GND", signal_terminal),
            ),
        )
        assert template.mpn == "4-20mA Sensor"
        assert len(template.pins) == 2
        assert template.pins[0].device_pin == "Sig+"
        assert template.pins[1].device_pin == "GND"

    def test_frozen(self, signal_terminal):
        template = DeviceTemplate(
            mpn="Test",
            pins=(PinDef("1", signal_terminal),),
        )
        with pytest.raises(AttributeError):
            template.mpn = "Other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Sequential pin numbering (default mode)
# ---------------------------------------------------------------------------


class TestSequentialPins:
    """Tests for auto-numbered sequential pins."""

    def test_single_device(self, signal_terminal, plc_ai):
        """Single device with two pins on same terminal auto-numbers 1, 2."""
        template = DeviceTemplate(
            mpn="4-20mA",
            pins=(
                PinDef("Sig+", signal_terminal, plc_ai),
                PinDef("GND", signal_terminal),
            ),
        )
        rows = generate_field_connections([("PT-01", template)])

        assert len(rows) == 2
        # Row structure: (tag, device_pin, terminal, terminal_pin, plc_tag, "")
        assert rows[0] == ("PT-01", "Sig+", signal_terminal, "1", "PLC:AI", "")
        assert rows[1] == ("PT-01", "GND", signal_terminal, "2", "", "")

    def test_multiple_devices_same_terminal(self, signal_terminal, plc_ai):
        """Multiple devices on the same terminal continue numbering."""
        template = DeviceTemplate(
            mpn="4-20mA",
            pins=(
                PinDef("Sig+", signal_terminal, plc_ai),
                PinDef("GND", signal_terminal),
            ),
        )
        rows = generate_field_connections([
            ("PT-01", template),
            ("PT-02", template),
        ])

        assert len(rows) == 4
        # First device gets pins 1, 2
        assert rows[0][3] == "1"
        assert rows[1][3] == "2"
        # Second device continues with 3, 4
        assert rows[2][3] == "3"
        assert rows[3][3] == "4"

    def test_different_terminals(self, signal_terminal, ext_gnd, plc_di):
        """Pins on different terminals have independent counters."""
        template = DeviceTemplate(
            mpn="Level Switch",
            pins=(
                PinDef("1", signal_terminal, plc_di),
                PinDef("2", ext_gnd),
            ),
        )
        rows = generate_field_connections([
            ("LS-01", template),
            ("LS-02", template),
        ])

        assert len(rows) == 4
        # X100 pins: 1, 2 (from LS-01 pin "1" and LS-02 pin "1")
        assert rows[0][3] == "1"  # LS-01, X100
        assert rows[2][3] == "2"  # LS-02, X100
        # X300 pins: 1, 2 (independent counter)
        assert rows[1][3] == "1"  # LS-01, X300
        assert rows[3][3] == "2"  # LS-02, X300


# ---------------------------------------------------------------------------
# Prefixed pin numbering (pin_prefix mode)
# ---------------------------------------------------------------------------


class TestPrefixedPins:
    """Tests for prefix-based group numbering."""

    def test_single_device_prefixed(self):
        """Prefixed pins format as prefix:group_number."""
        terminal = Terminal("X200", "Power")
        template = DeviceTemplate(
            mpn="400V 3P+N",
            pins=(
                PinDef("L1", terminal, pin_prefix="L1"),
                PinDef("L2", terminal, pin_prefix="L2"),
                PinDef("L3", terminal, pin_prefix="L3"),
                PinDef("N", terminal, pin_prefix="N"),
            ),
        )
        rows = generate_field_connections([("400V Main", template)])

        assert len(rows) == 4
        assert rows[0][3] == "L1:1"
        assert rows[1][3] == "L2:1"
        assert rows[2][3] == "L3:1"
        assert rows[3][3] == "N:1"

    def test_multiple_devices_prefixed(self):
        """Multiple devices with same prefixes increment the group number."""
        terminal = Terminal("X200", "Power")
        template = DeviceTemplate(
            mpn="230V 3P",
            pins=(
                PinDef("L1", terminal, pin_prefix="L1"),
                PinDef("L2", terminal, pin_prefix="L2"),
                PinDef("L3", terminal, pin_prefix="L3"),
            ),
        )
        rows = generate_field_connections([
            ("Feed A", template),
            ("Feed B", template),
        ])

        assert len(rows) == 6
        # First device: group 1
        assert rows[0][3] == "L1:1"
        assert rows[1][3] == "L2:1"
        assert rows[2][3] == "L3:1"
        # Second device: group 2
        assert rows[3][3] == "L1:2"
        assert rows[4][3] == "L2:2"
        assert rows[5][3] == "L3:2"

    def test_partial_prefix_overlap(self):
        """Devices using different subsets of prefixes on same terminal."""
        terminal = Terminal("X200", "Power")
        template_full = DeviceTemplate(
            mpn="400V 3P+N",
            pins=(
                PinDef("L1", terminal, pin_prefix="L1"),
                PinDef("L2", terminal, pin_prefix="L2"),
                PinDef("L3", terminal, pin_prefix="L3"),
                PinDef("N", terminal, pin_prefix="N"),
            ),
        )
        template_n_only = DeviceTemplate(
            mpn="N-only device",
            pins=(
                PinDef("A1", terminal, pin_prefix="N"),
                PinDef("A2", terminal, pin_prefix="L1"),
            ),
        )
        rows = generate_field_connections([
            ("Dev A", template_full),
            ("Dev B", template_n_only),
        ])

        # Dev A: all prefixes get group 1
        assert rows[0][3] == "L1:1"
        assert rows[1][3] == "L2:1"
        assert rows[2][3] == "L3:1"
        assert rows[3][3] == "N:1"
        # Dev B: uses N and L1, max(N=1, L1=1) + 1 = 2
        assert rows[4][3] == "N:2"
        assert rows[5][3] == "L1:2"


# ---------------------------------------------------------------------------
# Fixed pin numbering (terminal_pin mode)
# ---------------------------------------------------------------------------


class TestFixedPins:
    """Tests for fixed terminal pin names."""

    def test_fixed_pins(self):
        """Fixed terminal_pin values are used directly, not auto-numbered."""
        terminal = Terminal("X500", "Motor terminal")
        template = DeviceTemplate(
            mpn="Pump 3P",
            pins=(
                PinDef("U1", terminal, terminal_pin="L1"),
                PinDef("V1", terminal, terminal_pin="L2"),
                PinDef("W1", terminal, terminal_pin="L3"),
            ),
        )
        rows = generate_field_connections([("PU-01", template)])

        assert len(rows) == 3
        assert rows[0][3] == "L1"
        assert rows[1][3] == "L2"
        assert rows[2][3] == "L3"

    def test_fixed_pins_do_not_affect_sequential(self, signal_terminal):
        """Fixed pins don't increment the sequential counter."""
        terminal = Terminal("X500", "Motor terminal")
        fixed_template = DeviceTemplate(
            mpn="Motor",
            pins=(
                PinDef("U1", terminal, terminal_pin="L1"),
            ),
        )
        seq_template = DeviceTemplate(
            mpn="Sensor",
            pins=(
                PinDef("1", terminal),
            ),
        )
        rows = generate_field_connections([
            ("M-01", fixed_template),
            ("S-01", seq_template),
        ])

        assert rows[0][3] == "L1"  # fixed
        assert rows[1][3] == "1"   # sequential starts at 1


# ---------------------------------------------------------------------------
# Terminal override
# ---------------------------------------------------------------------------


class TestTerminalOverride:
    """Tests for the terminal_override in DeviceEntry tuples."""

    def test_override_fills_missing_terminals(self):
        """PinDef without terminal uses the override from DeviceEntry."""
        override = Terminal("X400", "Override terminal")
        template = DeviceTemplate(
            mpn="Motor",
            pins=(
                PinDef("U1", terminal_pin="L1"),
                PinDef("V1", terminal_pin="L2"),
            ),
        )
        rows = generate_field_connections([("M-01", template, override)])

        assert len(rows) == 2
        assert rows[0][2] is override
        assert rows[1][2] is override

    def test_pindef_terminal_takes_precedence(self):
        """PinDef terminal is used even when override is provided."""
        override = Terminal("X400", "Override")
        specific = Terminal("X500", "Specific")
        template = DeviceTemplate(
            mpn="Mixed",
            pins=(
                PinDef("1", specific),
                PinDef("2"),  # No terminal, will use override
            ),
        )
        rows = generate_field_connections([("D-01", template, override)])

        assert rows[0][2] is specific
        assert rows[1][2] is override


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrors:
    """Tests for error conditions."""

    def test_missing_terminal_raises(self):
        """Raises ValueError when pin has no terminal and no override."""
        template = DeviceTemplate(
            mpn="Bad",
            pins=(PinDef("1"),),
        )
        with pytest.raises(ValueError, match="no terminal in template"):
            generate_field_connections([("D-01", template)])


# ---------------------------------------------------------------------------
# PLC reference tagging
# ---------------------------------------------------------------------------


class TestPlcReferences:
    """Tests for PLC reference tags in connection rows."""

    def test_plc_tag_present(self, signal_terminal, plc_ai):
        template = DeviceTemplate(
            mpn="Sensor",
            pins=(PinDef("Sig+", signal_terminal, plc_ai),),
        )
        rows = generate_field_connections([("PT-01", template)])
        assert rows[0][4] == "PLC:AI"

    def test_plc_tag_absent(self, signal_terminal):
        template = DeviceTemplate(
            mpn="Sensor",
            pins=(PinDef("GND", signal_terminal),),
        )
        rows = generate_field_connections([("PT-01", template)])
        assert rows[0][4] == ""


# ---------------------------------------------------------------------------
# Reuse terminals
# ---------------------------------------------------------------------------


class TestReuseTerminals:
    """Tests for the reuse_terminals parameter."""

    def test_reuse_from_list(self, signal_terminal, plc_ai):
        """Reuse pins from an explicit list."""
        template = DeviceTemplate(
            mpn="4-20mA",
            pins=(
                PinDef("Sig+", signal_terminal, plc_ai),
                PinDef("GND", signal_terminal),
            ),
        )
        rows = generate_field_connections(
            [("PT-01", template)],
            reuse_terminals={"X100": ["42", "43"]},
        )

        assert rows[0][3] == "42"
        assert rows[1][3] == "43"

    def test_reuse_does_not_affect_other_terminals(
        self, signal_terminal, ext_gnd, plc_di
    ):
        """Reuse on one terminal doesn't affect sequential on another."""
        template = DeviceTemplate(
            mpn="Level Switch",
            pins=(
                PinDef("1", signal_terminal, plc_di),
                PinDef("2", ext_gnd),
            ),
        )
        rows = generate_field_connections(
            [("LS-01", template)],
            reuse_terminals={"X100": ["99"]},
        )

        assert rows[0][3] == "99"  # reused
        assert rows[1][3] == "1"   # sequential


# ---------------------------------------------------------------------------
# Mixed numbering modes in one template
# ---------------------------------------------------------------------------


class TestMixedModes:
    """Tests for templates with mixed pin numbering modes."""

    def test_mixed_fixed_and_sequential(self):
        """A template with both fixed and sequential pins."""
        terminal = Terminal("X600", "Mixed terminal")
        template = DeviceTemplate(
            mpn="Complex Valve",
            pins=(
                PinDef("A1", terminal, pin_prefix="N"),
                PinDef("A2", terminal, pin_prefix="L"),
                PinDef("B1", terminal),  # sequential
            ),
        )
        rows = generate_field_connections([("XV-01", template)])

        assert rows[0][3] == "N:1"
        assert rows[1][3] == "L:1"
        assert rows[2][3] == "1"  # sequential counter starts at 1


# ---------------------------------------------------------------------------
# ConnectionRow structure
# ---------------------------------------------------------------------------


class TestConnectionRowStructure:
    """Tests for the ConnectionRow tuple structure."""

    def test_row_has_six_fields(self, signal_terminal):
        template = DeviceTemplate(
            mpn="Simple",
            pins=(PinDef("1", signal_terminal),),
        )
        rows = generate_field_connections([("D-01", template)])
        assert len(rows) == 1
        assert len(rows[0]) == 6

    def test_row_fields_are_correct_types(self, signal_terminal, plc_ai):
        template = DeviceTemplate(
            mpn="Simple",
            pins=(PinDef("1", signal_terminal, plc_ai),),
        )
        rows = generate_field_connections([("D-01", template)])
        row = rows[0]
        assert isinstance(row[0], str)           # tag
        assert isinstance(row[1], str)           # device_pin
        assert row[2] is signal_terminal         # terminal object
        assert isinstance(row[3], str)           # terminal_pin
        assert isinstance(row[4], str)           # plc_tag
        assert isinstance(row[5], str)           # reserved (empty)
        assert row[5] == ""


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------


class TestEmptyInput:
    """Tests for edge cases with empty input."""

    def test_empty_device_list(self):
        rows = generate_field_connections([])
        assert rows == []
