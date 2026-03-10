"""Re-export shim: actual code lives in schematika.core.autonumbering."""

from schematika.core.autonumbering import (  # noqa: F401
    create_autonumberer,
    get_tag_number,
    next_tag,
    next_terminal_pins,
    resolve_terminal_pins,
)
from schematika.electrical.utils.utils import (  # noqa: F401
    get_terminal_counter as get_terminal_counter,
)
from schematika.electrical.utils.utils import (  # noqa: F401
    set_terminal_counter as set_terminal_counter,
)
