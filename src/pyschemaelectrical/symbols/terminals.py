from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from pyschemaelectrical.model.constants import DEFAULT_POLE_SPACING
from pyschemaelectrical.model.core import Element, Point, Port, Symbol, Vector
from pyschemaelectrical.model.parts import (
    create_pin_labels,
    standard_text,
    terminal_circle,
)
from pyschemaelectrical.utils.transform import translate

"""
IEC 60617 Terminal Symbols.
"""


@dataclass(frozen=True)
class Terminal(Symbol):
    """
    Specific symbol type for Terminals.
    Distinct from generic Symbols to allow for specialized
    system-level processing (e.g., CSV export).

    Attributes:
        terminal_number (Optional[str]): The specifically assigned terminal number.
    """

    terminal_number: Optional[str] = None


@dataclass(frozen=True)
class TerminalBlock(Symbol):
    """
    Symbol representing a block of terminals (e.g. 3-pole).
    Contains mapping of ports to terminal numbers.

    Attributes:
        channel_map (Dict[Tuple[str, str], str]): Map of
            (up_port_id, down_port_id) -> terminal_number.
    """

    # Map of (up_port_id, down_port_id) -> terminal_number
    channel_map: Optional[Dict[Tuple[str, str], str]] = None


def terminal_symbol(
    label: str = "", pins: tuple = (), label_pos: str = "left"
) -> Terminal:
    """
    Create an IEC 60617 Terminal symbol.

    Symbol Layout:
       O

    Args:
        label (str): The tag of the terminal strip (e.g. "X1").
        pins (tuple): Tuple of pin numbers. Only the first
                      one is used as the terminal number.
                      It is displayed at the bottom port.
        label_pos (str): Position of label ('left' or 'right').

    Returns:
        Terminal: The terminal symbol.
    """

    # Center at (0,0)
    c = terminal_circle(Point(0, 0))

    elements: List[Element] = [c]
    if label:
        elements.append(standard_text(label, Point(0, 0), label_pos=label_pos))

    # Port 1: Up (Input/From)
    # Port 2: Down (Output/To)
    ports = {
        "1": Port("1", Point(0, 0), Vector(0, -1)),
        "2": Port("2", Point(0, 0), Vector(0, 1)),
    }
    ports["top"] = replace(ports["1"], id="top")
    ports["bottom"] = replace(ports["2"], id="bottom")

    term_num = None
    if pins:
        # User Requirement: "only have a pin number at the bottom"
        # We take the first pin as the terminal number.
        term_num = pins[0]

        # We attach it to Port "2" (Bottom/Down).
        # We use a temporary dict to force the function to label only Port "2"
        elements.extend(create_pin_labels(ports={"2": ports["2"]}, pins=(term_num,)))

    return Terminal(
        elements=elements, ports=ports, label=label, terminal_number=term_num
    )


def multi_pole_terminal_symbol(
    label: str = "",
    pins: tuple = (),
    poles: int = 2,
    label_pos: str = "left",
) -> TerminalBlock:
    """
    Create an N-pole terminal block.

    Args:
        label: The tag of the terminal strip (e.g. "X1").
        pins: Tuple of terminal numbers, one per pole.
              Padded with empty strings if shorter than poles.
        poles: Number of poles (must be >= 2).
        label_pos: Position of label ('left' or 'right').

    Returns:
        TerminalBlock: The N-pole terminal block.
    """
    p_safe = list(pins)
    while len(p_safe) < poles:
        p_safe.append("")

    all_elements: List[Element] = []
    new_ports = {}
    channel_map = {}

    for i in range(poles):
        pole_label = label if i == 0 else ""
        pole_lpos = label_pos if i == 0 else "left"
        pole = terminal_symbol(label=pole_label, pins=(p_safe[i],), label_pos=pole_lpos)
        if i > 0:
            pole = translate(pole, DEFAULT_POLE_SPACING * i, 0)

        all_elements += pole.elements

        in_id = str(i * 2 + 1)
        out_id = str(i * 2 + 2)
        if "1" in pole.ports:
            new_ports[in_id] = replace(pole.ports["1"], id=in_id)
        if "2" in pole.ports:
            new_ports[out_id] = replace(pole.ports["2"], id=out_id)
        channel_map[(in_id, out_id)] = pole.terminal_number

    return TerminalBlock(
        elements=tuple(all_elements), ports=new_ports, label=label, channel_map=channel_map
    )


def three_pole_terminal_symbol(
    label: str = "", pins: tuple = ("1", "2", "3"), label_pos: str = "left"
) -> TerminalBlock:
    """
    Create a 3-pole terminal block.

    Args:
        label: The tag of the terminal strip.
        pins: A tuple of 3 terminal numbers (e.g. ("1", "2", "3")).
        label_pos: Position of label ('left' or 'right').

    Returns:
        TerminalBlock: The 3-pole terminal block.
    """
    return multi_pole_terminal_symbol(label, pins, poles=3, label_pos=label_pos)
