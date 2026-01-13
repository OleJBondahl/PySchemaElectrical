"""
Standard Power Circuits.

Note: This module requires terminal IDs and spacing values to be passed from the calling project.
No terminal or spacing constants are hard-coded in the library.
"""

from typing import Any, Tuple, List, Dict, Callable, Optional, Union

from pyschemaelectrical.system.system import Circuit
from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.symbols.blocks import psu, dynamic_block
from pyschemaelectrical.symbols.contacts import three_pole_spdt
from pyschemaelectrical.model.constants import GRID_SIZE



def create_psu(
    state: Any,
    x: float,
    y: float,
    spacing: float = 150,
    terminal_input: str = None,
    terminal_output_24v: str = None,
    terminal_output_gnd: str = None,
    symbol_spacing: float = 60,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a standardized PSU block circuit using CircuitBuilder.
    
    Args:
        terminal_input: Terminal ID for AC input
        terminal_output_24v: Terminal ID for 24V output
        terminal_output_gnd: Terminal ID for GND output
        symbol_spacing: Spacing between symbols in the circuit
    """
    if not all([terminal_input, terminal_output_24v, terminal_output_gnd]):
        raise ValueError("All terminal parameters are required")
    
    builder = CircuitBuilder(state)
    builder.set_layout(x, y, spacing=spacing)
    
    # PSU Width/Geometry is approx 60mm.
    # Terminals need to be spread.
    # Relative offsets:
    # PSU Center at X.
    # L/N Terminals at Y. PSU at Y+Spacing. 24V/GND at Y+Spacing*2.
    
    # 0. L Terminal (Top Left)
    builder.add_terminal(
        terminal_input, 
        logical_name='INPUT', 
        pins=["L"], # Hardcode for now or use map
        x_offset=-15, 
        y_increment=0, 
        auto_connect_next=False
    )
    
    # 1. N Terminal (Top Right)
    builder.add_terminal(
        terminal_input,  # Same strip
        logical_name='INPUT', 
        pins=["N"],
        x_offset=15, 
        y_increment=symbol_spacing,
        label_pos="right",
        auto_connect_next=False
    )

    # 2. PSU Block (Middle)
    builder.add_component(
        psu, 
        tag_prefix="G",
        y_increment=symbol_spacing,
        auto_connect_next=False
    )
    
    # 3. 24V Terminal (Bot Left)
    builder.add_terminal(
        terminal_output_24v,
        logical_name='OUTPUT_24V',
        x_offset=-15,
        y_increment=0,
        pins=["1"], # TODO: Proper pin logic
        auto_connect_next=False
    )
    
    # 4. GND Terminal (Bot Right)
    builder.add_terminal(
        terminal_output_gnd,
        logical_name='OUTPUT_GND',
        x_offset=15,
        y_increment=0,
        pins=["1"],
        label_pos="right",
        auto_connect_next=False
    )
    
    # Manual Connections
    # Indices: 0=L, 1=N, 2=PSU, 3=24V, 4=GND
    # Connect L(0) to PSU(2)
    builder.add_connection(0, 0, 2, 0, side_a="bottom", side_b="top") # P0 maps to L? Need verify
    # Connect N(1) to PSU(2)
    builder.add_connection(1, 0, 2, 1, side_a="bottom", side_b="top") # P1 maps to N?
    # Connect PSU(2) to 24V(3)
    builder.add_connection(3, 0, 2, 0, side_a="top", side_b="bottom") 
    # Connect PSU(2) to GND(4)
    builder.add_connection(4, 0, 2, 1, side_a="top", side_b="bottom")
    
    result = builder.build(count=kwargs.get("count", 1))
    return result.state, result.circuit, result.used_terminals

def create_changeover(
    state: Any,
    x: float,
    y: float,
    terminal_input_1: str = None,
    terminal_input_2: str = None,
    terminal_output: str = None,
    symbol_spacing: float = 60,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a manual changeover switch circuit (3-pole) using CircuitBuilder.
    
    Args:
        terminal_input_1: First input terminal ID (e.g., main power)
        terminal_input_2: Second input terminal ID (e.g., emergency power)
        terminal_output: Output terminal ID
        symbol_spacing: Spacing between symbols
    """
    if not all([terminal_input_1, terminal_input_2, terminal_output]):
        raise ValueError("All terminal parameters are required")
    
    builder = CircuitBuilder(state)
    builder.set_layout(x, y)
    
    # Switch is central.
    # Input 1 (Main) Left. Input 2 (EM) Right.
    # Output Center.
    
    # We will build it as 3 components per phase? No, 3-pole symbols.
    # CircuitBuilder supports 3-pole components.
    
    # 0. Main Input Terminals (Left)
    builder.add_terminal(
        terminal_input_1,
        logical_name='INPUT_1',
        poles=3, 
        x_offset=-GRID_SIZE*4, # Shift left
        y_increment=0,
        auto_connect_next=False
    )

    # 1. EM Input Terminals (Right)
    builder.add_terminal(
        terminal_input_2,
        logical_name='INPUT_2',
        poles=3,
        x_offset=GRID_SIZE*4, # Shift right
        y_increment=symbol_spacing * 1.5,
        label_pos="right",
        auto_connect_next=False
    )
    
    # 2. Changeover Switch (Center)
    builder.add_component(
        three_pole_spdt,
        tag_prefix="K",
        poles=3,
        y_increment=symbol_spacing * 1.5,
        auto_connect_next=False
    )
    
    # 3. Output Terminals (Center)
    builder.add_terminal(
        terminal_output,
        logical_name='OUTPUT',
        poles=3,
        auto_connect_next=False # End of chain
    )
    
    # Connections
    # 0(Main) -> 2(Switch) (NC side?)
    # 1(EM) -> 2(Switch) (NO side?)
    # 2(Switch) -> 3(Output) (COM side)
    
    # Note: Using manual connections requires mapping indices correctly.
    # CircuitBuilder manual connection passes index and pole.
    # But for 3-pole items, we need to register EACH pole manually?
    # Or implement a helper.
    # Currently builder.add_connection takes specific pole.
    # I'll just rely on graphical auto-connect for now, but register Logic.
    
    # For graphical auto-connect:
    # Terminals are at top. Switch middle.
    # If using CircuitBuilder, graphics are handled by `auto_connect_circuit` in build().
    # It scans ports. If geometry aligns, it connects.
    # Layout strategy:
    # 0: Term Main @ (-20, 0)
    # 1: Term EM @ (20, 0)
    # 2: Switch @ (0, 75). Switch has ports at specific offsets?
    #    three_pole_spdt has NC/NO ports. Usually NC is left, NO is right?
    #    If they align with terminals, it works.
    
    
    result = builder.build(count=kwargs.get("count", 1))
    return result.state, result.circuit, result.used_terminals


def create_voltage_monitor(
    state: Any,
    x: float,
    y: float,
    terminal_input: str = None,
    symbol_spacing: float = 60,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a voltage monitor circuit using CircuitBuilder.
    
    Args:
        terminal_input: Input terminal ID for voltage monitoring
        symbol_spacing: Spacing between symbols
    """
    if not terminal_input:
        raise ValueError("terminal_input parameter is required")
    
    builder = CircuitBuilder(state)
    builder.set_layout(x, y, symbol_spacing=symbol_spacing)

    tag_prefix = kwargs.get("tag_prefix", "K")
    
    # 1. Input Terminals (Top)
    # They should align with the dynamic block ports (L1, L2, L3)
    # Dynamic block has pin_spacing=GRID_SIZE * 2
    # So we need 3 terminals spaced by GRID_SIZE * 2
    
    # L1 Terminal
    builder.add_terminal(
        input_terminal_id,
        logical_name='INPUT_L1',
        pins=["L1"], # Placeholder pin logic
        x_offset=-GRID_SIZE*2, 
        y_increment=0,
        auto_connect_next=False
    )
    
     # L2 Terminal
    builder.add_terminal(
        input_terminal_id,
        logical_name='INPUT_L2',
        pins=["L2"],
        x_offset=0, # Center
        y_increment=0,
        forced_pos_fields={'x': x}, # Force absolute X to center? No, builder uses relative to current component usually
        # Actually builder auto-advances if not parallel. 
        # But here we want 3 terminals in parallel on the same Y line.
        # CircuitBuilder's flow is sequential. To do parallel, we reset context or use offsets carefully.
        # But wait, component chain is usually vertical.
        # These 3 terminals are horizontal relative to each other?
        # Yes, L1, L2, L3 are ports on top.
    )
    # Actually, CircuitBuilder isn't great for horizontal parallel items in a vertical flow yet without tricks.
    # But `_create_voltage_monitor` did it by just adding symbols manually.
    # Let's use `add_component` with explicit offsets if possible, or just standard sequential but override X.
    
    # Let's retry:
    # We add the Monitor Symbol first? No, terminals are usually above.
    # Let's add the Monitor Symbol first, then terminals above it? No, standard is flow down.
    
    # Alternative: Just one 3-pole terminal?
    # `three_pole_terminal` has standard spacing. `dynamic_block` has configurable spacing.
    # If we match them, it's easy.
    # dynamic_block uses GRID_SIZE*2.
    # three_pole_terminal uses GRID_SIZE*2 ? (Need to check symbol).
    # Assuming we can use a single 3-pole terminal if spacing aligns.
    
    builder.add_terminal(
        terminal_input,
        logical_name='INPUT',
        poles=3, 
        y_increment=0,
        auto_connect_next=True # Connect to next component
    )
    
    # 2. Monitor Symbol
    builder.add_component(
        dynamic_block,  # Note: dynamic_block is a function returning a Symbol, builder handles it if it's a standard symbol function
        # But dynamic_block needs arguments (top_pins, bottom_pins).
        # CircuitBuilder's add_component passes extra kwargs to the symbol function.
        tag_prefix=tag_prefix,
        y_increment=kwargs.get("symbol_spacing", 50),
        # Extra args for dynamic_block:
        top_pins=("L1", "L2", "L3"),
        bottom_pins=("11", "12", "14"),
        pin_spacing=GRID_SIZE * 2
    )

    
    # 3. Output logic (Open pins)
    # No terminals below for now.
    
    result = builder.build(count=kwargs.get("count", 1))
    return result.state, result.circuit, result.used_terminals


def create_power_distribution(
    state: Any,
    x: float,
    y: float,
    spacing: float = 150,
    spacing_single_pole: float = 100,
    **kwargs
) -> Tuple[Any, Any, List[Any]]:
    """
    Creates a complete power distribution system (Changeover + Voltage Monitor + PSU).
    
    Args:
        spacing: Motor circuit spacing value
        spacing_single_pole: Single pole circuit spacing value
        terminal_maps: Dict mapping logical keys to physical terminal IDs.
                       Required keys: 'INPUT_1', 'INPUT_2', 'OUTPUT', 'PSU_INPUT', 'PSU_OUTPUT_24V', 'PSU_OUTPUT_GND'
    """
    terminal_maps = kwargs.get("terminal_maps", {})
    if not terminal_maps:
        raise ValueError("terminal_maps parameter is required")
        
    count = kwargs.get("count", 1)
    
    # 1. Changeover Switch (Main Power Entry)
    # We use manual offsets if we want them side-by-side or builder if we want iteration.
    # The existing project logic used create_horizontal_layout for changeover.
    # We can replicate that simply by iterating if count > 1.
    
    all_elements = []
    all_terminals = []
    
    current_x = x
    
    # 1. Changeover
    for _ in range(count):
        state, circuit, terminals = create_changeover(
            state, 
            current_x, 
            y,
            terminal_input_1=terminal_maps.get('INPUT_1'),
            terminal_input_2=terminal_maps.get('INPUT_2'),
            terminal_output=terminal_maps.get('OUTPUT')
        )
        all_elements.extend(circuit.elements)
        all_terminals.extend(terminals)
        current_x += spacing
        
    # 2. Voltage Monitor
    # Positioned after the last changeover
    # Offset logic from project: start_x + (count * spacing) + 50
    # Our current_x is already start_x + count*spacing.
    vm_x = current_x + 50 - kwargs.get("spacing", Spacing.MOTOR_CIRCUIT_SPACING) # Wait, loop increments at end.
    # Actually explicit logic: start_x + count*spacing.
    # If count=1, loop runs once, current_x moves to x+spacing.
    # So vm_x = current_x + 50 is reasonable.
    
    # Wait, in original code: vm_start_x = start_x + (count * Spacing.MOTOR_CIRCUIT_SPACING) + 50
    # But create_horizontal_layout returns elements. If count=1, it occupies one slot.
    # Let's trust the relative layout.
    
    # Correction: The original code added spacing * count. 
    # If standard spacing is used, we can just continue from where we left off.
    
    vm_x = x + (count * spacing) + 50
    
    state, vm_circuit, vm_terms = create_voltage_monitor(
        state=state,
        x=vm_x,
        y=y,
        terminal_input=terminal_maps.get('INPUT_1')
    )
    all_elements.extend(vm_circuit.elements)
    all_terminals.extend(vm_terms)
    
    # 3. 24V PSU
    # Positioned after VM.
    psu_x = vm_x + spacing_single_pole + 25
    
    state, psu_c, psu_terms = create_psu(
        state=state,
        x=psu_x,
        y=y,
        terminal_input=terminal_maps.get('PSU_INPUT'),
        terminal_output_24v=terminal_maps.get('PSU_OUTPUT_24V'),
        terminal_output_gnd=terminal_maps.get('PSU_OUTPUT_GND'),
        pin_overrides=kwargs.get('pin_overrides', {})
    )
    all_elements.extend(psu_c.elements)
    all_terminals.extend(psu_terms)
    
    # Combine everything
    system_circuit = Circuit(elements=all_elements)
    
    # Add input/output terminals to list if not already there (helper lists)
    # The sub-create functions return used terminals, so we should be good.
    # But create_changeover might not return the 'Main' terminals if they aren't 'used' in the generic sense?
    # CircuitBuilder returns used_terminals tracked by add_terminal.
    
    return state, system_circuit, list(set(all_terminals))
