"""
PySchemaElectrical Library.
"""

from .system.system import Circuit, add_symbol, render_system  # noqa: E402
from .builder import BuildResult, CircuitBuilder, ComponentRef, PortRef
from .utils.autonumbering import create_autonumberer, get_tag_number, next_terminal_pins
from .utils.utils import set_tag_counter, set_terminal_counter, get_terminal_counter
from .utils.export_utils import export_terminal_list
from .utils.terminal_bridges import (
    BridgeRange,
    ConnectionDef,
    expand_range_to_pins,
    get_connection_groups_for_terminal,
    generate_internal_connections_data,
    parse_terminal_pins_from_csv,
    update_csv_with_internal_connections,
)
from .system.connection_registry import get_registry, export_registry_to_csv
from .model.constants import (
    StandardSpacing,
    StandardTags,
    StandardPins,
    StandardCircuitKeys,
    SpacingConfig,
    PinSet,
    LayoutDefaults,
    CircuitLayoutConfig,
    CircuitLayouts,
)
from .model.state import create_initial_state, GenerationState
from .exceptions import (
    CircuitValidationError,
    PortNotFoundError,
    ComponentNotFoundError,
    TagReuseExhausted,
    TerminalReuseExhausted,
    WireLabelCountMismatch,
)
from .terminal import Terminal
from .wire import wire
from .descriptors import ref, comp, term, build_from_descriptors
from .plc import PlcMapper
from .project import Project
from . import std_circuits  # noqa: E402, I001 — must be last to avoid circular imports
