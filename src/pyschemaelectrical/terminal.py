"""
Terminal type for PySchemaElectrical.

Provides a first-class `Terminal` type that replaces the string-based
terminal ID hack. Terminals carry metadata (description, bridge info,
reference flag) while being fully compatible with string operations
by inheriting from `str`.
"""

from typing import List, Optional, Tuple, Union

BridgeDef = Optional[Union[str, List[Tuple[int, int]]]]


class Terminal(str):
    """
    A terminal block definition with metadata.

    Terminals ARE strings (via inheritance) for full backwards compatibility
    with existing code that uses terminal IDs as plain strings.

    Args:
        id: Terminal identifier (e.g., "X001").
        description: Human-readable description (e.g., "Main 400V AC").
        bridge: Internal bridge definition. "all" for all pins bridged,
                list of (start, end) tuples for specific ranges, or None.
        reference: True for non-physical terminals (e.g., "PLC:DO").
                   Reference terminals are excluded from terminal reports.
    """

    __slots__ = ("description", "bridge", "reference")

    description: str
    bridge: BridgeDef
    reference: bool

    def __new__(
        cls,
        id: str,
        description: str = "",
        bridge: BridgeDef = None,
        reference: bool = False,
    ) -> "Terminal":
        instance = super().__new__(cls, id)
        object.__setattr__(instance, "description", description)
        object.__setattr__(instance, "bridge", bridge)
        object.__setattr__(instance, "reference", reference)
        return instance

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"Terminal is immutable, cannot set '{name}'")

    def __hash__(self) -> int:
        return str.__hash__(self)

    def __eq__(self, other: object) -> bool:
        return str.__eq__(self, str(other))
