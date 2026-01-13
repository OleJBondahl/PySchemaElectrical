"""
Standard Control Circuits.

Note: This module requires terminal IDs and spacing values to be passed from the calling project.
No terminal or spacing constants are hard-coded in the library.
"""

from typing import Any, Tuple, List
from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.symbols.coils import coil
from pyschemaelectrical.symbols.contacts import spdt_contact, normally_open
from pyschemaelectrical.model.constants import GRID_SIZE



def create_motor_control(
    state: Any,
    x: float,
    y: float,
    terminal_em_stop: str = None,
    terminal_lights_switches: str = None,
    spacing: float = 100,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a standard motor control circuit (Start/Stop with latch or PLC control).
    
    Args:
        terminal_em_stop: Emergency stop terminal ID
        terminal_lights_switches: Lights/switches terminal ID
        spacing: Circuit spacing
    """
    if not all([terminal_em_stop, terminal_lights_switches]):
        raise ValueError("terminal_em_stop and terminal_lights_switches are required")
    
    builder = CircuitBuilder(state)
    builder.set_layout(x, y, spacing=spacing)
    
    # Components:
    # 1. EM Stop Input (Stop)
    # 2. Coil (Q)
    # 3. Contact (K) (Readback/Latch) - Optional?
    
    # 0. EM Stop Terminal
    builder.add_terminal(
        terminal_em_stop,
        logical_name='EM_STOP',
        auto_connect_next=True
    )
    
    # 1. Coil (Q)
    # Usually connected after EM Stop.
    builder.add_component(
        coil,
        tag_prefix="Q",
        auto_connect_next=False # Manual wiring for coil A1 connected to EM Stop
    )

    # 2. Feedback Contact (K)
    # In parallel or separate?
    # Based on existing 'motor_controll_circuit.py', there is an SPDT contact K
    # and a Terminal Light/Switch.
    
    # Existing logic:
    # EM_Stop -> Q(A1). Q(A2) -> PLC:AI (or GND).
    # K(Contact) -> Lights_Switches.
    
    # This implies TWO columns?
    # Column 1: Control (EM -> Coil)
    # Column 2: Feedback (Switch -> Contact)
    
    # Using our new x_offset we can do this!
    
    # -- Column 1 --
    # Already added Terminal EM_STOP (x=0, y=0)
    # Already added Coil Q (x=0, y=50)
    
    # -- Column 2 --
    # Feedback Contact K (x=50, y=100?)
    # Switch Terminal (x=50, y=150?)
    
    builder.add_component(
        spdt_contact,
        tag_prefix="K",
        x_offset=GRID_SIZE * 6, # Shift right 30mm
        y_increment=0, # Reset Y relative to... previous was Q.
        # Check builder loop: y increments by spec value.
        # If Q increment was default (50), current_y is now 50.
        # We want K aligned?
        # Let's handle Y manually if we can, or just let it stack.
        auto_connect_next=False
    )
    
    builder.add_terminal(
        terminal_lights_switches,
        logical_name='LIGHTS_SWITCHES',
        x_offset=GRID_SIZE * 6,
        y_increment=50,
        label_pos="right",
        auto_connect_next=False # Connect K to Lights manually
    )

    # Manual Connections
    # 0(EM) -> 1(Q)(A1) (Auto connect works if vertical? But we said auto_connect_next=False for Q?)
    # Actually Q is at y=50. EM at y=0. Vertical align.
    # If auto_connect_next=True on EM, it connects to Q.
    # But Q is 'symbol', EM is 'terminal'. auto_connect_next logic checks valid pairs.
    # Let's set auto_connect_next=True for EM.
    
    # 2(K) -> 3(Lights)
    # They are vertically aligned at x=30.
    # builder.add_connection(2, 0, 3, 0)
    
    
    result = builder.build(
        count=kwargs.get("count", 1),
        tag_generators=kwargs.get("tag_generators"),
        terminal_maps=kwargs.get("terminal_maps"),
        start_indices=kwargs.get("start_indices")
    )
    return result.state, result.circuit, result.used_terminals



def create_switch(
    state: Any,
    x: float,
    y: float,
    terminal_input: str = None,
    terminal_output: str = None,
    spacing: float = 100,
    symbol_spacing: float = 60,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a simple switch circuit.
    
    Args:
        terminal_input: Input terminal ID
        terminal_output: Output terminal ID (typically GND)
        spacing: Circuit spacing
        symbol_spacing: Symbol spacing
    """
    if not all([terminal_input, terminal_output]):
        raise ValueError("terminal_input and terminal_output are required")
    
    builder = CircuitBuilder(state)
    builder.set_layout(
        x=x,
        y=y,
        spacing=spacing,
        symbol_spacing=symbol_spacing
    )
    
    # 1. Input Terminal
    builder.add_terminal(terminal_input, poles=1)
    
    # 2. Switch (Normally Open)
    builder.add_component(normally_open, tag_prefix='S', poles=1)
    
    # 3. Output Terminal (GND)
    builder.add_terminal(terminal_output, poles=1)
    
    result = builder.build(
        count=kwargs.get("count", 1),
        start_indices=kwargs.get("start_indices"),
        terminal_start_indices=kwargs.get("terminal_start_indices"),
        tag_generators=kwargs.get("tag_generators"),
        terminal_maps=kwargs.get("terminal_maps")
    )
    return result.state, result.circuit, result.used_terminals


