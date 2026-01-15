"""
Global constants for the IEC Symbol Library.
All geometric and stylistic parameters should be defined here.
Contains library-level defaults including spacing, tags, and pin configurations.
Project-specific constants (terminal IDs, paths) should be defined in user projects.
"""
from dataclasses import dataclass
from typing import Tuple

# Grid System
GRID_SIZE = 5.0  # mm, Base grid unit
GRID_SUBDIVISION = GRID_SIZE / 2 # 2.5mm, Half grid for smaller alignments

# Geometry
TERMINAL_RADIUS = 0.25 * GRID_SIZE # 1.25mm
LINE_WIDTH_THIN = 0.05 * GRID_SIZE # 0.25mm
LINE_WIDTH_THICK = 0.1 * GRID_SIZE # 0.5mm
LINKAGE_DASH_PATTERN = f"{0.4 * GRID_SIZE}, {0.4 * GRID_SIZE}" # "2.0, 2.0" Stippled/Dashed pattern

# Reference Symbol Geometry
REF_ARROW_LENGTH = 3 * GRID_SUBDIVISION # 7.5mm
REF_ARROW_HEAD_LENGTH = 0.4 * GRID_SIZE # 2.0mm
REF_ARROW_HEAD_WIDTH = 0.32 * GRID_SIZE # 1.6mm

# Text & Fonts
TEXT_FONT_FAMILY="Times New Roman"
TEXT_SIZE_MAIN = GRID_SIZE # 5.0mm
TEXT_OFFSET_X = -GRID_SIZE # -5.0mm

TEXT_FONT_FAMILY_AUX = "sans-serif"
TEXT_SIZE_PIN = 0.7 * GRID_SIZE # 3.5mm
PIN_LABEL_OFFSET_X = 0.3 * GRID_SIZE # 1.5mm
PIN_LABEL_OFFSET_Y_ADJUST = 0.0 # mm, adjustment for up/down ports

# Layout
DEFAULT_POLE_SPACING = 2 * GRID_SIZE # 10.0mm
DEFAULT_WIRE_ALIGNMENT_TOLERANCE = 0.2 * GRID_SIZE # 1.0mm

# Colors
COLOR_BLACK = "black"
COLOR_WHITE = "white"

# Document Defaults
DEFAULT_DOC_WIDTH = "210mm"
DEFAULT_DOC_HEIGHT = "297mm"


@dataclass(frozen=True)
class SpacingConfig:
    """
    Spacing configuration for a circuit type.
    
    Attributes:
        circuit_spacing: Distance between adjacent circuits in mm
        symbols_start_x: X-coordinate where symbols begin in mm
        symbols_spacing: Distance between symbols within a circuit in mm
    """
    circuit_spacing: float
    symbols_start_x: float
    symbols_spacing: float


class StandardSpacing:
    """Standard spacing configurations for different circuit types."""
    
    MOTOR = SpacingConfig(
        circuit_spacing=30 * GRID_SIZE, # 150.0mm
        symbols_start_x=10 * GRID_SIZE, # 50.0mm
        symbols_spacing=12 * GRID_SIZE  # 60.0mm
    )
    
    SINGLE_POLE = SpacingConfig(
        circuit_spacing=20 * GRID_SIZE, # 100.0mm
        symbols_start_x=10 * GRID_SIZE, # 50.0mm
        symbols_spacing=12 * GRID_SIZE  # 60.0mm
    )
    
    POWER_DISTRIBUTION = SpacingConfig(
        circuit_spacing=16 * GRID_SIZE, # 80.0mm
        symbols_start_x=10 * GRID_SIZE, # 50.0mm
        symbols_spacing=8 * GRID_SIZE   # 40.0mm
    )


class StandardTags:
    """
    Standard IEC component tag prefixes.
    Following IEC 61346-2 designation standards.
    """
    BREAKER = "F"  # Protective devices (Fuses, Circuit Breakers)
    CONTACTOR = "Q"  # Power switching devices
    RELAY = "K"  # Auxiliary relays and contactors
    SWITCH = "S"  # Control switches
    POWER_SUPPLY = "PSU"  # Generators and power supplies
    TRANSFORMER = "T"  # Transformers
    MOTOR = "M"  # Motors
    INDICATOR = "H"  # Indicator lamps
    BUTTON = "S"  # Push buttons (same as switches)
    SENSOR = "B"  # Sensors and transducers
    TERMINAL = "X"  # Terminal blocks


@dataclass(frozen=True)
class PinSet:
    """
    Defines a set of related pins for a component.
    
    Attributes:
        pins: Tuple of pin names/numbers
        description: What this pin set represents
    """
    pins: Tuple[str, ...]
    description: str


class StandardPins:
    """Standard pin definitions for electrical components."""
    
    THREE_POLE = PinSet(
        pins=("L1", "T1", "L2", "T2", "L3", "T3"),
        description="Three-phase power connection (line/load pairs)"
    )
    
    THERMAL_OVERLOAD = PinSet(
        pins=("", "T1", "", "T2", "", "T3"),
        description="Thermal overload relay terminals (load side only)"
    )
    
    CURRENT_TRANSDUCER = PinSet(
        pins=("1", "2", "3", "4"),
        description="Current measurement transducer terminals"
    )
    
    # Common single pin identifiers
    L = 'L'  # Line
    N = 'N'  # Neutral
    PE = 'PE'  # Protective Earth
    V24 = '24V'  # 24V DC positive
    GND = 'GND'  # Ground / 0V


class StandardCircuitKeys:
    """
    Standard logical keys for terminal mapping.
    These provide common abstractions for circuit connections.
    """
    # Power distribution
    MAIN = 'MAIN'
    SUPPLY = 'SUPPLY'
    OUTPUT = 'OUTPUT'

    # Control power
    V24 = 'V24'
    GND = 'GND'

    # Generic I/O
    INPUT = 'INPUT'
    INPUT_1 = 'INPUT_1'
    INPUT_2 = 'INPUT_2'
    OUTPUT_24V = 'OUTPUT_24V'
    OUTPUT_GND = 'OUTPUT_GND'


# =============================================================================
# Layout Constants for std_circuits
# =============================================================================
# These constants define geometric layout values used in standard circuit creation.
# They are derived from GRID_SIZE for consistency.

class LayoutDefaults:
    """
    Default layout values for standard circuits.
    All values are in mm and relate to GRID_SIZE for consistency.
    """
    # Circuit spacing (horizontal distance between circuit instances)
    CIRCUIT_SPACING_MOTOR = 30 * GRID_SIZE       # 150.0mm Motor circuits (3-pole, wider)
    CIRCUIT_SPACING_POWER = 30 * GRID_SIZE       # 150.0mm Power distribution circuits
    CIRCUIT_SPACING_CONTROL = 20 * GRID_SIZE     # 100.0mm Control circuits (single-pole, narrower)
    CIRCUIT_SPACING_SINGLE_POLE = 20 * GRID_SIZE # 100.0mm Single-pole circuits

    # Symbol spacing (vertical distance between components within a circuit)
    SYMBOL_SPACING_DEFAULT = 10 * GRID_SIZE       # 50.0mm Default builder value
    SYMBOL_SPACING_STANDARD = 12 * GRID_SIZE      # 60.0mm Standard spacing for most circuits

    # Horizontal offsets (for positioning parallel components)
    # PSU terminal pairs (L/N at top, 24V/GND at bottom)
    PSU_TERMINAL_OFFSET = 3 * GRID_SIZE          # 15.0mm ±15mm from center for L/N and 24V/GND pairs

    # Changeover switch terminal offsets
    CHANGEOVER_TERMINAL_OFFSET = GRID_SIZE * 4  # ±20mm (4 grid units) for main/EM inputs

    # Control circuit column offset
    CONTROL_COLUMN_OFFSET = GRID_SIZE * 6       # 30mm (6 grid units) for feedback column

    # Composition offsets (for combining multiple circuits)
    VOLTAGE_MONITOR_OFFSET = 10 * GRID_SIZE       # 50.0mm Offset after changeover circuits
    PSU_LAYOUT_OFFSET = 5 * GRID_SIZE            # 25.0mm Offset after voltage monitor


@dataclass(frozen=True)
class CircuitLayoutConfig:
    """
    Complete layout configuration for a circuit type.
    Projects can create custom configs or use the defaults.
    """
    circuit_spacing: float
    symbol_spacing: float
    terminal_offset: float = 0.0        # Horizontal offset for terminal pairs
    column_offset: float = 0.0          # Offset for secondary columns


class CircuitLayouts:
    """Pre-configured layout configurations for standard circuit types."""

    PSU = CircuitLayoutConfig(
        circuit_spacing=LayoutDefaults.CIRCUIT_SPACING_POWER,
        symbol_spacing=LayoutDefaults.SYMBOL_SPACING_STANDARD,
        terminal_offset=LayoutDefaults.PSU_TERMINAL_OFFSET
    )

    CHANGEOVER = CircuitLayoutConfig(
        circuit_spacing=LayoutDefaults.CIRCUIT_SPACING_POWER,
        symbol_spacing=LayoutDefaults.SYMBOL_SPACING_STANDARD,
        terminal_offset=LayoutDefaults.CHANGEOVER_TERMINAL_OFFSET
    )

    DOL_STARTER = CircuitLayoutConfig(
        circuit_spacing=LayoutDefaults.CIRCUIT_SPACING_MOTOR,
        symbol_spacing=LayoutDefaults.SYMBOL_SPACING_DEFAULT
    )

    MOTOR_CONTROL = CircuitLayoutConfig(
        circuit_spacing=LayoutDefaults.CIRCUIT_SPACING_CONTROL,
        symbol_spacing=LayoutDefaults.SYMBOL_SPACING_DEFAULT,
        column_offset=LayoutDefaults.CONTROL_COLUMN_OFFSET
    )

    SWITCH = CircuitLayoutConfig(
        circuit_spacing=LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE,
        symbol_spacing=LayoutDefaults.SYMBOL_SPACING_STANDARD
    )

    EMERGENCY_STOP = CircuitLayoutConfig(
        circuit_spacing=LayoutDefaults.CIRCUIT_SPACING_SINGLE_POLE,
        symbol_spacing=LayoutDefaults.SYMBOL_SPACING_DEFAULT
    )
