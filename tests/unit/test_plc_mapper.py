"""
Tests for PlcMapper declarative PLC I/O mapping.

Task 12A: Verifies module allocation, pin naming, terminal integration,
and connection generation.
"""

import pytest

from pyschemaelectrical.plc import PlcMapper


@pytest.fixture
def mapper():
    """Create a PlcMapper with standard module and sensor types."""
    plc = PlcMapper()
    plc.module_type("AI_mA", capacity=4, pin_format="CH{ch}{polarity}")
    plc.module_type("AI_RTD", capacity=2, pin_format="CH{ch}_{pin}")
    plc.module_type("DI", capacity=8, pin_format="DI{ch}")
    plc.module_type("DO", capacity=8, pin_format="DO{ch}")

    plc.sensor_type(
        "2Wire-mA", module="AI_mA", pins=["Signal", "GND"], polarity={0: "+", 1: "-"}
    )
    plc.sensor_type("RTD", module="AI_RTD", pins=["R+", "RL", "R-"])
    plc.sensor_type("DI_24V", module="DI", pins=["Signal"])
    plc.sensor_type("DO_24V", module="DO", pins=["Signal"])

    return plc


class TestModuleAllocation:
    def test_module_allocation_mA(self, mapper):
        """4 mA sensors should fill exactly 1 AI_mA module (capacity=4)."""
        for i in range(4):
            mapper.sensor(f"PT-{i:02d}", type="2Wire-mA", cable=f"W{i:04d}", terminal="X007")

        counts = mapper.module_count
        assert counts["AI_mA"] == 1

    def test_module_allocation_mA_overflow(self, mapper):
        """5 mA sensors should need 2 AI_mA modules."""
        for i in range(5):
            mapper.sensor(f"PT-{i:02d}", type="2Wire-mA", cable=f"W{i:04d}", terminal="X007")

        counts = mapper.module_count
        assert counts["AI_mA"] == 2

    def test_module_allocation_RTD(self, mapper):
        """3 RTD sensors should need 2 AI_RTD modules (capacity=2)."""
        for i in range(3):
            mapper.sensor(f"TT-{i:02d}", type="RTD", cable=f"W{i:04d}", terminal="X007")

        counts = mapper.module_count
        assert counts["AI_RTD"] == 2

    def test_module_allocation_RTD_exact_fit(self, mapper):
        """2 RTD sensors should fill exactly 1 module."""
        mapper.sensor("TT-01", type="RTD", cable="W0001", terminal="X007")
        mapper.sensor("TT-02", type="RTD", cable="W0002", terminal="X007")

        counts = mapper.module_count
        assert counts["AI_RTD"] == 1


class TestPinNaming:
    def test_pin_naming_mA(self, mapper):
        """mA sensor pins should use CH{ch}{polarity} format."""
        mapper.sensor("PT-01", type="2Wire-mA", cable="W0001", terminal="X007")

        connections = mapper.generate_connections()
        assert len(connections) == 2  # Signal + GND
        assert connections[0].module_pin == "CH1+"  # Signal with + polarity
        assert connections[1].module_pin == "CH1-"  # GND with - polarity

    def test_pin_naming_mA_second_channel(self, mapper):
        """Second mA sensor should get channel 2."""
        mapper.sensor("PT-01", type="2Wire-mA", cable="W0001", terminal="X007")
        mapper.sensor("PT-02", type="2Wire-mA", cable="W0002", terminal="X007")

        connections = mapper.generate_connections()
        assert connections[2].module_pin == "CH2+"
        assert connections[3].module_pin == "CH2-"

    def test_pin_naming_RTD(self, mapper):
        """RTD sensor pins should use CH{ch}_{pin} format."""
        mapper.sensor("TT-01", type="RTD", cable="W0001", terminal="X007")

        connections = mapper.generate_connections()
        assert len(connections) == 3  # R+, RL, R-
        assert connections[0].module_pin == "CH1_R+"
        assert connections[1].module_pin == "CH1_RL"
        assert connections[2].module_pin == "CH1_R-"

    def test_pin_naming_DI(self, mapper):
        """DI sensor pins should use DI{ch} format."""
        mapper.sensor("SW-01", type="DI_24V", cable="W0001", terminal="X008")

        connections = mapper.generate_connections()
        assert len(connections) == 1
        assert connections[0].module_pin == "DI1"

    def test_pin_naming_DO(self, mapper):
        """DO sensor pins should use DO{ch} format."""
        mapper.sensor("RLY-01", type="DO_24V", cable="W0001", terminal="X008")

        connections = mapper.generate_connections()
        assert len(connections) == 1
        assert connections[0].module_pin == "DO1"


class TestTerminalIntegration:
    def test_terminal_pins_sequential(self, mapper):
        """Terminal pins should be allocated sequentially starting from 1."""
        mapper.sensor("TT-01", type="RTD", cable="W0001", terminal="X007")
        mapper.sensor("TT-02", type="RTD", cable="W0002", terminal="X007")

        connections = mapper.generate_connections()
        # TT-01 gets pins 1, 2, 3 (3 wires for RTD)
        assert connections[0].terminal_pin == "1"
        assert connections[1].terminal_pin == "2"
        assert connections[2].terminal_pin == "3"
        # TT-02 gets pins 4, 5, 6
        assert connections[3].terminal_pin == "4"
        assert connections[4].terminal_pin == "5"
        assert connections[5].terminal_pin == "6"

    def test_terminal_pins_with_seeded_start(self, mapper):
        """Terminal pins should respect seeded start values."""
        mapper.set_terminal_start("X007", 5)
        mapper.sensor("TT-01", type="RTD", cable="W0001", terminal="X007")

        connections = mapper.generate_connections()
        assert connections[0].terminal_pin == "5"
        assert connections[1].terminal_pin == "6"
        assert connections[2].terminal_pin == "7"

    def test_different_terminals_independent_counters(self, mapper):
        """Different terminals should have independent pin counters."""
        mapper.sensor("TT-01", type="RTD", cable="W0001", terminal="X007")
        mapper.sensor("SW-01", type="DI_24V", cable="W0002", terminal="X008")

        connections = mapper.generate_connections()
        # X007 pins: 1, 2, 3 (RTD)
        rtd_conns = [c for c in connections if c.terminal == "X007"]
        assert rtd_conns[0].terminal_pin == "1"
        # X008 pins: 1 (DI)
        di_conns = [c for c in connections if c.terminal == "X008"]
        assert di_conns[0].terminal_pin == "1"


class TestGenerateConnections:
    def test_connection_fields(self, mapper):
        """Connection objects should have all expected fields."""
        mapper.sensor("PT-01-CX", type="2Wire-mA", cable="W0104", terminal="X007")

        connections = mapper.generate_connections()
        c = connections[0]
        assert c.sensor_tag == "PT-01-CX"
        assert c.cable == "W0104"
        assert c.terminal == "X007"
        assert c.terminal_pin == "1"
        assert c.module_name == "AI_mA_1"
        assert c.module_pin == "CH1+"
        assert c.sensor_pin == "Signal"

    def test_connections_table_format(self, mapper):
        """generate_connections_table() should return list of string lists."""
        mapper.sensor("PT-01", type="2Wire-mA", cable="W0001", terminal="X007")

        table = mapper.generate_connections_table()
        assert len(table) == 2
        assert all(isinstance(row, list) for row in table)
        assert all(isinstance(cell, str) for row in table for cell in row)
        assert len(table[0]) == 7  # 7 columns

    def test_module_naming_increments(self, mapper):
        """Module names should increment when capacity is exceeded."""
        # 3 RTD sensors, capacity=2 -> AI_RTD_1 (2 sensors) + AI_RTD_2 (1 sensor)
        mapper.sensor("TT-01", type="RTD", cable="W0001", terminal="X007")
        mapper.sensor("TT-02", type="RTD", cable="W0002", terminal="X007")
        mapper.sensor("TT-03", type="RTD", cable="W0003", terminal="X007")

        connections = mapper.generate_connections()
        # First 2 sensors -> AI_RTD_1
        assert connections[0].module_name == "AI_RTD_1"  # TT-01 pin 1
        assert connections[3].module_name == "AI_RTD_1"  # TT-02 pin 1
        # Third sensor -> AI_RTD_2
        assert connections[6].module_name == "AI_RTD_2"  # TT-03 pin 1

    def test_channel_resets_in_new_module(self, mapper):
        """Channel numbers should reset to 1 in a new module."""
        mapper.sensor("TT-01", type="RTD", cable="W0001", terminal="X007")
        mapper.sensor("TT-02", type="RTD", cable="W0002", terminal="X007")
        mapper.sensor("TT-03", type="RTD", cable="W0003", terminal="X007")

        connections = mapper.generate_connections()
        # TT-01 is channel 1 of module 1
        assert connections[0].module_pin == "CH1_R+"
        # TT-02 is channel 2 of module 1
        assert connections[3].module_pin == "CH2_R+"
        # TT-03 is channel 1 of module 2 (reset)
        assert connections[6].module_pin == "CH1_R+"

    def test_empty_mapper(self, mapper):
        """Empty mapper should produce no connections."""
        connections = mapper.generate_connections()
        assert connections == []

    def test_full_project_example(self, mapper):
        """Replicate the auxillary_cabinet_v3 sensor list."""
        mapper.set_terminal_start("X007", 1)
        mapper.sensor("TT-01-CX", type="RTD", cable="W0102", terminal="X007")
        mapper.sensor("TT-02-CX", type="RTD", cable="W0103", terminal="X007")
        mapper.sensor("PT-01-CX", type="2Wire-mA", cable="W0104", terminal="X007")
        mapper.sensor("PT-02-CX", type="2Wire-mA", cable="W0105", terminal="X007")
        mapper.sensor("LT-01-RX", type="2Wire-mA", cable="W0006", terminal="X007")
        mapper.sensor("TT-01-RX", type="RTD", cable="W0007", terminal="X007")
        mapper.sensor("TT-01-HX", type="RTD", cable="W0027", terminal="X007")

        connections = mapper.generate_connections()
        # 4 RTD sensors * 3 pins = 12 + 3 mA sensors * 2 pins = 6 = 18 connections total
        assert len(connections) == 18

        # Verify module allocation
        counts = mapper.module_count
        assert counts["AI_RTD"] == 2  # 4 RTD, capacity 2
        assert counts["AI_mA"] == 1   # 3 mA, capacity 4


class TestValidation:
    def test_unregistered_module_type_raises(self):
        """Registering a sensor type with unknown module should raise."""
        plc = PlcMapper()
        with pytest.raises(ValueError, match="Module type 'UNKNOWN'"):
            plc.sensor_type("bad", module="UNKNOWN", pins=["Signal"])

    def test_unregistered_sensor_type_raises(self):
        """Adding a sensor with unknown type should raise."""
        plc = PlcMapper()
        plc.module_type("DI", capacity=8, pin_format="DI{ch}")
        with pytest.raises(ValueError, match="Sensor type 'UNKNOWN'"):
            plc.sensor("SW-01", type="UNKNOWN", cable="W0001", terminal="X008")

    def test_chaining(self):
        """All registration methods should support chaining."""
        plc = (
            PlcMapper()
            .module_type("DI", capacity=8, pin_format="DI{ch}")
            .sensor_type("DI_24V", module="DI", pins=["Signal"])
            .sensor("SW-01", type="DI_24V", cable="W0001", terminal="X008")
            .set_terminal_start("X008", 5)
        )
        connections = plc.generate_connections()
        assert len(connections) == 1
        assert connections[0].terminal_pin == "5"
