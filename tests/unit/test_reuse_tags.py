"""Tests for reuse_tags on CircuitBuilder.build()."""

import pytest

from pyschemaelectrical.builder import CircuitBuilder
from pyschemaelectrical.exceptions import TagReuseError
from pyschemaelectrical.symbols.coils import coil_symbol
from pyschemaelectrical.symbols.contacts import normally_open_symbol
from pyschemaelectrical.utils.autonumbering import create_autonumberer


def test_reuse_tags_yields_tags_from_source():
    """Build coils, then build contacts with reuse_tags, verify same K tags."""
    state = create_autonumberer()

    # Build coils (allocates K tags: K1, K2, K3)
    coil_builder = CircuitBuilder(state)
    coil_builder.set_layout(x=0, y=0, spacing=80)
    coil_builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    coil_result = coil_builder.build(count=3)

    assert coil_result.component_map["K"] == ["K1", "K2", "K3"]

    # Build contacts reusing K tags
    contact_builder = CircuitBuilder(coil_result.state)
    contact_builder.set_layout(x=0, y=0, spacing=80)
    contact_builder.add_component(normally_open_symbol, "K", pins=("13", "14"))
    contact_result = contact_builder.build(count=3, reuse_tags={"K": coil_result})

    assert contact_result.component_map["K"] == ["K1", "K2", "K3"]


def test_reuse_tags_exhaustion_raises():
    """Building more instances than source tags should raise TagReuseError."""
    state = create_autonumberer()

    coil_builder = CircuitBuilder(state)
    coil_builder.set_layout(x=0, y=0, spacing=80)
    coil_builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    coil_result = coil_builder.build(count=2)

    contact_builder = CircuitBuilder(coil_result.state)
    contact_builder.set_layout(x=0, y=0, spacing=80)
    contact_builder.add_component(normally_open_symbol, "K", pins=("13", "14"))

    with pytest.raises(TagReuseError):
        contact_builder.build(count=3, reuse_tags={"K": coil_result})


def test_build_result_reuse_tags_method():
    """BuildResult.reuse_tags() should return a callable generator."""
    state = create_autonumberer()

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=80)
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    result = builder.build(count=2)

    gen = result.reuse_tags("K")
    assert callable(gen)

    s, tag1 = gen(state)
    s, tag2 = gen(s)
    assert tag1 == "K1"
    assert tag2 == "K2"


def test_reuse_tags_with_tag_generators_coexist():
    """reuse_tags and explicit tag_generators should coexist."""
    state = create_autonumberer()

    builder = CircuitBuilder(state)
    builder.set_layout(x=0, y=0, spacing=80)
    builder.add_component(coil_symbol, "K", pins=("A1", "A2"))
    coil_result = builder.build(count=2)

    builder2 = CircuitBuilder(coil_result.state)
    builder2.set_layout(x=0, y=0, spacing=80)
    builder2.add_component(normally_open_symbol, "K", pins=("13", "14"))
    builder2.add_component(normally_open_symbol, "S", pins=("3", "4"))

    def fixed_s(s):
        return s, "S_FIXED"

    result = builder2.build(
        count=2,
        reuse_tags={"K": coil_result},
        tag_generators={"S": fixed_s},
    )

    assert result.component_map["K"] == ["K1", "K2"]
    assert result.component_map["S"] == ["S_FIXED", "S_FIXED"]
