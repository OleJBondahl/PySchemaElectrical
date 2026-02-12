from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.std_circuits import (
    changeover,
    dol_starter,
    emergency_stop,
    spdt,
)
from pyschemaelectrical.utils.autonumbering import create_autonumberer


def render_circuit_to_string(circuit):
    """Helper to render a circuit element list to SVG string."""
    # We use a temporary string Io or just render_to_svg to a dummy path?
    # Actually render_to_svg takes a path string.
    # But checking renderer.py, maybe we can use to_xml_element directly and tostring.
    import xml.etree.ElementTree as ET

    from pyschemaelectrical.utils.renderer import to_xml_element

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
        state, circuit, _ = dol_starter(
            state, 0, 0, tm_top="X1", tm_bot="X2", tm_bot_right="X3"
        )

        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "dol_starter")

    def test_changeover_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        state, circuit, _ = changeover(
            state, 0, 0, tm_top_left="X1", tm_top_right="X2", tm_bot="X3"
        )
        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "changeover_circuit")

    def test_emergency_stop_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        state, circuit, _ = emergency_stop(state, 0, 0, tm_top="X1", tm_bot="X2")
        svg_content = render_circuit_to_string(circuit)
        snapshot_svg(svg_content, "emergency_stop")

    def test_motor_control_snapshot(self, snapshot_svg):
        state = create_autonumberer()
        state, circuit, _ = spdt(
            state, 0, 0, tm_top="X1", tm_bot_left="X2", tm_bot_right="X3"
        )
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
        from pyschemaelectrical.symbols.assemblies import contactor_symbol
        from pyschemaelectrical.symbols.protection import (
            three_pole_thermal_overload_symbol,
        )

        builder.add_component(
            three_pole_thermal_overload_symbol, tag_prefix="-F", poles=3
        )
        builder.add_component(contactor_symbol, tag_prefix="-K", poles=3)
        builder.add_terminal("X2", poles=3)

        result = builder.build()
        svg_content = render_circuit_to_string(result.circuit)
        snapshot_svg(svg_content, "builder_integration_flow")
