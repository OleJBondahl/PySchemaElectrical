
import sys
import os

# Ensure we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyschemaelectrical.core import Point
from pyschemaelectrical.symbols.contacts import three_pole_normally_open, three_pole_normally_closed
from pyschemaelectrical.symbols.protection import three_pole_thermal_overload
from pyschemaelectrical.symbols.terminals import three_pole_terminal
from pyschemaelectrical.renderer import render_to_svg
from pyschemaelectrical.layout import layout_vertical_chain

# --- High Level System Builder Functions ---

def create_system(layout_func, configs, start_pos=Point(50, 50), spacing_x=120.0):
    """
    Generates a system of multiple circuit blocks side-by-side.
    
    Args:
        layout_func (callable): Function that takes (config, start_point) and returns 
                                a list of Symbols. This defines the 'shape' of one block.
        configs (list[dict]): A list of configuration dictionaries. One per block.
                              These are passed to layout_func.
        start_pos (Point): The top-left position of the first block.
        spacing_x (float): The horizontal distance between the start of adjacent blocks.
        
    Returns:
        list[Symbol]: A flat list of all symbols in the system.
    """
    system_symbols = []
    
    current_x = start_pos.x
    current_y = start_pos.y
    
    for i, config in enumerate(configs):
        # Determine start point for this instance
        block_start = Point(current_x, current_y)
        
        # Build the block using the provided layout function
        # We pass the full config dict to the layout function
        block_symbols = layout_func(config, block_start)
        
        system_symbols.extend(block_symbols)
        
        # Advance X position
        current_x += spacing_x
        
    return system_symbols

# --- Specific Layout Definition (as per three_pole_demo) ---

def standard_motor_starter_layout(config, start_point):
    """
    Creates a standard motor starter circuit (Terminal -> NO -> NC -> Thermal -> Terminal).
    Mirroring the structure from examples/three_pole_demo.py
    
    Args:
        config (dict): Configuration for the components. 
                       Keys should match the internal component identifiers 
                       (e.g., 'term_top', 'contactor_main', etc.).
                       Values should be dicts of kwargs for the factories (label, pins).
        start_point (Point): The starting anchor point for this vertical chain.
        
    Returns:
        list[Symbol]: The interconnected symbols.
    """
    
    # 1. Helper to safely merge user config with defaults
    #    This allows the user to specify just {"label": "X100"} and keep default pins.
    def get_component_args(key, default_label, default_pins):
        user_args = config.get(key, {})
        # Start with defaults
        final_args = {
            "label": default_label,
            "pins": default_pins
        }
        # Update with user provided values (overwriting defaults)
        final_args.update(user_args)
        return final_args

    # 2. Instantiate Components using the configs
    
    # Top Terminals
    t_top_args = get_component_args("term_top", "X1", ("1", "2", "3", "4", "5", "6"))
    top_terminals = three_pole_terminal(**t_top_args)
    
    # Main Contactor (NO)
    k1_args = get_component_args("k1", "-K1", ("1", "2", "3", "4", "5", "6"))
    k1 = three_pole_normally_open(**k1_args)
    
    # Secondary/Safety Contactor (NC)
    k2_args = get_component_args("k2", "-K2", ("11", "12", "13", "14", "15", "16"))
    k2 = three_pole_normally_closed(**k2_args)
    
    # Thermal Overload
    f1_args = get_component_args("f1", "-F1", ("1", "2", "3", "4", "5", "6"))
    f1 = three_pole_thermal_overload(**f1_args)
    
    # Bottom Terminals
    t_bot_args = get_component_args("term_bot", "X2", ("U", "V", "W", "X", "Y", "Z"))
    bot_terminals = three_pole_terminal(**t_bot_args)
    
    # 3. Layout
    # Connect them vertically.
    return layout_vertical_chain(
        symbols=[top_terminals, k1, k2, f1, bot_terminals],
        start=start_point,
        spacing=40.0
    )


def main():
    print("Generating Multi-Circuit System Demo...")
    
    # Define our system configuration
    # We want 3 motor starters side-by-side.
    
    system_configs = [
        # Circuit 1: The 'Baseline'
        {
            "term_top": {"label": "X1"},
            "k1":       {"label": "-K1"},
            "k2":       {"label": "-K2"},
            "f1":       {"label": "-F1"},
            "term_bot": {"label": "X2"},
        },
        # Circuit 2: Different Tags, Custom Pins
        {
            "term_top": {"label": "X3", "pins": ("L1", "L2", "L3", "N", "PE", "Spare")},
            "k1":       {"label": "-K3"},
            "k2":       {"label": "-K4"},
            "f1":       {"label": "-F2"},
            "term_bot": {"label": "X4"},
        },
        # Circuit 3: Another one
        {
            "term_top": {"label": "X5"},
            "k1":       {"label": "-K5"},
            "k2":       {"label": "-K6"},
            "f1":       {"label": "-F3"},
            "term_bot": {"label": "X6"},
        }
    ]
    
    # Build the system
    # We pass our specific layout function (standard_motor_starter_layout)
    # and the config.
    all_components = create_system(
        layout_func=standard_motor_starter_layout, 
        configs=system_configs, 
        start_pos=Point(50, 50), 
        spacing_x=70.0 # Enough space for 3-pole width (approx 60-80?) plus margin
    )
    
    # Render
    # Use a wide canvas
    output_file = "multi_circuit_demo.svg"
    render_to_svg(all_components, output_file, width="450mm", height="400mm")
    print(f"Saved to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
