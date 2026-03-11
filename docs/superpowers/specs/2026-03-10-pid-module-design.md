# Design: P&ID Module for Schematika

**Date:** 2026-03-10
**Status:** Approved
**Scope:** Add P&ID (Piping & Instrumentation Diagram) support to Schematika

## Problem

Schematika generates electrical schematic diagrams but cannot produce P&ID drawings. Engineers working with industrial automation systems (e.g., cooling systems controlled by electrical cabinets) need both drawing types. Instruments like temperature transmitters appear on both the P&ID (connected to a pipe) and the electrical schematic (wired to a PLC input). Currently, there's no way to maintain cross-referencing between these drawings.

## Solution

Expand the library into **Schematika** — a unified engineering documentation library with two peer domain modules sharing common infrastructure:

- `schematika.electrical` — IEC 60617 electrical schematics (existing functionality)
- `schematika.pid` — ISO 14617 + ISA 5.1 P&ID diagrams (new)
- `schematika.catalog` — Cross-domain device registry (new)
- `schematika.core` — Shared geometry, rendering, state threading (extracted from existing code)

## Architecture

### Package Structure

```
src/schematika/
    core/                           # Shared infrastructure
        geometry.py                 # Point, Vector, Style, Element
        primitives.py               # Line, Circle, Text, Path, Group, Polygon
        symbol.py                   # Symbol, Port, SymbolFactory
        parts.py                    # standard_text, multipole, terminal_circle, box
        state.py                    # GenerationState, create_initial_state
        transform.py                # translate, rotate
        renderer.py                 # SVG render_to_svg
        autonumbering.py            # next_tag, next_terminal_pins
        exceptions.py               # Shared exception hierarchy

    electrical/                     # IEC 60617 (existing, reorganized)
        constants.py, symbols/, builder.py, descriptors.py,
        circuit.py, connection_registry.py, layout.py, wire_labels.py,
        terminal.py, wire.py, field_devices.py, internal_device.py,
        plc_resolver.py, cable_export.py, export_utils.py,
        terminal_bridges.py, system_analysis.py

    pid/                            # ISO 14617 + ISA 5.1 (new)
        constants.py                # PID grid, line weights, ISA letter codes
        symbols/
            process.py              # centrifugal_pump, positive_displacement_pump
            vessels.py              # tank, heat_exchanger
            valves.py               # gate_valve, control_valve, check_valve, ball_valve
            instruments.py          # instrument_bubble (ISA 5.1)
            piping.py               # pipe_segment, reducer, tee, cap
        builder.py                  # PIDBuilder (named-graph model)
        diagram.py                  # PIDDiagram container
        layout.py                   # Flow-based placement + pipe routing
        connections.py              # PipeStyle, Manhattan routing

    catalog/                        # Cross-domain device registry
        device.py                   # CatalogDevice, InstrumentSpec, ProcessSpec, ElectricalSpec
        registry.py                 # DeviceCatalog

    project.py                      # Extended Project (both page types)
    rendering/typst/                # Shared PDF compilation
```

### PIDBuilder: Named Graph Model

CircuitBuilder uses a linear chain model that struggles with 2D placement. PIDBuilder uses **named references** and **port-to-port alignment**:

```python
builder = PIDBuilder(state)
builder.add_equipment("tank", tank, "T", x=50, y=100)
builder.add_equipment("pump", centrifugal_pump, "P",
                      relative_to="tank", from_port="outlet", to_port="inlet")
builder.add_equipment("hx", heat_exchanger, "HX",
                      relative_to="pump", from_port="outlet", to_port="shell_in")
builder.add_instrument("tt101", "TT", on_equipment="hx", on_port="shell_out")
builder.pipe("tank", "pump", line_spec="2-CW-101")
builder.pipe("pump", "hx")
builder.signal_line("tt101", "dcs_panel")
result = builder.build()
```

**Why this is better:**
- Named refs (`"tank"`) instead of integer indices
- Port-to-port alignment instead of above/below/offset fields
- Explicit pipe declarations instead of implicit auto-connect
- Graph topology — branches and loops are natural

### Device Catalog

Single source of truth for instruments appearing on both drawings:

```python
catalog = DeviceCatalog()
catalog.register(CatalogDevice(
    tag="TT-101",
    description="CW supply temperature",
    process=ProcessSpec(
        instrument=InstrumentSpec("TT", "101", "field"),
        service="Cooling water supply",
        range="0-100°C",
        output="4-20mA",
    ),
    electrical=ElectricalSpec(
        terminal="X100",
        pins=(PinDef("Sig+", SIGNAL), PinDef("GND", SIGNAL)),
        device_template=SENSOR_4_20MA,
    ),
))

# P&ID side
pid_builder.add_instrument("tt101", catalog=catalog, device_tag="TT-101",
                           on_equipment="pipe_section_1")

# Electrical side
project.field_devices(catalog.generate_field_connections())
```

### P&ID Symbol Conventions

| Category | Port IDs | Standard |
|----------|----------|----------|
| Equipment (pumps, tanks) | `"inlet"`, `"outlet"`, `"drain"`, `"vent"` | ISO 14617 |
| Valves | `"in"`, `"out"`, `"actuator"` | ISO 14617 |
| Instruments | `"process"`, `"signal_out"` | ISA 5.1 |

### Pipes vs Wires

| Aspect | Electrical Wire | P&ID Pipe |
|--------|----------------|-----------|
| Line weight | 0.25mm | 0.7mm |
| Direction | Implicit (top-down) | Explicit (flow arrows) |
| Routing | Vertical auto-connect | Manhattan routing (horizontal-first) |
| Signal lines | N/A | Dashed (0.35mm) |

### Symbol Verification

Test-only approach with geometric assertions:

```python
def test_centrifugal_pump_geometry():
    sym = centrifugal_pump("P-001")
    bbox = compute_bounding_box(sym)
    assert bbox.width == pytest.approx(20.0, abs=0.5)
    assert "inlet" in sym.ports
    assert "outlet" in sym.ports
    assert sym.ports["inlet"].direction == Vector(-1, 0)
```

A `compute_bounding_box()` utility in `core/` supports this across both domains.

## Implementation Phases

1. **Core extraction** — Extract shared `core/` from `model/` + `utils/`
2. **Package rename** — renamed to `schematika`
3. **P&ID symbols** — ISO 14617 factories for cooling/HVAC scope
4. **PIDDiagram + pipe routing** — Container + Manhattan routing
5. **PIDBuilder** — Named-graph fluent builder
6. **Device Catalog** — Cross-domain registry
7. **Project integration** — Mixed electrical + P&ID projects
8. **Consumer migration** — Update auxillary_cabinet_v3

## Key Decisions

- **Standards:** ISO 14617 (symbols) + ISA 5.1 (instrument ID) for P&ID; IEC 60617 for electrical
- **Initial scope:** Cooling/HVAC systems (pumps, valves, heat exchangers, tanks, T/P/F sensors)
- **Library name:** Schematika (`pip install schematika`)
- **Symbol verification:** Test-only (geometric assertions in pytest)
- **Cross-reference:** Device Catalog pattern (central registry, both modules reference by tag)
- **Layout model:** Flow-based with relative placement (named-graph, port-to-port alignment)
- **Zero runtime dependencies:** Maintained
