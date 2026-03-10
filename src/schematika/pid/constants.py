"""
P&ID-specific constants following ISO 14617 and ISA 5.1 standards.
"""

# Line weights (mm)
PID_LINE_WEIGHT = 0.7  # process pipe line weight
PID_SIGNAL_LINE_WEIGHT = 0.35  # signal/instrument line weight
PID_SIGNAL_DASH = "2,2"  # dash pattern for signal lines

# Symbol dimensions (mm)
INSTRUMENT_BUBBLE_RADIUS = 10.0  # ISA 5.1 instrument bubble radius
VALVE_SIZE = 15.0  # standard valve triangle size
EQUIPMENT_SCALE = 1.0  # base scale factor

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
