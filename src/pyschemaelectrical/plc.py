"""
PLC I/O Mapping.

Declarative PLC mapper for allocating sensors to PLC modules,
generating pin names, and tracking terminal connections.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleTypeDef:
    """Definition of a PLC I/O module type."""

    name: str
    capacity: int  # Number of channels per module
    pin_format: str  # Format string, e.g. "CH{ch}{polarity}", "DI{ch}"


@dataclass(frozen=True)
class SensorTypeDef:
    """Definition of a sensor type and how it connects to a PLC module."""

    name: str
    module: str  # Module type name
    pins: tuple[
        str, ...
    ]  # Pin names per channel, e.g. ("Signal", "GND") or ("R+", "RL", "R-")
    polarity: dict[int, str] | None = (
        None  # Pin index -> polarity suffix, e.g. {0: "+", 1: "-"}
    )


@dataclass
class SensorInstance:
    """A specific sensor instance to be mapped."""

    tag: str  # Sensor tag, e.g. "TT-01-CX"
    sensor_type: str  # Sensor type name, e.g. "RTD"
    cable: str  # Cable reference, e.g. "W0102"
    terminal: str  # Terminal ID, e.g. "X007"


@dataclass
class PlcConnection:
    """A single PLC connection row."""

    sensor_tag: str
    cable: str
    terminal: str
    terminal_pin: str
    module_name: str
    module_pin: str
    sensor_pin: str


class PlcMapper:
    """
    Declarative PLC I/O mapper.

    Allocates sensors to PLC modules, generates pin names,
    and tracks terminal connections.

    Usage::

        plc = PlcMapper()
        plc.module_type("AI_mA", capacity=4, pin_format="CH{ch}{polarity}")
        plc.module_type("AI_RTD", capacity=2, pin_format="CH{ch}_{pin}")
        plc.sensor_type(
            "2Wire-mA", module="AI_mA",
            pins=["Signal", "GND"],
            polarity={0: "+", 1: "-"},
        )
        plc.sensor_type("RTD", module="AI_RTD", pins=["R+", "RL", "R-"])
        plc.sensor("TT-01-CX", type="RTD", cable="W0102", terminal="X007")
        connections = plc.generate_connections()
    """

    def __init__(self) -> None:
        self._module_types: dict[str, ModuleTypeDef] = {}
        self._sensor_types: dict[str, SensorTypeDef] = {}
        self._sensors: list[SensorInstance] = []
        self._terminal_pin_counters: dict[str, int] = {}

    def module_type(self, name: str, capacity: int, pin_format: str) -> "PlcMapper":
        """
        Register a PLC module type.

        Args:
            name: Module type name (e.g. "AI_mA", "DI")
            capacity: Number of sensor channels per module
            pin_format: Pin name format string. Supported placeholders:
                - {ch}: channel number (1-based)
                - {polarity}: polarity suffix from sensor_type polarity map
                - {pin}: pin name from sensor_type pins list

        Returns:
            self for chaining
        """
        self._module_types[name] = ModuleTypeDef(
            name=name, capacity=capacity, pin_format=pin_format
        )
        return self

    def sensor_type(
        self,
        name: str,
        module: str,
        pins: list[str],
        polarity: dict[int, str] | None = None,
    ) -> "PlcMapper":
        """
        Register a sensor type.

        Args:
            name: Sensor type name (e.g. "RTD", "2Wire-mA")
            module: Module type name this sensor connects to
            pins: Pin names for each wire (e.g. ["R+", "RL", "R-"])
            polarity: Optional mapping of pin index to polarity suffix

        Returns:
            self for chaining
        """
        if module not in self._module_types:
            raise ValueError(
                f"Module type '{module}' not registered. "
                f"Register it with module_type() first. "
                f"Available: {list(self._module_types.keys())}"
            )
        self._sensor_types[name] = SensorTypeDef(
            name=name, module=module, pins=tuple(pins), polarity=polarity
        )
        return self

    def sensor(self, tag: str, type: str, cable: str, terminal: str) -> "PlcMapper":
        """
        Add a sensor instance.

        Args:
            tag: Sensor tag (e.g. "TT-01-CX")
            type: Sensor type name (must be registered)
            cable: Cable reference (e.g. "W0102")
            terminal: Terminal ID for connections (e.g. "X007")

        Returns:
            self for chaining
        """
        if type not in self._sensor_types:
            raise ValueError(
                f"Sensor type '{type}' not registered. "
                f"Register it with sensor_type() first. "
                f"Available: {list(self._sensor_types.keys())}"
            )
        self._sensors.append(
            SensorInstance(tag=tag, sensor_type=type, cable=cable, terminal=terminal)
        )
        return self

    def set_terminal_start(self, terminal_id: str, start: int) -> "PlcMapper":
        """
        Seed the terminal pin counter for a specific terminal.

        Args:
            terminal_id: Terminal ID (e.g. "X007")
            start: Starting pin number

        Returns:
            self for chaining
        """
        self._terminal_pin_counters[terminal_id] = start
        return self

    def _next_terminal_pin(self, terminal_id: str) -> str:
        """Get the next available pin number for a terminal."""
        current = self._terminal_pin_counters.get(terminal_id, 1)
        self._terminal_pin_counters[terminal_id] = current + 1
        return str(current)

    def _format_module_pin(
        self,
        module_type: ModuleTypeDef,
        channel: int,
        sensor_type_def: SensorTypeDef,
        pin_index: int,
    ) -> str:
        """Format a module pin name using the module's pin_format template."""
        fmt = module_type.pin_format
        pin_name = (
            sensor_type_def.pins[pin_index]
            if pin_index < len(sensor_type_def.pins)
            else ""
        )
        polarity = ""
        if sensor_type_def.polarity and pin_index in sensor_type_def.polarity:
            polarity = sensor_type_def.polarity[pin_index]

        return fmt.format(ch=channel, polarity=polarity, pin=pin_name)

    def generate_connections(self) -> list[PlcConnection]:
        """
        Allocate sensors to modules and generate connection data.

        Performs bin-packing: sensors are assigned to modules of the
        matching type. When a module reaches capacity, a new module
        is created.

        Returns:
            List of PlcConnection objects, one per wire.
        """
        # Group sensors by module type
        sensors_by_module: dict[str, list[SensorInstance]] = {}
        for s in self._sensors:
            st = self._sensor_types[s.sensor_type]
            mod_name = st.module
            if mod_name not in sensors_by_module:
                sensors_by_module[mod_name] = []
            sensors_by_module[mod_name].append(s)

        connections: list[PlcConnection] = []

        for mod_type_name, sensors in sensors_by_module.items():
            mod_type = self._module_types[mod_type_name]

            for sensor_idx, sensor in enumerate(sensors):
                module_num = (sensor_idx // mod_type.capacity) + 1
                channel = (sensor_idx % mod_type.capacity) + 1
                module_name = f"{mod_type_name}_{module_num}"

                st = self._sensor_types[sensor.sensor_type]

                # Generate one connection per pin/wire
                for pin_idx, pin_name in enumerate(st.pins):
                    module_pin = self._format_module_pin(mod_type, channel, st, pin_idx)
                    terminal_pin = self._next_terminal_pin(sensor.terminal)

                    connections.append(
                        PlcConnection(
                            sensor_tag=sensor.tag,
                            cable=sensor.cable,
                            terminal=sensor.terminal,
                            terminal_pin=terminal_pin,
                            module_name=module_name,
                            module_pin=module_pin,
                            sensor_pin=pin_name,
                        )
                    )

        return connections

    def generate_connections_table(self) -> list[list[str]]:
        """
        Generate connections as a list of string rows (for CSV export).

        Returns:
            List of rows, each row is [sensor_tag, cable, terminal,
            terminal_pin, module_name, module_pin, sensor_pin].
        """
        return [
            [
                c.sensor_tag,
                c.cable,
                c.terminal,
                c.terminal_pin,
                c.module_name,
                c.module_pin,
                c.sensor_pin,
            ]
            for c in self.generate_connections()
        ]

    @property
    def module_count(self) -> dict[str, int]:
        """
        Calculate the number of modules needed per module type.

        Returns:
            Dict mapping module type name to count of modules needed.
        """
        counts: dict[str, int] = {}
        for s in self._sensors:
            st = self._sensor_types[s.sensor_type]
            mod_name = st.module
            counts[mod_name] = counts.get(mod_name, 0) + 1

        return {
            name: math.ceil(count / self._module_types[name].capacity)
            for name, count in counts.items()
        }
