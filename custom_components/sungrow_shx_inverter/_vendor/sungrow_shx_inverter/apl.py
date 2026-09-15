"""The apl subsystem."""

from modbus_connection.model import integer

from .model import SungrowComponent


class Apl(SungrowComponent):
    """Apl register fields."""

    register_space = "holding"

    apl_shutdown_at_zero_raw = integer(31212, signed=False)
    """APL shutdown at zero raw; zero-based address 31212."""
