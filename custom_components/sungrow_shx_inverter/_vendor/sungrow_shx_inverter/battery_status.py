"""The battery status subsystem."""

from modbus_connection.model import gauge

from .model import SungrowComponent


class BatteryStatus(SungrowComponent):
    """Battery status register fields."""

    register_space = "input"

    battery_level = gauge(13022, 0.1, signed=False, unit="%")
    """Battery level; zero-based address 13022."""

    battery_temperature = gauge(13024, 0.1, signed=True, unit="°C")
    """Battery temperature; zero-based address 13024."""
