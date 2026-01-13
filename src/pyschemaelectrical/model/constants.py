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
GRID_SUBDIVISION = 2.5 # mm, Half grid for smaller alignments

# Geometry
TERMINAL_RADIUS = 1.25 # mm
LINE_WIDTH_THIN = 0.25 # mm
LINE_WIDTH_THICK = 0.5 # mm
LINKAGE_DASH_PATTERN = "2, 2" # Stippled/Dashed pattern for mechanical linkages (2mm dash, 2mm gap)

# Text & Fonts
TEXT_FONT_FAMILY="Times New Roman"
TEXT_SIZE_MAIN = 5.0 # For component tags like K1, X1
TEXT_OFFSET_X = -5.0 # mm, default label offset from symbol center

TEXT_FONT_FAMILY_AUX = "sans-serif"
TEXT_SIZE_PIN = 3.5 # For pin numbers like 13, 14
PIN_LABEL_OFFSET_X = 1.5 # mm, distance from port
PIN_LABEL_OFFSET_Y_ADJUST = 0.0 # mm, adjustment for up/down ports

# Layout
DEFAULT_POLE_SPACING = 10.0 # mm, 2 * GRID_SIZE
DEFAULT_WIRE_ALIGNMENT_TOLERANCE = 1.0 # mm

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
        circuit_spacing=150.0,
        symbols_start_x=50.0,
        symbols_spacing=60.0
    )
    
    SINGLE_POLE = SpacingConfig(
        circuit_spacing=100.0,
        symbols_start_x=50.0,
        symbols_spacing=60.0
    )
    
    POWER_DISTRIBUTION = SpacingConfig(
        circuit_spacing=80.0,
        symbols_start_x=50.0,
        symbols_spacing=40.0
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
    POWER_SUPPLY = "G"  # Generators and power supplies
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
