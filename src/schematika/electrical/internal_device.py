"""Internal device definition for BOM tracking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InternalDevice:
    """Metadata for an internal cabinet component.

    Used to associate MPN and description with tag prefixes for
    Bill of Materials generation.

    Attributes:
        prefix: Tag prefix for autonumbering (e.g., "Q", "K", "F").
        mpn: Manufacturer part number (e.g., "LC1D09").
        description: Human-readable description (e.g., "Contactor 9A").
    """

    prefix: str
    mpn: str
    description: str
