from typing import Dict, List, Tuple, Optional
from pyschemaelectrical.model.core import Symbol, Element
from ..symbols.breakers import three_pole_circuit_breaker
from ..symbols.protection import three_pole_thermal_overload
from ..symbols.terminals import three_pole_terminal
from ..symbols.assemblies import contactor
from pyschemaelectrical.layout.layout import auto_connect, auto_connect_labeled
from pyschemaelectrical.utils.transform import translate
from pyschemaelectrical.utils.autonumbering import next_tag, next_terminal_pins, auto_contact_pins, auto_thermal_pins, auto_coil_pins

def motor_circuit(
    state: Dict[str, int],
    x_position: float,
    y_start: float,
    normal_spacing: float,
    tight_spacing: float,
    wire_config: Optional[Dict[str, List[Tuple[str, str]]]] = None,
    terminal_tags: Tuple[str, str] = ("X1", "X2")
) -> Tuple[Dict[str, int], List[Element]]:
    """
    Create a complete motor protection circuit with autonumbered components.

    This function creates a vertical chain of:
    - Top terminal (terminal_tags[0]) - tag stays the same, pins auto-increment
    - Circuit breaker (F) - tag auto-increments
    - Thermal overload (F) - tag auto-increments
    - Contactor (Q) - tag auto-increments
    - Bottom terminal (terminal_tags[1]) - tag stays the same, pins auto-increment

    Args:
        state: Current autonumbering state.
        x_position: Horizontal position for the circuit.
        y_start: Starting vertical position.
        normal_spacing: Standard spacing between components.
        tight_spacing: Tight spacing (e.g., between breaker and thermal).
        wire_config: Dictionary mapping component tag prefixes to wire specifications.
                     Key: Component tag prefix (e.g. "X", "Q").
                     Value: List of (color, size) tuples for the wires originating from that component.
        terminal_tags: Tuple of terminal tags (top, bottom). Default is ("X1", "X2").

    Returns:
        Tuple containing updated state and list of placed symbols/lines.
    """
    all_elements: List[Element] = []
    current_y = y_start
    wire_config = wire_config or {}

    # Generate auto-incrementing tags for F and Q components
    state, f1_tag = next_tag(state, "F")
    state, ft_tag = next_tag(state, "FT")
    state, q_tag = next_tag(state, "Q")
    state, t_tag = next_tag(state, "T")

    # Generate auto-incrementing pins for terminals (ONCE per circuit, shared by X1 and X2)
    state, terminal_pins = next_terminal_pins(state, poles=3)

    # Create components
    top_terminals = three_pole_terminal(
        label=terminal_tags[0],
        pins=terminal_pins
    )

    circuit_breaker = three_pole_circuit_breaker(
        label=f1_tag,
        pins=auto_contact_pins()
    )

    thermal_overload = three_pole_thermal_overload(
        label=ft_tag,
        pins=auto_thermal_pins()
    )

    contactor_asm = contactor(
        label=q_tag,
        coil_pins=auto_coil_pins(),
        contact_pins=auto_contact_pins()
    )

    bot_terminals = three_pole_terminal(
        label=terminal_tags[1],
        pins=terminal_pins
    )

    # Place components vertically
    top_placed = translate(top_terminals, x_position, current_y)
    all_elements.append(top_placed)
    current_y += normal_spacing

    f1_placed = translate(circuit_breaker, x_position, current_y)
    all_elements.append(f1_placed)
    current_y += tight_spacing

    ft_placed = translate(thermal_overload, x_position, current_y)
    all_elements.append(ft_placed)
    current_y += normal_spacing

    q_placed = translate(contactor_asm, x_position, current_y)
    all_elements.append(q_placed)
    
    # Place Current Transducer on the Leftmost Wire (Pole 1)
    # Between Contactor and Bottom Terminal
    # Position: x_position (Left Wire), Y = current_y + normal_spacing / 2
    from .transducers import current_transducer_assembly
    
    transducer_y = current_y + normal_spacing / 2
    transducer = translate(
        current_transducer_assembly(label=t_tag, pins=("1", "2", "3", "4")), 
        x_position, 
        transducer_y
    )
    all_elements.append(transducer)
    
    current_y += normal_spacing

    bot_placed = translate(bot_terminals, x_position, current_y)
    all_elements.append(bot_placed)

    def connect_intelligent(src: Symbol, dst: Symbol) -> List[Element]:
        """Helper to connect components with labels determined by source component tag."""
        specs = None
        if src.label:
            for prefix, sp in wire_config.items():
                if src.label.startswith(prefix):
                    specs = sp
                    break

        if specs:
            return auto_connect_labeled(src, dst, specs)
        else:
            return auto_connect(src, dst)

    # Auto-connect all components with conditional labeled wires
    all_elements.extend(connect_intelligent(top_placed, f1_placed))
    all_elements.extend(connect_intelligent(f1_placed, ft_placed))
    all_elements.extend(connect_intelligent(ft_placed, q_placed))
    all_elements.extend(connect_intelligent(q_placed, bot_placed))

    return state, all_elements
