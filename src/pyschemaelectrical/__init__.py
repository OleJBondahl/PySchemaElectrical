"""
PySchemaElectrical Library.
"""

from .system.system import Circuit, render_system, add_symbol
from .builder import CircuitBuilder
from .utils.autonumbering import create_autonumberer, get_tag_number, next_terminal_pins
from .utils.utils import set_tag_counter, set_terminal_counter
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
)
from . import std_circuits
