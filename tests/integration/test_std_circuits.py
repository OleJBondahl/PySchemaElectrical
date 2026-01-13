import pytest
import pytest
from pyschemaelectrical.std_circuits import (
    create_dol_starter, 
    create_psu, 
    create_changeover, 
    create_emergency_stop, 
    create_motor_control
)
from pyschemaelectrical.utils.autonumbering import create_autonumberer
from pyschemaelectrical.utils.renderer import render_to_svg
from pyschemaelectrical.builder import CircuitBuilder

def render_circuit_to_string(circuit):
    """Helper to render a circuit element list to SVG string."""
    # We use a temporary string Io or just render_to_svg to a dummy path? 
    # Actually render_to_svg takes a path string. 
    # But checking renderer.py, maybe we can use to_xml_element directly and tostring.
    from pyschemaelectrical.utils.renderer import to_xml_element
    import xml.etree.ElementTree as ET
    
    root = to_xml_element(circuit.elements)
    return ET.tostring(root, encoding="unicode")

class TestStandardCircuitsSnapshot:
    """
    Regression tests for standard circuits.
    These tests render the circuits and compare the SVG output against stored snapshots.
    """

    def test_dol_starter_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        # DOL Starter is usually built via helper or builder.
        # Ideally we test the `create_dol_starter` function if it returns a circuit.
        state, circuit, _ = create_dol_starter(state, 0, 0)
        
        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "dol_starter")

    def test_psu_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        state, circuit, _ = create_psu(state, 0, 0)
        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "psu_circuit")

    def test_changeover_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        state, circuit, _ = create_changeover(state, 0, 0)
        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "changeover_circuit")

    def test_emergency_stop_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        state, circuit, _ = create_emergency_stop(state, 0, 0)
        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "emergency_stop")

    def test_motor_control_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        state, circuit, _ = create_motor_control(state, 0, 0)
        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "motor_control")

    def test_builder_integration_dry_run(self, snapshot_svg):
        """Test a manual build process representing a real user flow."""
        state = create_autonumberer()
        builder = CircuitBuilder(state)
        builder.set_layout(0, 0)
        
        # Add terminals and components like a small system
        builder.add_terminal("X1", poles=3)
        # We need sumbols. Importing from library directly for this test
        from pyschemaelectrical.symbols.protection import three_pole_thermal_overload
        from pyschemaelectrical.symbols.assemblies import contactor
        
        builder.add_component(three_pole_thermal_overload, tag_prefix="-F", poles=3)
        builder.add_component(contactor, tag_prefix="-K", poles=3)
        builder.add_terminal("X2", poles=3)
        
        result = builder.build()
        svg_content = render_circuit_to_string(result.circuit)
        snapshot_svg(svg_content, "builder_integration_flow")
