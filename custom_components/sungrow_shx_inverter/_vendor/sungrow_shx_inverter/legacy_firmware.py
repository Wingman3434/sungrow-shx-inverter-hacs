"""The legacy firmware subsystem."""

from modbus_connection.model import string

from .model import SungrowComponent


class LegacyFirmware(SungrowComponent):
    """Legacy firmware register fields."""

    register_space = "input"

    version_1 = string(2581, 11)
    """Version 1; zero-based address 2581."""

    version_2 = string(2596, 11)
    """Version 2; zero-based address 2596."""

    version_3 = string(2612, 11)
    """Version 3; zero-based address 2612."""

    version_4_sungrow_battery = string(2628, 11)
    """Version 4 (Sungrow Battery); zero-based address 2628."""
