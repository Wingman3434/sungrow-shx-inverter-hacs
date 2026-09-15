"""The identity subsystem."""

from modbus_connection.model import gauge, integer, string

from .model import SungrowComponent


class Identity(SungrowComponent):
    """Identity register fields."""

    register_space = "input"

    inverter_serial = string(4989, 10)
    """inverter serial; zero-based address 4989."""

    device_type_code = integer(4999, signed=False)
    """device type code; zero-based address 4999."""

    inverter_rated_output = gauge(5000, 100, signed=False, unit="W")
    """Inverter rated output; zero-based address 5000."""
