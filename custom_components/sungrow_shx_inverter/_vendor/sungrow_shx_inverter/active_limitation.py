"""The active limitation subsystem."""

from modbus_connection.model import gauge, integer

from .model import SungrowComponent


class ActiveLimitation(SungrowComponent):
    """Active limitation register fields."""

    register_space = "holding"

    active_power_limitation_raw = integer(13088, signed=False)
    """Active power limitation raw; zero-based address 13088."""

    active_power_limitation_ratio_raw = gauge(13089, 0.1, signed=False, unit="%")
    """Active power limitation ratio raw; zero-based address 13089."""
