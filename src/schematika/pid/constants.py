"""
P&ID-specific constants following ISO 14617 and ISA 5.1 standards.

All dimensional constants are derived from the core grid system to stay
consistent with electrical schematic proportions.
"""

from schematika.core.constants import (
    GRID_SIZE,
    LINE_WIDTH_THIN,
    TEXT_FONT_FAMILY,
    TEXT_SIZE_MAIN,
)

__all__ = [
    "GRID_SIZE",
    "LINE_WIDTH_THIN",
    "TEXT_FONT_FAMILY",
    "TEXT_SIZE_MAIN",
    "PID_EQUIPMENT_STROKE",
    "PID_LINE_WEIGHT",
    "PID_SIGNAL_LINE_WEIGHT",
    "PID_SIGNAL_DASH",
    "PID_PNEUMATIC_DASH",
    "PID_OPEN_TANK_DASH",
    "INSTRUMENT_BUBBLE_RADIUS",
    "VALVE_SIZE",
    "PID_STUB_LENGTH",
    "PID_PUMP_RADIUS",
    "PID_TANK_HALF_WIDTH",
    "PID_TANK_HALF_HEIGHT",
    "PID_HX_RADIUS",
    "PID_VALVE_CENTER_RADIUS",
    "PID_VALVE_BALL_RADIUS",
    "PID_ACTUATOR_STEM_HEIGHT",
    "PID_ACTUATOR_TRI_HEIGHT",
    "PID_TEXT_SIZE_BUBBLE",
    "PID_TEXT_SIZE_TAG",
    "PID_TEXT_SIZE_PIPE",
    "PID_TAG_OFFSET",
    "PID_LABEL_PIPE_OFFSET",
    "PID_TEE_HALF_LENGTH",
    "PID_TEE_BRANCH_LENGTH",
    "PID_REDUCER_LENGTH",
    "PID_REDUCER_INLET_HALF_H",
    "PID_REDUCER_OUTLET_HALF_H",
    "PID_CAP_HALF_HEIGHT",
    "PID_HX_TUBE_OFFSET",
    "PID_HX_TUBE_LENGTH_FACTOR",
    "PID_FLOW_ARROW_SIZE",
    "PID_DEFAULT_PIPE_LENGTH",
    "PID_MIN_EQUIPMENT_GAP",
    "PID_MIN_LEG_SPACING",
    "PID_LABEL_OFFSET",
    "ISA_FIRST_LETTER",
    "ISA_SUCCEEDING_LETTERS",
]

# Line weights (mm)
PID_EQUIPMENT_STROKE = GRID_SIZE * 0.1  # 0.5mm — valve bodies, pump circles, tanks
PID_LINE_WEIGHT = GRID_SIZE * 7 / 50  # 0.7mm — process pipes
PID_SIGNAL_LINE_WEIGHT = LINE_WIDTH_THIN  # 0.25mm — signal/instrument lines

# Dash patterns (grid-relative)
PID_SIGNAL_DASH = f"{GRID_SIZE * 0.4},{GRID_SIZE * 0.4}"
PID_PNEUMATIC_DASH = (
    f"{GRID_SIZE * 0.2},{GRID_SIZE * 0.6},{GRID_SIZE},{GRID_SIZE * 0.6}"
)
PID_OPEN_TANK_DASH = f"{GRID_SIZE * 0.6},{GRID_SIZE * 0.4}"

# Symbol dimensions (mm) — ISA 5.1 / ISO 14617 compliant
INSTRUMENT_BUBBLE_RADIUS = GRID_SIZE * 1.2  # 6mm radius → 12mm diameter (ISA 5.1)
VALVE_SIZE = GRID_SIZE * 2  # 10mm valve triangle size
PID_STUB_LENGTH = GRID_SIZE  # 5mm pipe stub connecting ports to body
PID_PUMP_RADIUS = GRID_SIZE * 2  # 10mm pump circle radius (20mm diameter)
PID_TANK_HALF_WIDTH = GRID_SIZE * 3  # 15mm (30mm total tank width)
PID_TANK_HALF_HEIGHT = GRID_SIZE * 4  # 20mm (40mm total tank height)
PID_HX_RADIUS = GRID_SIZE * 2.5  # 12.5mm heat exchanger radius

# Valve sub-component dimensions
PID_VALVE_CENTER_RADIUS = GRID_SIZE * 0.3  # 1.5mm globe/control center circle
PID_VALVE_BALL_RADIUS = GRID_SIZE * 0.5  # 2.5mm ball valve indicator
PID_ACTUATOR_STEM_HEIGHT = GRID_SIZE * 1.6  # 8mm actuator stem
PID_ACTUATOR_TRI_HEIGHT = GRID_SIZE * 0.8  # 4mm actuator triangle

# Text sizes (mm) — ISA 5.1 / ISO 3098
PID_TEXT_SIZE_BUBBLE = GRID_SIZE * 0.5  # 2.5mm letters inside instrument bubbles
PID_TEXT_SIZE_TAG = GRID_SIZE * 0.5  # 2.5mm equipment/instrument tags
PID_TEXT_SIZE_PIPE = GRID_SIZE * 0.5  # 2.5mm pipe labels

# Text/label offsets
PID_TAG_OFFSET = GRID_SIZE * 0.8  # 4mm tag number below bubble
PID_LABEL_PIPE_OFFSET = GRID_SIZE * 0.4  # 2mm label above pipe centerline

# Piping element dimensions
PID_TEE_HALF_LENGTH = GRID_SIZE * 2  # 10mm tee horizontal half-span
PID_TEE_BRANCH_LENGTH = GRID_SIZE * 2  # 10mm tee branch length
PID_REDUCER_LENGTH = GRID_SIZE * 2  # 10mm reducer horizontal span
PID_REDUCER_INLET_HALF_H = GRID_SIZE  # 5mm reducer inlet half-height
PID_REDUCER_OUTLET_HALF_H = GRID_SIZE * 0.5  # 2.5mm reducer outlet half-height
PID_CAP_HALF_HEIGHT = GRID_SIZE * 0.6  # 3mm cap bar half-height

# HX internals
PID_HX_TUBE_OFFSET = GRID_SIZE * 0.7  # 3.5mm tube pass line offset from center
PID_HX_TUBE_LENGTH_FACTOR = 0.6  # tube pass line = 60% of radius (ratio, not mm)

# Flow arrow
PID_FLOW_ARROW_SIZE = GRID_SIZE * 0.6  # 3mm flow direction arrow half-size

# Default pipe segment length
PID_DEFAULT_PIPE_LENGTH = GRID_SIZE * 10  # 50mm

# Spacing constants (mm)
PID_MIN_EQUIPMENT_GAP = GRID_SIZE * 6  # 30mm — minimum gap between equipment
PID_MIN_LEG_SPACING = GRID_SIZE * 8  # 40mm — minimum spacing between pipe legs
PID_LABEL_OFFSET = GRID_SIZE  # 5mm — label offset from symbol edge

# ISA 5.1 letter code lookup tables
ISA_FIRST_LETTER = {
    "A": "Analysis",
    "B": "Burner/Combustion",
    "C": "Conductivity",
    "D": "Density",
    "E": "Voltage",
    "F": "Flow",
    "G": "Gauging",
    "H": "Hand",
    "I": "Current",
    "J": "Power",
    "K": "Time",
    "L": "Level",
    "M": "Moisture",
    "N": "User Choice",
    "O": "User Choice",
    "P": "Pressure",
    "Q": "Quantity",
    "R": "Radiation",
    "S": "Speed",
    "T": "Temperature",
    "U": "Multivariable",
    "V": "Vibration",
    "W": "Weight",
    "X": "Unclassified",
    "Y": "Event/State",
    "Z": "Position",
}

ISA_SUCCEEDING_LETTERS = {
    "A": "Alarm",
    "C": "Controller",
    "E": "Element",
    "G": "Glass/Gauge",
    "H": "High",
    "I": "Indicator",
    "K": "Control Station",
    "L": "Low",
    "N": "User Choice",
    "O": "Orifice",
    "P": "Point",
    "R": "Recorder",
    "S": "Switch",
    "T": "Transmitter",
    "V": "Valve",
    "X": "Unclassified",
    "Y": "Relay/Compute",
    "Z": "Driver/Actuator",
}
