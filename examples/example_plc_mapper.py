"""
Example: PLC I/O Mapping with PlcMapper.

Demonstrates the PlcMapper for declaring PLC module types, sensor types,
and sensor instances. The mapper auto-assigns sensors to module channels
and generates a connections table.

Run with:
    python -m examples.example_plc_mapper
"""

from pyschemaelectrical.plc import PlcMapper


def main():
    """Create a PLC I/O mapping for a small process system."""

    print("=" * 60)
    print("PySchemaElectrical — PLC Mapper Example")
    print("=" * 60)

    plc = PlcMapper()

    # ── Register module types ─────────────────────────────────
    plc.module_type("AI_RTD", capacity=2, pin_format="CH{ch}_{pin}")
    plc.module_type("AI_mA", capacity=4, pin_format="CH{ch}{polarity}")
    plc.module_type("DI", capacity=8, pin_format="DI{ch}")

    # ── Register sensor types ─────────────────────────────────
    plc.sensor_type("RTD", module="AI_RTD", pins=["R+", "RL", "R-"])
    plc.sensor_type(
        "2Wire-mA",
        module="AI_mA",
        pins=["Signal", "GND"],
        polarity={0: "+", 1: "-"},
    )
    plc.sensor_type("ProxSwitch", module="DI", pins=["Signal"])

    # ── Add sensor instances ──────────────────────────────────
    plc.sensor("TT-01", type="RTD", cable="W0101", terminal="X007")
    plc.sensor("TT-02", type="RTD", cable="W0102", terminal="X007")
    plc.sensor("PT-01", type="2Wire-mA", cable="W0201", terminal="X008")
    plc.sensor("PT-02", type="2Wire-mA", cable="W0202", terminal="X008")
    plc.sensor("LS-01", type="ProxSwitch", cable="W0301", terminal="X009")
    plc.sensor("LS-02", type="ProxSwitch", cable="W0302", terminal="X009")

    # ── Generate connections ──────────────────────────────────
    connections = plc.generate_connections()

    print(f"\nTotal connections: {len(connections)}")
    print(f"Modules needed:   {plc.module_count}")
    print()

    # Print connections table
    header = f"{'Module':<12} {'Pin':<12} {'Sensor':<10} {'Cable':<8} {'Terminal':<10} {'T.Pin':<6} {'S.Pin':<8}"
    print(header)
    print("-" * len(header))
    for conn in connections:
        print(
            f"{conn.module_name:<12} {conn.module_pin:<12} "
            f"{conn.sensor_tag:<10} {conn.cable:<8} "
            f"{conn.terminal:<10} {conn.terminal_pin:<6} {conn.sensor_pin:<8}"
        )

    # Generate CSV table
    table = plc.generate_connections_table()
    print(f"\nCSV table ({len(table)} rows including header)")


if __name__ == "__main__":
    main()
