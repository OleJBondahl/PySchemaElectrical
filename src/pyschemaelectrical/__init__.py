"""
PySchemaElectrical Library.
"""

from . import std_circuits
from .builder import BuildResult, CircuitBuilder, ComponentRef, PortRef
from .descriptors import build_from_descriptors, comp, ref, term
from .exceptions import (
    CircuitValidationError,
    ComponentNotFoundError,
    PortNotFoundError,
    TagReuseExhausted,
    WireLabelCountMismatch,
)
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
from .model.state import GenerationState, create_initial_state
from .system.connection_registry import export_registry_to_csv, get_registry
from .system.system import Circuit, add_symbol, render_system
from .terminal import Terminal
from .utils.autonumbering import create_autonumberer, get_tag_number, next_terminal_pins
from .utils.export_utils import export_terminal_list
from .utils.terminal_bridges import (
    BridgeRange,
    ConnectionDef,
    expand_range_to_pins,
    generate_internal_connections_data,
    get_connection_groups_for_terminal,
    parse_terminal_pins_from_csv,
    update_csv_with_internal_connections,
)
from .utils.utils import set_tag_counter, set_terminal_counter
from .wire import wire
