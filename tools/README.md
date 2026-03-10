# Tools

Standalone utilities that complement PySchemaElectrical but live outside the main library (which has zero runtime dependencies).

## cad_parser

Parses existing CAD electrical drawings into a structured JSON format that an AI agent (or script) can use to recreate the schematic with PySchemaElectrical.

### Supported Formats

| Format | Extension | Parser | Required Package |
|--------|-----------|--------|-----------------|
| AutoCAD Electrical | `.dxf` | `AutocadParser` | `ezdxf` (MIT) |
| KiCad Schematic | `.kicad_sch` | `KicadParser` | `kiutils` (MIT) |
| SVG (CAD export) | `.svg` | `SvgParser` | stdlib only |
| PDF (CAD export) | `.pdf` | `PdfParser` | `PyMuPDF` (AGPL-3) |

AutoCAD `.dwg` files must first be converted to `.dxf` using the [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) (free).

### Installation

```bash
cd tools/cad_parser

# Install for AutoCAD DXF parsing
pip install -e ".[autocad]"

# Install for KiCad parsing
pip install -e ".[kicad]"

# Install everything
pip install -e ".[all]"
```

### CLI Usage

```bash
# Parse a DXF file, output JSON to stdout
python -m cad_parser drawing.dxf

# Parse and save to file
python -m cad_parser schematic.kicad_sch -o result.json

# Verbose logging (shows extraction details)
python -m cad_parser drawing.dxf -v

# Custom JSON indentation
python -m cad_parser drawing.dxf --indent 4
```

### Python API

```python
from cad_parser import parse_file

# Auto-detects format by extension
data = parse_file("drawing.dxf")

# Access structured data
for comp in data.components:
    print(f"{comp.tag}: {comp.type} ({comp.family})")
    print(f"  Position: ({comp.position.x}, {comp.position.y})")
    print(f"  Terminals: {comp.terminals}")

for wire in data.wires:
    print(f"{wire.id}: {wire.wire_number}")
    if wire.from_endpoint:
        print(f"  From: {wire.from_endpoint.component}:{wire.from_endpoint.pin}")
    if wire.to_endpoint:
        print(f"  To: {wire.to_endpoint.component}:{wire.to_endpoint.pin}")

for net in data.nets:
    members = ", ".join(f"{m.component}:{m.pin}" for m in net.members)
    print(f"Net {net.name}: {members}")

# Export as JSON
print(data.to_json())
```

### Output Format

All parsers produce a unified `SchematicData` structure:

```json
{
  "metadata": {
    "source_format": "autocad_dxf",
    "filename": "motor_starter.dxf",
    "pages": 1
  },
  "components": [
    {
      "tag": "K1",
      "type": "contactor",
      "family": "CR",
      "description": "Main contactor",
      "position": {"x": 150.0, "y": 200.0},
      "terminals": {"TERM01": "1", "TERM02": "2"},
      "attributes": {"MFG": "Siemens", "_block_name": "HCR1"}
    }
  ],
  "wires": [
    {
      "id": "W1",
      "wire_number": "L1",
      "from_endpoint": {"component": "Q1", "pin": "2"},
      "to_endpoint": {"component": "K1", "pin": "1"},
      "segments": [
        {"start": {"x": 100.0, "y": 50.0}, "end": {"x": 100.0, "y": 150.0}}
      ]
    }
  ],
  "terminals": [
    {"strip": "X1", "pin": "1", "description": "Phase L1", "wire": "L1"}
  ],
  "nets": [
    {
      "name": "L1",
      "members": [
        {"component": "Q1", "pin": "2"},
        {"component": "K1", "pin": "1"}
      ]
    }
  ]
}
```

### How Each Parser Works

**AutoCAD DXF** (highest fidelity) — AutoCAD Electrical stores component data as named attributes on block INSERT entities (`TAG1`, `FAMILY`, `DESC1-3`, `TERM*`, `WIRENO`). The parser reads these directly, then traces `LINE` entities using union-find to build wire networks and associate wire numbers.

**KiCad** — Parses the S-expression `.kicad_sch` file via `kiutils`. Extracts symbol references, values, and properties. Wires are traced geometrically. If a sibling `.xml` netlist file exists (exported via `kicad-cli sch export netlist`), it is used for clean net connectivity.

**SVG** (best-effort) — Heuristic parser for CAD-exported SVGs. Detects wires from `<line>`/`<polyline>` elements, identifies component tags via regex on `<text>` elements, and uses `<g>` groups to cluster symbol geometry. Handles coordinate transforms. Less reliable than native format parsers.

**PDF** (best-effort) — Converts each page to SVG via PyMuPDF, then delegates to the SVG parser. Falls back to direct vector extraction (`page.get_drawings()`) on older PyMuPDF versions.

### Mapping to PySchemaElectrical

The extracted data maps to the library's API:

| Extracted Field | PySchemaElectrical Concept |
|----------------|---------------------------|
| `component.tag` (K1, Q3) | Component tag in `CircuitBuilder.add()` |
| `component.type` (contactor, motor) | Symbol factory selection |
| `component.terminals` | `Terminal()` objects with `pin_prefixes` |
| `wire.wire_number` (L1, 400) | Wire labels via `wire()` helper |
| `net.members` | Connection topology for `auto_connect` |

### Intended AI Agent Workflow

```
1. Engineer provides a CAD drawing (.dxf, .kicad_sch, .pdf, .svg)
2. cad_parser extracts structured JSON
3. AI agent reads the JSON output
4. Agent maps components → PySchemaElectrical symbol factories
5. Agent generates CircuitBuilder / build_from_descriptors() code
6. PySchemaElectrical renders the new SVG schematic
```

### Limitations

- **Connectivity from SVG/PDF** is approximate — based on geometric proximity, not semantic data
- **Pin positions** use the component's insertion point as a proxy (resolving actual pin geometry from block definitions is not implemented)
- **Wire networks** with 3+ connection points only track the first two endpoints in `from_endpoint`/`to_endpoint` (all connections are captured in `nets`)
- **KiCad pin-level connectivity** requires an exported XML netlist for full accuracy
- **AutoCAD DWG** files need conversion to DXF first (via ODA File Converter)
