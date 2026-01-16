"""
Example: Direct-On-Line (DOL) Motor Starter Circuit.

This example demonstrates how to create a DOL motor starter using the
standard circuits library.
"""

from pathlib import Path
from pyschemaelectrical import create_autonumberer, std_circuits, render_system
from .constants import Terminals, Paths


def main():
    """
    Create a DOL starter circuit example.

    Demonstrates:
    - Creating a single DOL starter
    - Creating multiple DOL starters (count parameter)
    - Using project-specific terminal IDs
    """
    # Initialize autonumbering state
    state = create_autonumberer()

    # Create output directory
    output_path = Path(Paths.DOL_STARTER)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Example 1: Single DOL starter
    print("Creating DOL starter circuit...")
    state, circuit, used_terminals = std_circuits.dol_starter(
        state=state,
        x=0,
        y=0,
        tm_top=Terminals.MAIN_POWER,
        tm_bot=Terminals.MOTOR_1,
        tm_bot_right=Terminals.PE,
        tm_aux_1=Terminals.FUSED_24V,
        tm_aux_2=Terminals.GND,
    )

    # Render to SVG
    render_system(circuit, str(output_path))
    print(f"✓ Single DOL starter saved to: {Paths.DOL_STARTER}")
    print(f"  Used terminals: {used_terminals}")

    # Example 2: Multiple DOL starters (count=2)
    print("\nCreating multiple DOL starters (count=2)...")
    state_multi = create_autonumberer()
    state_multi, circuit_multi, used_terminals_multi = std_circuits.dol_starter(
        state=state_multi,
        x=0,
        y=0,
        tm_top=Terminals.MAIN_POWER,
        tm_bot=Terminals.MOTOR_1,
        tm_bot_right=Terminals.PE,
        tm_aux_1=Terminals.FUSED_24V,
        tm_aux_2=Terminals.GND,
        count=2,
    )

    multi_path = output_path.parent / "dol_starter_multiple.svg"
    render_system(circuit_multi, str(multi_path))
    print(f"✓ Multiple DOL starters saved to: {multi_path}")
    print(f"  Used terminals: {used_terminals_multi}")


if __name__ == "__main__":
    main()
