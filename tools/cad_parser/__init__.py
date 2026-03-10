from __future__ import annotations

from pathlib import Path

from .models import (
    ComponentInfo,
    Metadata,
    NetInfo,
    NetMember,
    Position,
    SchematicData,
    TerminalInfo,
    WireEndpoint,
    WireInfo,
    WireSegment,
)

__all__ = [
    "ComponentInfo",
    "Metadata",
    "NetInfo",
    "NetMember",
    "Position",
    "SchematicData",
    "TerminalInfo",
    "WireEndpoint",
    "WireInfo",
    "WireSegment",
    "parse_file",
]


def parse_file(path: str | Path) -> SchematicData:
    """Dispatch to the appropriate parser based on file extension.

    Supported extensions:
      .dxf  — AutoCAD Electrical (requires ezdxf)
      .kicad_sch — KiCad schematic (requires kiutils/kinparse)
      .pdf  — PDF schematic (requires PyMuPDF)
      .svg  — SVG schematic (requires svgpathtools/lxml)
    """
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".dxf":
        from .parsers.autocad import AutocadParser  # noqa: PLC0415

        return AutocadParser().parse(p)
    elif ext == ".kicad_sch":
        from .parsers.kicad import KicadParser  # noqa: PLC0415

        return KicadParser().parse(p)
    elif ext == ".pdf":
        from .parsers.pdf import PdfParser  # noqa: PLC0415

        return PdfParser().parse(p)
    elif ext == ".svg":
        from .parsers.svg import SvgParser  # noqa: PLC0415

        return SvgParser().parse(p)
    else:
        raise ValueError(
            f"Unsupported file extension: {ext!r}. "
            "Supported: .dxf, .kicad_sch, .pdf, .svg"
        )
