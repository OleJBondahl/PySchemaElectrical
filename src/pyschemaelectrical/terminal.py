"""
Terminal type for PySchemaElectrical.

Provides a first-class `Terminal` dataclass that replaces the string-based
terminal ID hack. Terminals carry metadata (description, bridge info,
reference flag) while remaining backwards-compatible with string comparisons.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

BridgeDef = Optional[Union[str, List[Tuple[int, int]]]]


@dataclass(frozen=True)
class Terminal:
    """
    A terminal block definition with metadata.

    Terminals act as strings (via __str__, __eq__, __hash__) for backwards
    compatibility with existing code that uses terminal IDs as plain strings.

    Args:
        id: Terminal identifier (e.g., "X001").
        description: Human-readable description (e.g., "Main 400V AC").
        bridge: Internal bridge definition. "all" for all pins bridged,
                list of (start, end) tuples for specific ranges, or None.
        reference: True for non-physical terminals (e.g., "PLC:DO").
                   Reference terminals are excluded from terminal reports.
    """

    id: str
    description: str = ""
    bridge: BridgeDef = None
    reference: bool = False

    def __str__(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        return str(self) == str(other)
