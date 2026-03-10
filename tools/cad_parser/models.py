from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

# Mutable by design: parsers build these incrementally (appending to lists, etc.)
# Returned SchematicData should be treated as finalized output by consumers.


@dataclass
class Position:
    x: float
    y: float


@dataclass
class ComponentInfo:
    tag: str
    type: str
    family: str
    description: str
    position: Position
    terminals: dict[str, str] = field(default_factory=dict)
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class WireSegment:
    start: Position
    end: Position


@dataclass
class WireEndpoint:
    component: str
    pin: str


@dataclass
class WireInfo:
    id: str
    wire_number: str
    from_endpoint: WireEndpoint | None
    to_endpoint: WireEndpoint | None
    segments: list[WireSegment] = field(default_factory=list)


@dataclass
class TerminalInfo:
    strip: str
    pin: str
    description: str
    wire: str


@dataclass
class NetMember:
    component: str
    pin: str


@dataclass
class NetInfo:
    name: str
    members: list[NetMember] = field(default_factory=list)


@dataclass
class Metadata:
    source_format: str
    filename: str
    pages: int


@dataclass
class SchematicData:
    metadata: Metadata
    components: list[ComponentInfo] = field(default_factory=list)
    wires: list[WireInfo] = field(default_factory=list)
    terminals: list[TerminalInfo] = field(default_factory=list)
    nets: list[NetInfo] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
