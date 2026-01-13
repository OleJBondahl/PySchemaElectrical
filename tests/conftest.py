import pytest
import os
from pathlib import Path

# Fixture to handle snapshot comparison for SVG content
@pytest.fixture
def snapshot_svg(request):
    """
    Fixture that returns a function to compare SVG content against a stored snapshot.
    Usage:
        def test_something(snapshot_svg):
            svg_content = generate_svg()
            snapshot_svg(svg_content, "something_snapshot")
    """
    # Directory for snapshots is adjacent to this conftest file + /snapshots
    snapshot_dir = Path(__file__).parent / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)

    def _compare(content: str, snapshot_name: str):
        # Normalize the content (optional: strip dynamic dates/ids if strictly necessary)
        # For now, we assume the generator is deterministic or mocked.
        # But we do trip whitespace from ends.
        content = content.strip()
        
        snapshot_file = snapshot_dir / f"{snapshot_name}.svg"
        
        # Environment variable to force update snapshots: PYTEST_UPDATE_SNAPSHOTS=1
        update_snapshots = os.getenv("PYTEST_UPDATE_SNAPSHOTS") == "1"

        if not snapshot_file.exists() or update_snapshots:
            # Write/Update snapshot
            snapshot_file.write_text(content, encoding="utf-8")
            # If we are just updating, we might want to warn or print
            if update_snapshots:
                print(f"Updated snapshot: {snapshot_file}")
            else:
                print(f"Created new snapshot: {snapshot_file}")
            return

        # Compare
        expected_content = snapshot_file.read_text(encoding="utf-8").strip()
        
        # Simple string equality
        # In a real scenario, XML parsing comparison might be more robust to ignore attribute order,
        # but string equality is stricter and strictly requested ("consistency").
        assert content == expected_content, (
            f"Snapshot mismatch for {snapshot_name}. \n"
            f"Run with PYTEST_UPDATE_SNAPSHOTS=1 to update if this change is intentional."
        )

    return _compare
