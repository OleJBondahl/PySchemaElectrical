"""Custom exceptions for PySchemaElectrical."""


class CircuitValidationError(Exception):
    """
    Raised when circuit validation fails.

    This exception provides detailed information about validation failures
    to help developers quickly identify and fix issues.
    """

    pass


class PortNotFoundError(CircuitValidationError):
    """Raised when a referenced port does not exist on a component."""

    def __init__(self, component_tag: str, port_id: str, available_ports: list):
        self.component_tag = component_tag
        self.port_id = port_id
        self.available_ports = available_ports
        super().__init__(
            f"Port '{port_id}' not found on component '{component_tag}'. "
            f"Available ports: {available_ports}"
        )


class ComponentNotFoundError(CircuitValidationError):
    """Raised when a referenced component index is out of bounds."""

    def __init__(self, index: int, max_index: int):
        super().__init__(
            f"Component index {index} is out of bounds. Valid indices: 0-{max_index}"
        )
