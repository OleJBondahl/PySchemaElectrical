"""
High-level functions for creating wire labels on connections.

This module provides functional abstractions for adding wire specification labels
(color, size, etc.) to connection lines in electrical schematics.
"""

from itertools import cycle, islice
from typing import List, Optional, Tuple

from pyschemaelectrical.model.constants import TEXT_FONT_FAMILY_AUX, TEXT_SIZE_PIN
from pyschemaelectrical.model.core import Element, Point
from pyschemaelectrical.model.primitives import Line, Text


def calculate_wire_label_position(
    start: Point,
    end: Point,
    offset_x: float = -2.5,  # Default to -2.5 to place left of wire
) -> Point:
    """
    Calculate the position for a wire label along a vertical wire.

    Places the label at the midpoint of the wire.

    Args:
        start (Point): Starting point of the wire.
        end (Point): Ending point of the wire.
        offset_x (float): Horizontal offset from wire (default -2.5).

    Returns:
        Point: The calculated label position.
    """
    mid_x = (start.x + end.x) / 2.0
    mid_y = (start.y + end.y) / 2.0

    return Point(mid_x + offset_x, mid_y)


def create_wire_label_text(
    text_content: str, position: Point, font_size: float = TEXT_SIZE_PIN
) -> Text:
    """
    Create a text element for a wire label.

    Rotated 90 degrees (text runs downwards) and centered on the wire.

    Args:
        text_content (str): The label text (e.g., "RD 2.5mm²").
        position (Point): The position for the text.
        font_size (float): Font size for the text.

    Returns:
        Text: The configured text element.
    """
    from pyschemaelectrical.model.core import Style

    return Text(
        content=text_content,
        position=position,
        anchor="middle",  # Center horizontally (relative to rotated text)
        dominant_baseline="middle",  # Center vertically (relative to rotated text, i.e., on the wire)
        font_size=font_size,
        rotation=90.0,  # Text runs downwards
        style=Style(stroke="none", fill="black", font_family=TEXT_FONT_FAMILY_AUX),
    )


def format_wire_specification(color: str = "", size: str = "") -> str:
    """
    Format wire color and size into a standardized label string.

    Args:
        color (str): Wire color code (e.g., "RD", "BK").
        size (str): Wire size specification (e.g., "2.5mm²", "0.5mm²").

    Returns:
        str: Formatted wire specification string.

    Examples:
        >>> format_wire_specification("RD", "2.5mm²")
        'RD 2.5mm²'
        >>> format_wire_specification("BK", "")
        'BK'
        >>> format_wire_specification("", "2.5mm²")
        '2.5mm²'
    """
    parts = [p for p in [color, size] if p]
    return " ".join(parts)


def create_labeled_wire(
    start: Point,
    end: Point,
    wire_color: str = "",
    wire_size: str = "",
    label_offset_x: float = -2.5,
) -> List[Element]:
    """
    Create a wire connection with an optional label.

    High-level function that creates both the wire line and its label text
    if wire specifications are provided.

    Args:
        start (Point): Starting point of the wire.
        end (Point): Ending point of the wire.
        wire_color (str): Wire color code (e.g., "RD", "BK").
        wire_size (str): Wire size specification (e.g., "2.5mm²").
        label_offset_x (float): Horizontal offset for label (default -2.5).

    Returns:
        List[Element]: List containing the wire line and optionally the label text.
    """
    from pyschemaelectrical.model.parts import standard_style

    elements: List[Element] = []

    # Create the wire line
    wire_line = Line(start, end, style=standard_style())
    elements.append(wire_line)

    # Add label if specifications are provided
    label_text = format_wire_specification(wire_color, wire_size)
    if label_text:
        label_pos = calculate_wire_label_position(start, end, label_offset_x)
        label = create_wire_label_text(label_text, label_pos)
        elements.append(label)

    return elements


def create_labeled_connections(
    connection_specs: List[Tuple[Point, Point, str, str]],
) -> List[Element]:
    """
    Create multiple labeled wire connections from specifications.

    Functional approach to batch-create wire connections with labels.

    Args:
        connection_specs: List of tuples, each containing:
            - start (Point): Wire start point
            - end (Point): Wire end point
            - color (str): Wire color code
            - size (str): Wire size specification

    Returns:
        List[Element]: All wire lines and labels as flat list.

    Example:
        >>> specs = [
        ...     (Point(0, 0), Point(0, 10), "RD", "2.5mm²"),
        ...     (Point(10, 0), Point(10, 10), "BK", "0.5mm²")
        ... ]
        >>> elements = create_labeled_connections(specs)
    """
    from functools import reduce

    all_elements = [
        create_labeled_wire(start, end, color, size)
        for start, end, color, size in connection_specs
    ]

    # Flatten the list of lists into a single list
    return reduce(lambda acc, x: acc + x, all_elements, [])


def find_vertical_wires(elements: List[Element], tolerance: float = 0.1) -> List[Line]:
    """
    Find all vertical wire segments in a circuit.

    Args:
        elements: List of circuit elements
        tolerance: X-coordinate tolerance for considering a wire vertical (mm)

    Returns:
        List of Line elements that are vertical wires
    """
    vertical_wires = []

    for element in elements:
        if isinstance(element, Line):
            # Check if line is vertical (start.x ≈ end.x and start.y != end.y)
            if (
                abs(element.start.x - element.end.x) < tolerance
                and abs(element.start.y - element.end.y) > tolerance
            ):
                vertical_wires.append(element)

    return vertical_wires


def add_wire_labels_to_circuit(
    circuit, wire_labels: Optional[List[str]] = None, offset_x: float = -2.5
) -> "Circuit":
    """
    Add wire labels to all vertical wires in a circuit.

    Returns a NEW circuit with wire labels added. Does NOT mutate the original.
    Wire labels are applied in order to vertical wires found in the circuit.

    Args:
        circuit: The Circuit object to add labels to
        wire_labels: List of wire label strings. If None, uses rotating standard labels.
        offset_x: Horizontal offset for labels from wire centerline (mm)

    Returns:
        Circuit: New circuit with wire labels added.
    """
    from pyschemaelectrical.system.system import Circuit

    # Find all vertical wires in the circuit
    vertical_wires = find_vertical_wires(circuit.elements)

    if not vertical_wires:
        print("Warning: No vertical wires found in circuit")
        return circuit

    # If no wire labels are provided, do not add any labels
    if wire_labels is None:
        return circuit

    # Ensure we have enough labels
    if len(wire_labels) < len(vertical_wires):
        # Repeat the provided wire labels to cover all wires
        # This handles cases where count > 1 (creating multiple circuit instances)
        wire_labels = list(islice(cycle(wire_labels), len(vertical_wires)))

    new_elements = []

    # Add labels to each wire
    for i, wire in enumerate(vertical_wires):
        if i >= len(wire_labels):
            break

        label_text = wire_labels[i]

        # Calculate label position at wire midpoint
        label_pos = calculate_wire_label_position(
            wire.start, wire.end, offset_x=offset_x
        )

        # Create text element
        text_element = create_wire_label_text(label_text, label_pos)

        # Add to new elements list
        new_elements.append(text_element)

    return Circuit(
        symbols=circuit.symbols,
        elements=list(circuit.elements) + new_elements,
    )
