"""
Example: State Threading Across Multiple Circuits.

Demonstrates how the autonumbering state flows through multiple circuit
factory calls, ensuring terminal pins auto-increment correctly and
component tags don't collide.

Key concept: Each factory function receives the current state and returns
an updated state. By passing the returned state to the next call,
pin numbering and tag counting continue seamlessly.

Run with:
    python -m examples.example_state_threading
"""

from pyschemaelectrical.std_circuits import coil, emergency_stop, no_contact
from pyschemaelectrical.system.system import merge_circuits, render_system
from pyschemaelectrical.utils.autonumbering import create_autonumberer


def main():
    """Build multiple circuits sharing terminals with continuous pin numbering."""

    print("=" * 60)
    print("PySchemaElectrical — State Threading Example")
    print("=" * 60)

    # Create initial state — all counters start at 1
    state = create_autonumberer()

    # ── Circuit 1: Emergency stop on X1 ───────────────────────
    # State goes in, updated state comes out
    result1 = emergency_stop(state, x=0, y=0, tm_top="X1", tm_bot="X2")
    state = result1.state  # Pass updated state forward

    print("\nAfter emergency_stop:")
    print(f"  Tags: {result1.component_map}")
    print(f"  X1 pins: {result1.terminal_pin_map.get('X1', [])}")
    print(f"  X2 pins: {result1.terminal_pin_map.get('X2', [])}")

    # ── Circuit 2: NO contacts, also using X1 ────────────────
    # X1 pins continue from where circuit 1 left off
    result2 = no_contact(state, x=100, y=0, tm_top="X1", tm_bot="X2", count=2)
    state = result2.state

    print("\nAfter no_contact (count=2):")
    print(f"  Tags: {result2.component_map}")
    print(f"  X1 pins: {result2.terminal_pin_map.get('X1', [])}")
    print(f"  X2 pins: {result2.terminal_pin_map.get('X2', [])}")

    # ── Circuit 3: Coils, using X1 for top terminal ──────────
    # X1 pins continue from where circuit 2 left off
    result3 = coil(state, x=300, y=0, tm_top="X1", count=2)
    state = result3.state

    print("\nAfter coil (count=2):")
    print(f"  Tags: {result3.component_map}")
    print(f"  X1 pins: {result3.terminal_pin_map.get('X1', [])}")

    # ── Merge all circuits for rendering ──────────────────────
    combined = merge_circuits(
        [result1.circuit, result2.circuit, result3.circuit]
    )

    render_system(combined, "examples/output/state_threading.svg")
    print("\nSVG written to examples/output/state_threading.svg")
    print("\nNotice: X1 terminal pins increment continuously across all 3 circuits.")


if __name__ == "__main__":
    main()
