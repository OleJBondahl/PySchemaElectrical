"""Tests for the A3 frame generator."""

from pyschemaelectrical.rendering.typst.frame_generator import (
    A3_HEIGHT,
    A3_WIDTH,
    CONTENT_HEIGHT,
    CONTENT_WIDTH,
    INNER_FRAME_X1,
    INNER_FRAME_X2,
    INNER_FRAME_Y1,
    INNER_FRAME_Y2,
    generate_frame,
)


def test_a3_dimensions():
    """A3 dimensions should be 420x297mm."""
    assert A3_WIDTH == 420
    assert A3_HEIGHT == 297


def test_content_dimensions():
    """Content area should be 400x277mm."""
    assert CONTENT_WIDTH == 400
    assert CONTENT_HEIGHT == 277


def test_inner_frame_positions():
    """Inner frame should be at 10mm from page edges."""
    assert INNER_FRAME_X1 == 10
    assert INNER_FRAME_Y1 == 10
    assert INNER_FRAME_X2 == 410
    assert INNER_FRAME_Y2 == 287


def test_generate_frame_returns_circuit():
    """generate_frame should return a Circuit with elements."""
    circuit = generate_frame()
    assert circuit is not None
    assert len(circuit.elements) > 0


def test_generate_frame_has_grid_labels():
    """Frame should contain column (1-8) and row (A-F) labels."""
    from pyschemaelectrical.model.primitives import Text

    circuit = generate_frame()
    texts = [e for e in circuit.elements if isinstance(e, Text)]

    # Should have labels for 8 columns * 2 sides + 6 rows * 2 sides = 28 labels
    labels = [t.content for t in texts]
    for i in range(1, 9):
        assert str(i) in labels, f"Column label {i} missing"
    for c in "ABCDEF":
        assert c in labels, f"Row label {c} missing"


def test_generate_frame_custom_font():
    """generate_frame should accept a custom font_family parameter."""
    from pyschemaelectrical.model.primitives import Text

    circuit = generate_frame(font_family="Arial")
    texts = [e for e in circuit.elements if isinstance(e, Text)]
    # At least one text should have the custom font
    assert any(t.style.font_family == "Arial" for t in texts)


def test_generate_frame_has_lines():
    """Frame should contain border lines."""
    from pyschemaelectrical.model.primitives import Line

    circuit = generate_frame()
    lines = [e for e in circuit.elements if isinstance(e, Line)]
    # Two rectangles (outer + inner) = 8 lines, plus grid dividers
    assert len(lines) >= 8
