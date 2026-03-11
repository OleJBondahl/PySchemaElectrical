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
    "INSTRUMENT_BUBBLE_RADIUS",
    "VALVE_SIZE",
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
PID_SIGNAL_DASH = "2,2"  # dash pattern for signal lines

# Symbol dimensions (mm)
INSTRUMENT_BUBBLE_RADIUS = GRID_SIZE * 2  # 10mm — ISA 5.1 instrument bubble radius
VALVE_SIZE = GRID_SIZE * 3  # 15mm — standard valve triangle size

# Spacing constants (mm)
PID_MIN_EQUIPMENT_GAP = GRID_SIZE * 4  # 20mm — minimum gap between equipment
PID_MIN_LEG_SPACING = GRID_SIZE * 10  # 50mm — minimum spacing between pipe legs
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
