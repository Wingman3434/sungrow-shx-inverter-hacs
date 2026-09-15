"""The battery health subsystem."""

from modbus_connection.model import gauge

from .model import SungrowComponent


class BatteryHealth(SungrowComponent):
    """Battery health register fields."""

    register_space = "input"

    battery_state_of_health = gauge(13023, 0.1, signed=False, unit="%")
    """Battery state of health; zero-based address 13023."""
