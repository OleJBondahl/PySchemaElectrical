
"""
Global constants for the IEC Symbol Library.
All geometric and stylistic parameters should be defined here.
"""

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
