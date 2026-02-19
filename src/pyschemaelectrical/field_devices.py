"""
Field device templates and connection generation.

Provides reusable data types for describing how field devices (sensors,
valves, motors, power feeds) connect to cabinet terminals and PLC modules.
Each device is described by a ``DeviceTemplate`` containing an ordered
tuple of ``PinDef`` entries.  The ``generate_field_connections()`` function
expands a list of device declarations into ``ConnectionRow`` tuples with
auto-numbered terminal pins and PLC reference tags.

Usage example::

    from pyschemaelectrical import Terminal
    from pyschemaelectrical.field_devices import (
        PinDef, DeviceTemplate, generate_field_connections,
    )

    # Define terminals
    SIGNAL = Terminal("X100", "Signal terminal")
    PLC_AI = Terminal("PLC:AI", reference=True)

    # Define a device template
    SENSOR_4_20 = DeviceTemplate(
        mpn="4-20mA Transmitter",
        pins=(
            PinDef("Sig+", SIGNAL, PLC_AI),
            PinDef("GND", SIGNAL),
        ),
    )

    # Expand into connection rows
    rows = generate_field_connections([
        ("PT-01", SENSOR_4_20),
        ("PT-02", SENSOR_4_20),
    ])
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from pyschemaelectrical.builder import BuildResult
    from pyschemaelectrical.terminal import Terminal

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

ConnectionRow = tuple[str, str, Any, str, str, str]
"""
A single connection row in the field wiring report.

Fields: (component_from, pin_from, terminal, terminal_pin, component_to, pin_to)

- component_from: Device tag (e.g., "PT-01").
- pin_from: Device pin name (e.g., "Sig+").
- terminal: Terminal object or tag string for the terminal block.
- terminal_pin: Resolved pin number on the terminal block.
- component_to: PLC reference tag or empty string.
- pin_to: Currently unused (empty string), reserved for PLC pin.
"""

DeviceEntry = Union[
    tuple[str, "DeviceTemplate"],
    tuple[str, "DeviceTemplate", "Terminal"],
]
"""
A device declaration for ``generate_field_connections()``.

Either ``(tag, template)`` — terminal comes from each PinDef — or
``(tag, template, terminal_override)`` — the override terminal is used
for any pin that has no terminal in its PinDef.
"""


# ---------------------------------------------------------------------------
# Core data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PinDef:
    """
    Defines one pin on a field device template.

    Pin numbering modes (mutually exclusive):

    - **Sequential** (default): auto-numbered ``"1"``, ``"2"``, ``"3"``...
      per terminal block.
    - **Prefixed** (``pin_prefix="L1"``): formatted ``"{prefix}:{index}"``.
      All prefixed pins on the same device share one group index per
      terminal.
    - **Fixed** (``terminal_pin="L1"``): literal pin name, no auto-numbering.

    Attributes:
        device_pin: Pin name on the physical device (e.g., ``"R+"``,
            ``"U1"``, ``"1"``).
        terminal: Physical terminal block.  ``None`` means use the
            device-level terminal override.
        plc: PLC reference terminal for auto-assignment.  ``None``
            means no PLC connection.
        terminal_pin: Fixed terminal pin name (skips auto-numbering).
        pin_prefix: Formatted prefix for auto-indexed pins.
    """

    device_pin: str
    terminal: Terminal | None = None
    plc: Terminal | None = None
    terminal_pin: str = ""
    pin_prefix: str = ""


@dataclass(frozen=True)
class SequentialPin(PinDef):
    """Auto-numbered terminal slot.

    Cannot have pin_prefix or terminal_pin — both must be empty.
    Terminal pin is assigned automatically as "1", "2", "3"...
    """

    def __post_init__(self) -> None:
        if self.pin_prefix:
            raise ValueError(
                f"SequentialPin '{self.device_pin}': pin_prefix must be empty "
                f"(use PrefixedPin for prefix-numbered pins)"
            )
        if self.terminal_pin:
            raise ValueError(
                f"SequentialPin '{self.device_pin}': terminal_pin must be empty "
                f"(use FixedPin for literal pin names)"
            )


@dataclass(frozen=True)
class PrefixedPin(PinDef):
    """Prefix-numbered terminal slot (e.g. 'L1:1', 'L2:1').

    Requires pin_prefix; cannot have terminal_pin.
    Terminal pin is formatted as "{pin_prefix}:{group_index}".
    """

    def __post_init__(self) -> None:
        if not self.pin_prefix:
            raise ValueError(f"PrefixedPin '{self.device_pin}': pin_prefix is required")
        if self.terminal_pin:
            raise ValueError(
                f"PrefixedPin '{self.device_pin}': terminal_pin must be empty "
                f"(use FixedPin for literal pin names)"
            )


@dataclass(frozen=True)
class FixedPin(PinDef):
    """Fixed terminal pin name (e.g. 'L1', 'PE').

    Requires terminal_pin; cannot have pin_prefix.
    Terminal pin is used literally without any auto-numbering.
    """

    def __post_init__(self) -> None:
        if not self.terminal_pin:
            raise ValueError(f"FixedPin '{self.device_pin}': terminal_pin is required")
        if self.pin_prefix:
            raise ValueError(
                f"FixedPin '{self.device_pin}': pin_prefix must be empty "
                f"(use PrefixedPin for prefix-numbered pins)"
            )


@dataclass(frozen=True)
class DeviceTemplate:
    """
    Reusable connection pattern for a field device type.

    Attributes:
        mpn: Manufacturer part number or type description.
        pins: Ordered pin definitions for this device.
    """

    mpn: str
    pins: tuple[PinDef, ...]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_terminal_pin(
    pin_def: PinDef,
    terminal_key: str,
    device_prefix_indices: dict[str, int],
    device_prefixes_used: dict[str, set[str]],
    prefix_counters: dict[str, dict[str, int]],
    sequential_counters: dict[str, int],
    reuse_iters: dict[str, Any],
) -> str:
    """Resolve the terminal pin string for a single pin definition.

    This implements the three mutually-exclusive numbering modes
    described in :class:`PinDef`.
    """
    # Mode 1: Fixed pin — use as-is.
    if pin_def.terminal_pin:
        return pin_def.terminal_pin

    # Mode 2: Prefixed pin — group-based numbering.
    if pin_def.pin_prefix:
        if terminal_key not in device_prefix_indices:
            # Compute group number from per-prefix counters for only the
            # prefixes this device uses on this terminal.  A device that
            # uses only N will not advance the L counter.
            tag_counters = prefix_counters.get(terminal_key, {})
            prefixes = device_prefixes_used.get(terminal_key, set())
            max_existing = max(
                (tag_counters.get(p, 0) for p in prefixes),
                default=0,
            )
            new_group = max_existing + 1
            device_prefix_indices[terminal_key] = new_group
            # Update per-prefix counters for the prefixes this device uses
            if terminal_key not in prefix_counters:
                prefix_counters[terminal_key] = {}
            for p in prefixes:
                prefix_counters[terminal_key][p] = new_group

        return f"{pin_def.pin_prefix}:{device_prefix_indices[terminal_key]}"

    # Mode 3: Sequential — consume from reuse iterator or auto-increment.
    if terminal_key in reuse_iters:
        return next(reuse_iters[terminal_key])

    sequential_counters[terminal_key] = sequential_counters.get(terminal_key, 0) + 1
    return str(sequential_counters[terminal_key])


def _build_reuse_iters(
    reuse_terminals: dict[str, list[str] | BuildResult] | None,
) -> dict[str, Any]:
    """Build reuse iterators from a ``reuse_terminals`` mapping.

    Accepted value types per key:

    - ``list[str]``: plain list of pin strings, consumed in order.
    - ``BuildResult``: pins are read from
      ``source.terminal_pin_map[key]``.
    """
    reuse_iters: dict[str, Any] = {}
    if not reuse_terminals:
        return reuse_iters
    for key, source in reuse_terminals.items():
        str_key = str(key)
        if isinstance(source, list):
            reuse_iters[str_key] = iter(source)
        else:
            # Assume BuildResult-like object with terminal_pin_map
            reuse_iters[str_key] = iter(source.terminal_pin_map.get(str_key, []))
    return reuse_iters


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_field_connections(
    devices: list[DeviceEntry],
    reuse_terminals: dict[str, list[str] | BuildResult] | None = None,
) -> list[ConnectionRow]:
    """
    Expand device declarations into connection row tuples.

    Terminal pins are auto-numbered sequentially per terminal block.
    PLC connections use reference tags (resolved later by
    ``PlcMapper`` or project-specific PLC modules).

    Args:
        devices: List of ``(tag, template)`` or
            ``(tag, template, terminal_override)`` tuples.
        reuse_terminals: Optional dict mapping terminal key to a list of
            pin strings or a ``BuildResult``.  When a terminal key
            matches, pins are consumed from the reuse source instead of
            being auto-numbered.

    Returns:
        List of :data:`ConnectionRow` tuples with auto-numbered terminal
        pins and PLC reference tags in the *component_to* field.

    Raises:
        ValueError: If a pin has no terminal and no terminal override
            was provided for its device.
    """
    sequential_counters: dict[str, int] = {}
    prefix_counters: dict[str, dict[str, int]] = {}
    reuse_iters = _build_reuse_iters(reuse_terminals)

    connections: list[ConnectionRow] = []

    for entry in devices:
        tag: str = entry[0]
        template: DeviceTemplate = entry[1]
        terminal_override: Terminal | None = (
            entry[2] if len(entry) > 2 else None  # type: ignore[arg-type]
        )

        device_prefix_indices: dict[str, int] = {}

        # Pre-compute which prefixes this device uses per terminal so
        # _resolve_terminal_pin can compute group numbers correctly.
        device_prefixes_used: dict[str, set[str]] = {}
        for pin_def in template.pins:
            if pin_def.pin_prefix:
                t = pin_def.terminal or terminal_override
                if t is not None:
                    device_prefixes_used.setdefault(str(t), set()).add(
                        pin_def.pin_prefix
                    )

        for pin_def in template.pins:
            terminal = pin_def.terminal or terminal_override

            if terminal is None:
                raise ValueError(
                    f"Device '{tag}' pin '{pin_def.device_pin}': "
                    f"no terminal in template and no terminal override "
                    f"provided"
                )

            terminal_pin = _resolve_terminal_pin(
                pin_def,
                str(terminal),
                device_prefix_indices,
                device_prefixes_used,
                prefix_counters,
                sequential_counters,
                reuse_iters,
            )
            plc_tag = str(pin_def.plc) if pin_def.plc else ""

            connections.append(
                (tag, pin_def.device_pin, terminal, terminal_pin, plc_tag, "")
            )

    return connections
