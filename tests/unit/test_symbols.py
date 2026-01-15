import pytest
from pyschemaelectrical.model.core import Symbol

# Imports from symbol library - assuming they are exposed correctly or via submodule
from pyschemaelectrical.symbols.terminals import terminal_symbol, three_pole_terminal_symbol
from pyschemaelectrical.symbols.contacts import normally_open_symbol, normally_closed_symbol, three_pole_normally_open_symbol
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.symbols.protection import three_pole_thermal_overload_symbol
from pyschemaelectrical.symbols.assemblies import contactor_symbol

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
        assert "1" in no.ports # Internal port ID maps to pins
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
