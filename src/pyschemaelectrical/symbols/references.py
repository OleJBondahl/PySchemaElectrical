from dataclasses import dataclass
from typing import Dict, List, Tuple

from pyschemaelectrical.model.constants import (
    REF_ARROW_HEAD_LENGTH,
    REF_ARROW_HEAD_WIDTH,
    REF_ARROW_LENGTH,
)
from pyschemaelectrical.model.core import Element, Point, Port, Symbol, Vector
from pyschemaelectrical.model.parts import standard_style, standard_text
from pyschemaelectrical.model.primitives import Line, Polygon


@dataclass(frozen=True)
class RefSymbol(Symbol):
    pass


def ref_symbol(
    tag: str = "",
    label: str = "",
    pins: Tuple[str, ...] = (),
    direction: str = "up",
    label_pos: str = "left",
    **kwargs,
) -> RefSymbol:
    """
    Reference symbol (arrow) to indicate connection to another circuit element.

    Args:
        tag (str): Auto-generated tag (usually ignored if label is present).
        label (str): The text to display (e.g. "F1:1"). If empty, uses tag.
        pins (tuple): Ignored, present for builder compatibility.
        direction (str): "up" (points up, connects from below) or "down" (points down, connects from above).
        label_pos (str): Position of the label ("left" or "right"). Default is "left".
        **kwargs: Extra arguments for compatibility.
    """
    elements: List[Element] = []
    ports: Dict[str, Port] = {}

    text_content = label if label else tag

    origin = Point(0, 0)

    style = standard_style()

    if direction == "up":
        # Arrow pointing UP.
        # Origin (0,0) is the TIP.
        # Tail is below origin.
        # This symbol acts as a SOURCE/TOP connection point.
        # Components connect to it from BELOW.

        tip = origin
        tail = Point(0, REF_ARROW_LENGTH)

        # Shaft: Line from Tail to Tip
        elements.append(Line(tail, tip, style))

        # Arrow Head at Tip (pointing UP)
        # ^
        head_base_y = tip.y + REF_ARROW_HEAD_LENGTH
        p_left = Point(-REF_ARROW_HEAD_WIDTH / 2, head_base_y)
        p_right = Point(REF_ARROW_HEAD_WIDTH / 2, head_base_y)

        elements.append(Polygon([p_left, tip, p_right], style))

        # Label: Placed to the right of the middle of the shaft
        mid_y = REF_ARROW_LENGTH / 2
        elements.append(
            standard_text(text_content, Point(0, mid_y), label_pos=label_pos)
        )

        # Port: Connects to below (output/down) at the Tail
        ports["2"] = Port("2", tail, Vector(0, 1))

    else:  # down
        # Arrow pointing DOWN.
        # Origin (0,0) is the TIP.
        # Tail is above origin.
        # This symbol acts as a SINK/BOTTOM connection point.
        # Components connect to it from ABOVE.

        tip = origin
        tail = Point(0, -REF_ARROW_LENGTH)

        # Shaft from Tail to Tip
        elements.append(Line(tail, tip, style))

        # Arrow Head at Tip (pointing DOWN)
        # v
        head_base_y = tip.y - REF_ARROW_HEAD_LENGTH
        p_left = Point(-REF_ARROW_HEAD_WIDTH / 2, head_base_y)
        p_right = Point(REF_ARROW_HEAD_WIDTH / 2, head_base_y)

        elements.append(Polygon([p_left, tip, p_right], style))

        # Label
        mid_y = -REF_ARROW_LENGTH / 2
        elements.append(
            standard_text(text_content, Point(0, mid_y), label_pos=label_pos)
        )

        # Port: Connects to above (input/up) at the Tail
        ports["1"] = Port("1", tail, Vector(0, -1))

    return RefSymbol(elements=elements, ports=ports, label=text_content)
