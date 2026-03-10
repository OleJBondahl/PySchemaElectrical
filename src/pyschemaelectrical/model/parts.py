"""Re-export shim: actual code lives in pyschemaelectrical.core.parts."""

# Re-export constants that were previously importable from model.parts
# (they originated in model.constants but were imported at module level there)
from pyschemaelectrical.model.constants import (  # noqa: F401
    PIN_LABEL_OFFSET_X,
    PIN_LABEL_OFFSET_Y_ADJUST,
    TEXT_FONT_FAMILY_AUX,
    TEXT_SIZE_PIN,
)
from pyschemaelectrical.core.parts import (  # noqa: F401
    _add_remapped_ports,
    box,
    create_extended_blade,
    create_pin_label_text,
    create_pin_labels,
    multipole,
    pad_pins,
    standard_style,
    standard_text,
    terminal_circle,
    terminal_text,
    three_pole_factory,
    two_pole_factory,
)
