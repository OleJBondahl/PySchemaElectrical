"""
Device catalog for cross-domain instrument tracking.

Provides a single source of truth for devices that appear on both
P&ID and electrical drawings.
"""

from schematika.catalog.device import (  # noqa: F401
    CatalogDevice,
    ElectricalSpec,
    InstrumentSpec,
    ProcessSpec,
)
from schematika.catalog.registry import DeviceCatalog  # noqa: F401
