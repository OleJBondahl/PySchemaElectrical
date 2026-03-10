from __future__ import annotations

import math

from .models import Position

FAMILY_TYPE_MAP: dict[str, str] = {
    "CR": "contactor",
    "TD": "timer_relay",
    "M": "motor",
    "CB": "circuit_breaker",
    "OL": "overload_relay",
    "PB": "pushbutton",
    "LT": "pilot_light",
    "FU": "fuse",
    "TR": "transformer",
    "TS": "terminal_strip",
    "SS": "selector_switch",
    "LS": "limit_switch",
    "PS": "pressure_switch",
    "PE": "photo_eye",
    "PL": "pilot_light",
    "SOL": "solenoid",
    "VFD": "variable_frequency_drive",
}


def normalize_component_type(family: str, block_name: str = "") -> str:
    upper_family = family.upper()
    if upper_family in FAMILY_TYPE_MAP:
        return FAMILY_TYPE_MAP[upper_family]
    upper_block = block_name.upper()
    for key, value in FAMILY_TYPE_MAP.items():
        if key in upper_block:
            return value
    return "unknown"


def distance(a: Position, b: Position) -> float:
    return math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def positions_close(a: Position, b: Position, tolerance: float = 0.5) -> bool:
    return distance(a, b) <= tolerance
