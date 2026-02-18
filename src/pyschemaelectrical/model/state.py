"""
Typed state for circuit generation.

Provides type-safe state management for the CircuitBuilder and
related generation functions.
"""

from dataclasses import dataclass, field
from typing import Any

# Avoid direct import if circular dependency is feared, but verified safe here.
from pyschemaelectrical.system.connection_registry import TerminalRegistry


@dataclass
class GenerationState:
    """
    Immutable state container for circuit generation.

    Attributes:
        tags: Counter for component tags (e.g., {"K": 3} means next K is K4)
        terminal_counters: Counter for terminal numbering per terminal block
        terminal_prefix_counters: Per-prefix counters for prefixed terminals
            (e.g., {"X001": {"L1": 3, "N": 2}} means next L1 on X001 is group 4)
        contact_channels: Counter for contact channel assignment
        terminal_registry: Registry of terminal connections
        pin_counter: Global pin counter (legacy)
    """

    tags: dict[str, int] = field(default_factory=dict)
    terminal_counters: dict[str, int] = field(default_factory=dict)
    terminal_prefix_counters: dict[str, dict[str, int]] = field(default_factory=dict)
    contact_channels: dict[str, int] = field(default_factory=dict)
    terminal_registry: TerminalRegistry | dict = field(
        default_factory=TerminalRegistry
    )
    pin_counter: int = 0

    def to_dict(self) -> dict[str, Any]:
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
            "terminal_prefix_counters": {
                tag: prefixes.copy()
                for tag, prefixes in self.terminal_prefix_counters.items()
            },
            "contact_channels": self.contact_channels.copy(),
            "terminal_registry": tr,
            "pin_counter": self.pin_counter,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GenerationState":
        """Create from dictionary for backward compatibility."""
        # Handle terminal_registry
        tr = d.get("terminal_registry")
        if tr is None:
            tr = TerminalRegistry()
        elif isinstance(tr, dict):
            # Legacy dict state — convert empty dicts to TerminalRegistry,
            # keep non-empty dicts as-is for backward compatibility.
            if not tr:
                tr = TerminalRegistry()
            else:
                tr = tr.copy()
        # If it's already an object (from to_dict), use it. It's frozen/immutable.

        return cls(
            tags=d.get("tags", {}).copy(),
            terminal_counters=d.get("terminal_counters", {}).copy(),
            terminal_prefix_counters={
                tag: prefixes.copy()
                for tag, prefixes in d.get("terminal_prefix_counters", {}).items()
            },
            contact_channels=d.get("contact_channels", {}).copy(),
            terminal_registry=tr,
            pin_counter=d.get("pin_counter", 0),
        )


def create_initial_state() -> dict[str, Any]:
    """
    Create a new initial state dictionary.

    Returns:
        dict: A fresh state with all required keys initialized.
    """
    return GenerationState().to_dict()
