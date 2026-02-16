"""
Typed state for circuit generation.

Provides type-safe state management for the CircuitBuilder and
related generation functions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Union

# Avoid direct import if circular dependency is feared, but verified safe here.
from pyschemaelectrical.system.connection_registry import TerminalRegistry


@dataclass
class GenerationState:
    """
    Immutable state container for circuit generation.

    Attributes:
        tags: Counter for component tags (e.g., {"K": 3} means next K is K4)
        terminal_counters: Counter for terminal numbering per terminal block
        contact_channels: Counter for contact channel assignment
        terminal_registry: Registry of terminal connections
        pin_counter: Global pin counter (legacy)
    """

    tags: Dict[str, int] = field(default_factory=dict)
    terminal_counters: Dict[str, int] = field(default_factory=dict)
    contact_channels: Dict[str, int] = field(default_factory=dict)
    terminal_registry: Union[TerminalRegistry, Dict] = field(
        default_factory=TerminalRegistry
    )
    pin_counter: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        # For terminal_registry, if it's a TerminalRegistry
        # object (immutable), we just pass reference.
        # If it's a dict (legacy fallback/empty), we copy it.
        tr = self.terminal_registry
        if isinstance(tr, dict):
            tr = tr.copy()

        return {
            "tags": self.tags.copy(),
            "terminal_counters": self.terminal_counters.copy(),
            "contact_channels": self.contact_channels.copy(),
            "terminal_registry": tr,
            "pin_counter": self.pin_counter,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GenerationState":
        """Create from dictionary for backward compatibility."""
        # Handle terminal_registry
        tr = d.get("terminal_registry")
        if tr is None:
            tr = TerminalRegistry()
        elif isinstance(tr, dict):
            # If it's a dict, keep it as dict or try to
            # convert? For now keep as is if it's legacy
            # dict state, but ideally it should be
            # TerminalRegistry. Note: pure dict won't have
            # add_connection unless we convert it.
            # If legacy dict has {terminal_registry: {}},
            # we probably want TerminalRegistry.
            if not tr:  # Empty dict
                tr = TerminalRegistry()
            else:
                tr = tr.copy()  # Keep as dict if not empty? Or warning?
        # If it's already an object (from to_dict), use it. It's frozen/immutable.

        return cls(
            tags=d.get("tags", {}).copy(),
            terminal_counters=d.get("terminal_counters", {}).copy(),
            contact_channels=d.get("contact_channels", {}).copy(),
            terminal_registry=tr,
            pin_counter=d.get("pin_counter", 0),
        )


def create_initial_state() -> Dict[str, Any]:
    """
    Create a new initial state dictionary.

    Returns:
        Dict: A fresh state with all required keys initialized.
    """
    return GenerationState().to_dict()
