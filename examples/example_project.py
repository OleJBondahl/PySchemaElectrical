"""
Example: Full Project with PDF Output.

Demonstrates the Layer 0 Project API by combining multiple standard circuits
into a multi-page drawing set. The Project handles state management,
terminal pin allocation, SVG generation, and PDF compilation automatically.

Run with:
    python -m examples.example_project

Requires the optional 'typst' dependency for PDF output:
    pip install pyschemaelectrical[pdf]

Without typst, use build_svgs() instead of build() for SVG-only output.
"""

from pyschemaelectrical import Project, Terminal
from pyschemaelectrical.wire import wire


def main():
    """Create a complete example project with multiple circuit pages."""

    print("=" * 60)
    print("PySchemaElectrical — Example Project")
    print("=" * 60)

    # ── Project definition ─────────────────────────────────────
    project = Project(
        title="Example Drawing Set",
        drawing_number="EX-001",
        author="PySchemaElectrical",
        project="Example Project",
        revision="01",
    )

    # ── Terminal definitions ───────────────────────────────────
    project.terminals(
        # Power terminals
        Terminal("X1", "Main 400V AC"),
        Terminal("X2", "AC Input 230V"),
        Terminal("X3", "Fused 24V DC", bridge="all"),
        Terminal("X4", "Ground / 0V", bridge="all"),
        Terminal("X5", "Main Supply"),
        Terminal("X6", "Emergency Supply"),
        Terminal("X7", "Changeover Output"),
        # Motor output terminals
        Terminal("X10", "Motor 1 Output"),
        Terminal("X11", "Motor 2 Output"),
        # Control terminals
        Terminal("X20", "Emergency Stop", bridge="all"),
        # PE
        Terminal("PE", "Protective Earth"),
    )

    # ── Motor wire labels ──────────────────────────────────────
    motor_wires = [
        wire("BR", "2.5mm2"),
        wire("BK", "2.5mm2"),
        wire("GY", "2.5mm2"),
        wire.EMPTY,
        wire.EMPTY,
        wire.EMPTY,
        wire("BR", "2.5mm2"),
        wire("BK", "2.5mm2"),
        wire("GY", "2.5mm2"),
        wire("BR", "2.5mm2"),
        wire("BK", "2.5mm2"),
        wire("GY", "2.5mm2"),
        wire.EMPTY,
        wire.EMPTY,
        wire.EMPTY,
        wire.EMPTY,
    ]

    # ── Circuits ───────────────────────────────────────────────

    # 1. DOL motor starters (2 motors)
    project.dol_starter(
        "motors",
        count=2,
        tm_top="X1",
        tm_bot=["X10", "X11"],
        tm_aux_1="X3",
        tm_aux_2="X4",
        wire_labels=motor_wires,
    )

    # 2. Changeover switch
    project.changeover(
        "changeover",
        tm_top_left="X5",
        tm_top_right="X6",
        tm_bot="X7",
    )

    # 3. Power supply
    project.psu(
        "psu",
        tm_top="X2",
        tm_bot_left="X3",
        tm_bot_right="X4",
    )

    # 4. Emergency stop
    project.emergency_stop(
        "estop",
        tm_top="X3",
        tm_bot="X20",
    )

    # 5. Coil circuit
    project.coil(
        "coils",
        count=2,
        tm_top="X3",
    )

    # ── Pages ──────────────────────────────────────────────────

    project.page("Motor Circuits", "motors")
    project.page("Changeover Switch", "changeover")
    project.page("Power Supply", "psu")
    project.page("Emergency Stop", "estop")
    project.page("Coil Circuits", "coils")
    project.terminal_report()

    # ── Build ──────────────────────────────────────────────────

    # Try PDF output first, fall back to SVG-only
    try:
        import typst  # noqa: F401

        output_pdf = "examples/output/example_project.pdf"
        project.build(
            output_pdf,
            temp_dir="examples/output/project_temp",
            keep_temp=True,
        )
        print(f"\nPDF compiled: {output_pdf}")
    except ImportError:
        print("\n'typst' package not installed — generating SVGs only.")
        print("Install with: pip install pyschemaelectrical[pdf]")
        project.build_svgs("examples/output/project_svgs")

    print("\nDone!")


if __name__ == "__main__":
    main()
