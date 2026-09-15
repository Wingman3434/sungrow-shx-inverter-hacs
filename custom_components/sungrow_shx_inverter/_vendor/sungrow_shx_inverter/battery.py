"""The battery subsystem."""

from modbus_connection.model import gauge, int32

from .model import SungrowComponent


class Battery(SungrowComponent):
    """Battery register fields."""

    register_space = "input"

    battery_power = int32(5213, word_order="little", unit="W")
    """Battery power; zero-based address 5213."""

    battery_current = gauge(5630, 0.1, signed=True, unit="A")
    """Battery current; zero-based address 5630."""

    battery_voltage = gauge(13019, 0.1, signed=False, unit="V")
    """Battery voltage; zero-based address 13019."""
