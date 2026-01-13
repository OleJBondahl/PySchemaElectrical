"""
Standard Motor Circuits.

Note: This module requires terminal IDs to be passed from the calling project.
No terminal or spacing constants are defined in the library.
"""

from typing import Any, Dict, List, Tuple

from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.symbols.assemblies import contactor
from pyschemaelectrical.symbols.breakers import three_pole_circuit_breaker
from pyschemaelectrical.symbols.protection import three_pole_thermal_overload
from pyschemaelectrical.symbols.transducers import current_transducer_assembly
from pyschemaelectrical.system.connection_registry import register_connection


def create_dol_starter(
    state: Any,
    x: float, 
    y: float,
    count: int = 1,
    spacing: float = 150,
    terminal_input: str = None,
    terminal_output: str = None,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Create a Direct-On-Line (DOL) Motor Starter.
    
    Args:
        state: Autonumbering state
        x: X position
        y: Y position
        count: Number of circuits to create
        spacing: Spacing between circuits
        terminal_input: Input terminal ID (required)
        terminal_output: Output terminal ID (required)
        **kwargs: Additional options including terminal_maps for aux connections
    """
    if not terminal_input or not terminal_output:
        raise ValueError("terminal_input and terminal_output are required parameters")
    
    builder = CircuitBuilder(state)
    builder.set_layout(x, y, spacing=spacing)
    
    # 1. Main Power Terminal
    builder.add_terminal(terminal_input, poles=3, label_pos="left")
    
    # 2. Circuit Breaker (Q)
    builder.add_component(three_pole_circuit_breaker, tag_prefix="F", poles=3)
    
    # 3. Thermal Overload (FT)
    builder.add_component(three_pole_thermal_overload, tag_prefix="FT", poles=3)

    # 4. Contactor (K)
    builder.add_component(contactor, tag_prefix="Q", poles=3)
    
    # 5. Current Transducer (CT)
    # The CT has 3 poles for power, plus aux connections.
    # We add it as a 3-pole component for the main flow.
    # Note: current_transducer_assembly function should be checked for signature matching.
    builder.add_component(current_transducer_assembly, tag_prefix="CT", poles=3)
    
    # 6. Motor Terminal
    builder.add_terminal(terminal_output, poles=3, label_pos="left")
    
    # 7. Aux Terminals (Optional)
    tm = kwargs.get('terminal_maps') or {}
    t_24v = tm.get('FUSED_24V')
    t_gnd = tm.get('GND')

    
    if t_24v:
        builder.add_terminal(t_24v, poles=1, label_pos="left", auto_connect_next=False)
        
    if t_gnd:
        builder.add_terminal(t_gnd, poles=1, label_pos="left", auto_connect_next=False)

    
    # Build main flow
    result = builder.build(count=kwargs.get("count", count))
    
    # 7. Add Aux connections (24V/GND -> CT) if needed
    # Using result.state and result.component_map we could do this.
    # For now, adhering to existing behavior but returning clean tuple.
    
    return result.state, result.circuit, result.used_terminals

def create_vfd_starter(state, x, y, count=1, **kwargs):
    # Placeholder for VFD
    pass
