from pyschemaelectrical.system import Circuit, add_symbol, auto_connect_circuit, render_system, layout_horizontal
from pyschemaelectrical.symbols.terminals import three_pole_terminal, terminal
from pyschemaelectrical.symbols.breakers import three_pole_circuit_breaker
from pyschemaelectrical.symbols.assemblies import contactor
from pyschemaelectrical.symbols.transducers import current_transducer_assembly
from pyschemaelectrical.autonumbering import create_autonumberer, next_tag, next_terminal_pins
from constants_examples import Terminals, Spacing
import os


def pump_circuit_generator(state, x, y):
    elements = []
    
    # Generate Tags and Pins using autonumbering state
    state, f_tag = next_tag(state, "F")
    state, q_tag = next_tag(state, "Q")
    state, ct_tag = next_tag(state, "CT")
    
    # Terminals
    state, main_pins = next_terminal_pins(state, Terminals.MAIN_400V, 3)
    state, ext_pins = next_terminal_pins(state, Terminals.EXT_AC, 3)
    state, fused_24v_pins = next_terminal_pins(state, Terminals.FUSED_24V, 1)
    state, gnd_pins = next_terminal_pins(state, Terminals.GND, 1)
    
    # Create a temporary circuit context
    c = Circuit()

    # Use x as the starting X for this circuit copy
    # We use Spacing class just for Y offsets now, but use passed 'x' for X position
    
    base_x = x
    
    add_symbol(c, three_pole_terminal(Terminals.MAIN_400V, pins=main_pins), base_x, y + Spacing.MOTOR_SYMBOLS_SPACING)
    add_symbol(c, three_pole_circuit_breaker(f_tag, pins=("1", "2", "3","4","5","6")), base_x, y + Spacing.MOTOR_SYMBOLS_SPACING * 2)
    add_symbol(c, contactor(q_tag, contact_pins=("1", "2", "3","4","5","6")), base_x, y + Spacing.MOTOR_SYMBOLS_SPACING * 3)
    # Capture CT symbol
    ct_sym = add_symbol(c, current_transducer_assembly(ct_tag, pins=("1", "2", "3","4")), base_x, y + Spacing.MOTOR_SYMBOLS_SPACING * 3.5)
    add_symbol(c, three_pole_terminal(Terminals.EXT_AC, pins=ext_pins), base_x, y + Spacing.MOTOR_SYMBOLS_SPACING * 4)

    # Add current transducer input terminals and capture them
    # Ensure to import auto_connect if not available, or use auto_connect_circuit's internal logic?
    # Actually auto_connect is imported in system.py but not exported? 
    # It is exported in __init__.py usually? No, checked layouts.
    # pump_example imports `auto_connect_circuit` from system.
    # We might need to import `auto_connect` from `pyschemaelectrical.layout`.
    
    t1 = add_symbol(c, terminal(Terminals.FUSED_24V, pins=fused_24v_pins, label_pos="right"), base_x-40, y + (Spacing.MOTOR_SYMBOLS_SPACING * 3.5) - 40)
    t2 = add_symbol(c, terminal(Terminals.GND, pins=gnd_pins, label_pos="right"), base_x-30, y + (Spacing.MOTOR_SYMBOLS_SPACING * 3.5) - 30)
    t3 = add_symbol(c, terminal("AI", pins=(), label_pos="right"), base_x-20, y + (Spacing.MOTOR_SYMBOLS_SPACING * 3.5) - 20)
    t4 = add_symbol(c, terminal("AI", pins=(), label_pos="right"), base_x-10, y + (Spacing.MOTOR_SYMBOLS_SPACING * 3.5) - 10)

    # Manually connect auxiliary terminals to CT
    # We need auto_connect function.
    from pyschemaelectrical.layout import auto_connect
    
    c.elements.extend(auto_connect(t1, ct_sym))
    c.elements.extend(auto_connect(t2, ct_sym))
    c.elements.extend(auto_connect(t3, ct_sym))
    c.elements.extend(auto_connect(t4, ct_sym))

    auto_connect_circuit(c)
    
    return state, c.elements


def main():
  os.makedirs("examples/output", exist_ok=True)
  
  # Initialize Autonumbering
  state = create_autonumberer()
  
  # Generate 3 circuits
  final_state, all_elements = layout_horizontal(
      start_state=state,
      start_x=Spacing.MOTOR_SYMBOLS_START_X,
      start_y=0, # Base Y
      spacing=Spacing.MOTOR_CIRCUIT_SPACING * 2, # More spacing between circuits
      count=3,
      generate_func=pump_circuit_generator
  )
  
  # Wrap in temporary circuit for rendering
  # render_system accepts a Circuit object which has .elements
  system_circuit = Circuit(elements=all_elements)
  
  render_system(system_circuit, "examples/output/pump_example.svg", width="auto", height="auto")

if __name__ == "__main__":
  main()
