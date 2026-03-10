"""Re-export shim: actual code lives in schematika.core.renderer."""

from schematika.core.renderer import (  # noqa: F401
    _render_element,
    _style_to_str,
    calculate_bounds,
    render_to_svg,
    save_svg,
    to_xml_element,
)
