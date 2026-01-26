from pyschemaelectrical.model.core import Symbol

# Imports from symbol library - assuming they are exposed correctly or via submodule
from pyschemaelectrical.symbols.terminals import (
    terminal_symbol,
    three_pole_terminal_symbol,
)
from pyschemaelectrical.symbols.contacts import (
    normally_open_symbol,
    normally_closed_symbol,
    three_pole_normally_open_symbol,
)
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.symbols.protection import three_pole_thermal_overload_symbol
from pyschemaelectrical.symbols.assemblies import (
    contactor_symbol,
    turn_switch_assembly_symbol,
)
from pyschemaelectrical.symbols.actuators import turn_switch_symbol
from pyschemaelectrical.symbols.motors import motor_symbol, three_pole_motor_symbol


class TestSymbolsUnit:
    def test_terminals(self):
        s = terminal_symbol("X1", ("1",))
        assert isinstance(s, Symbol)
        # Should have 2 ports (top and bottom)
        assert len(s.ports) >= 2

        s3 = three_pole_terminal_symbol("X3", ("1", "2", "3", "4", "5", "6"))
        assert isinstance(s3, Symbol)
        assert len(s3.ports) == 6

    def test_contacts(self):
        no = normally_open_symbol("-K1", ("13", "14"))
        assert isinstance(no, Symbol)
        assert len(no.elements) > 0
        assert "1" in no.ports  # Internal port ID maps to pins
        assert "2" in no.ports

        nc = normally_closed_symbol("-K2", ("11", "12"))
        assert isinstance(nc, Symbol)

        no3 = three_pole_normally_open_symbol("-Q1", ("1", "2", "3", "4", "5", "6"))
        assert isinstance(no3, Symbol)
        # Should have 6 ports
        assert len(no3.ports) >= 6

    def test_coil(self):
        c = coil_symbol("-K1", ("A1", "A2"))
        assert isinstance(c, Symbol)
        assert len(c.ports) == 2

    def test_protection(self):
        t = three_pole_thermal_overload_symbol("-F1", ("1", "2", "3", "4", "5", "6"))
        assert isinstance(t, Symbol)
        assert len(t.ports) == 6

    def test_assemblies_contactor(self):
        k = contactor_symbol("-K1", ("A1", "A2"), ("1", "2", "3", "4", "5", "6"))
        assert isinstance(k, Symbol)
        # Contactor has coil (2 ports) + 3 pole contact (6 ports) = 8 ports
        assert len(k.ports) == 8
        assert k.label == "-K1"

    def test_single_phase_motor(self):
        """Test single-phase motor symbol creation."""
        m = motor_symbol("-M1", ("1", "2"))
        assert isinstance(m, Symbol)
        assert len(m.ports) == 2
        assert "1" in m.ports
        assert "2" in m.ports
        assert m.label == "-M1"
        # Should have elements (circle, text, lines)
        assert len(m.elements) > 0

    def test_three_phase_motor(self):
        """Test three-phase motor symbol creation."""
        m3 = three_pole_motor_symbol("-M1", ("U", "V", "W", "PE"))
        assert isinstance(m3, Symbol)
        assert len(m3.ports) == 4
        assert "U" in m3.ports
        assert "V" in m3.ports
        assert "W" in m3.ports
        assert "PE" in m3.ports
        assert m3.label == "-M1"
        # Should have multiple elements (circle, text, terminal lines)
        assert len(m3.elements) > 0

    def test_three_phase_motor_positions(self):
        """Test three-phase motor symbol pin positions."""
        # Pins should populate left to right: U, V, W
        m3 = three_pole_motor_symbol("-M1", ("U", "V", "W", "PE"))

        u_pos = m3.ports["U"].position
        v_pos = m3.ports["V"].position
        w_pos = m3.ports["W"].position
        pe_pos = m3.ports["PE"].position

        # Verify relative X order
        assert u_pos.x < v_pos.x
        assert v_pos.x < w_pos.x

        # Verify specific offsets (based on DEFAULT_POLE_SPACING=10)
        # U: -10, V: 0, W: 10
        assert abs(u_pos.x - (-10.0)) < 0.001
        assert abs(v_pos.x - 0.0) < 0.001
        assert abs(w_pos.x - 10.0) < 0.001

        # PE should be to the right (at radius=20)
        assert pe_pos.x > w_pos.x
        assert abs(pe_pos.x - 20.0) < 0.001

    def test_turn_switch_symbol_creation(self):
        """Test basic creation of turn switch symbol."""
        sym = turn_switch_symbol()
        assert sym is not None
        assert isinstance(sym, Symbol)
        assert len(sym.elements) == 3  # TOP, MID, BOT lines
        assert len(sym.ports) == 0  # Actuator symbols have no ports

    def test_turn_switch_symbol_with_label(self):
        """Test turn switch symbol with label."""
        sym = turn_switch_symbol(label="-S1")
        assert sym is not None
        assert sym.label == "-S1"

    def test_turn_switch_symbol_rotation(self):
        """Test rotation is applied."""
        sym = turn_switch_symbol(rotation=180)
        assert sym is not None
        assert len(sym.elements) == 3
        # Elements should be transformed (rotation applied)

    def test_turn_switch_assembly_creation(self):
        """Test basic creation of turn switch assembly."""
        sym = turn_switch_assembly_symbol()
        assert sym is not None
        assert isinstance(sym, Symbol)
        # Assembly should have multiple elements: contact + linkage + actuator
        assert len(sym.elements) > 3

    def test_turn_switch_assembly_has_ports(self):
        """Assembly inherits ports from NO contact."""
        sym = turn_switch_assembly_symbol()
        assert "1" in sym.ports
        assert "2" in sym.ports
        assert len(sym.ports) == 2

    def test_turn_switch_assembly_custom_pins(self):
        """Test custom pin labels."""
        sym = turn_switch_assembly_symbol(label="-S1", pins=("A", "B"))
        assert sym.label == "-S1"
        # Ports always use internal IDs "1" and "2", pins are just visual labels
        assert "1" in sym.ports
        assert "2" in sym.ports
