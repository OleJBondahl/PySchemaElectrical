"""Re-export shim: actual code lives in pyschemaelectrical.core.exceptions."""

from pyschemaelectrical.core.exceptions import (  # noqa: F401
    CircuitValidationError,
    ComponentNotFoundError,
    PortNotFoundError,
    TagReuseError,
    TagReuseExhausted,
    TerminalReuseError,
    TerminalReuseExhausted,
    WireLabelCountMismatch,
    WireLabelMismatchError,
)
