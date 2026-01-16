from dataclasses import dataclass, field
from typing import List, Union
from pyschemaelectrical.model.core import Symbol, Element
from pyschemaelectrical.utils.transform import translate
from pyschemaelectrical.layout.layout import auto_connect
from pyschemaelectrical.utils.renderer import (
    render_to_svg,
)


@dataclass
class Circuit:
    """
    A container for electrical symbols and their connections.

    Attributes:
        symbols (List[Symbol]): Ordered list of main components.
        elements (List[Element]): All graphical elements (symbols + wires).
    """

    symbols: List[Symbol] = field(default_factory=list)
    elements: List[Element] = field(default_factory=list)


def add_symbol(circuit: Circuit, symbol: Symbol, x: float, y: float) -> Symbol:
    """
    Add a symbol to the circuit at a specified position.

    This function handles the translation of the symbol to the given coordinates
    and adds it to the circuit's internal storage.

    Args:
        circuit (Circuit): The circuit to add to.
        symbol (Symbol): The symbol instance to add (usually created from symbols library).
        x (float): The x-coordinate.
        y (float): The y-coordinate.

    Returns:
        Symbol: The placed (translated) symbol.
    """
    placed_symbol = translate(symbol, x, y)
    circuit.symbols.append(placed_symbol)
    circuit.elements.append(placed_symbol)
    return placed_symbol


def auto_connect_circuit(circuit: Circuit):
    """
    Automatically connect all adjacent connectable symbols in the circuit.

    Iterates through the symbols in the order they were added.
    Skips symbols marked with skip_auto_connect=True.
    Connects each symbol to the next connectable one using auto_connect logic.

    Args:
        circuit (Circuit): The circuit to process.
    """
    connectable_symbols = [s for s in circuit.symbols if not s.skip_auto_connect]

    for i in range(len(connectable_symbols) - 1):
        s1 = connectable_symbols[i]
        s2 = connectable_symbols[i + 1]
        lines = auto_connect(s1, s2)
        circuit.elements.extend(lines)


def render_system(
    circuits: Union[Circuit, List[Circuit]],
    filename: str,
    width: Union[str, int] = "auto",
    height: Union[str, int] = "auto",
):
    """
    Render one or more circuits to an SVG file.

    Args:
        circuits (Union[Circuit, List[Circuit]]): A single Circuit or list of Circuits.
        filename (str): The output file path.
        width (str|int): Document width.
        height (str|int): Document height.
    """
    all_elements = []

    # Normalize to list
    circuit_list: List[Circuit]
    if isinstance(circuits, list):
        circuit_list = circuits
    else:
        circuit_list = [circuits]

    for c in circuit_list:
        all_elements.extend(c.elements)

    render_to_svg(all_elements, filename, width=width, height=height)


def merge_circuits(target: Circuit, source: Circuit) -> None:
    """
    Merge source circuit into target circuit (mutates target).

    Args:
        target: The circuit to merge into
        source: The circuit to merge from
    """
    target.symbols.extend(source.symbols)
    target.elements.extend(source.elements)
