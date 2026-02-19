"""
PySchemaElectrical Library.
"""

from . import std_circuits  # noqa: E402, I001 — must be last to avoid circular imports
from .builder import BuildResult, CircuitBuilder, ComponentRef, PortRef
from .descriptors import build_from_descriptors, comp, ref, term
from .exceptions import (
    CircuitValidationError,
    ComponentNotFoundError,
    PortNotFoundError,
    TagReuseError,
    # Backward-compatible aliases (deprecated)
    TagReuseExhausted,
    TerminalReuseError,
    TerminalReuseExhausted,
    WireLabelCountMismatch,
    WireLabelMismatchError,
)
from .field_devices import DeviceTemplate, PinDef, generate_field_connections
from .model.constants import (
    CircuitLayoutConfig,
    CircuitLayouts,
    LayoutDefaults,
    PinSet,
    SpacingConfig,
    StandardCircuitKeys,
    StandardPins,
    StandardSpacing,
    StandardTags,
)
from .model.core import SymbolFactory
from .model.state import GenerationState, create_initial_state
from .plc import PlcMapper
from .project import Project
from .system.connection_registry import export_registry_to_csv, get_registry
from .system.system import (  # noqa: E402
    Circuit,
    add_symbol,
    merge_circuits,
    render_system,
)
from .terminal import Terminal
from .utils.autonumbering import create_autonumberer, get_tag_number, next_terminal_pins
from .utils.export_utils import (
    export_terminal_list,
    finalize_terminal_csv,
    merge_terminal_csv,
)
from .utils.terminal_bridges import (
    BridgeRange,
    ConnectionDef,
    expand_range_to_pins,
    generate_internal_connections_data,
    get_connection_groups_for_terminal,
    parse_terminal_pins_from_csv,
    update_csv_with_internal_connections,
)
from .utils.utils import (
    apply_start_indices,
    fixed_tag,
    get_terminal_counter,
    merge_terminals,
    set_tag_counter,
    set_terminal_counter,
)
from .wire import wire
