"""Backward compatibility shim — pyschemaelectrical is now schematika."""

import warnings

warnings.warn(
    "pyschemaelectrical is renamed to schematika. "
    "Update imports to 'from schematika import ...' or 'from schematika.electrical import ...'",
    DeprecationWarning,
    stacklevel=2,
)

from schematika.electrical import *  # noqa: F401, F403
