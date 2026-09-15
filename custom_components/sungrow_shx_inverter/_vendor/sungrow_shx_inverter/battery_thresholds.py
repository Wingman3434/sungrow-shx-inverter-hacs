"""The battery thresholds subsystem."""

from modbus_connection.model import gauge

from .model import SungrowComponent, bounded


class BatteryThresholds(SungrowComponent):
    """Battery thresholds register fields."""

    register_space = "holding"

    battery_charging_start_power = gauge(
        33148, 10, signed=False, nan=0xFFFF, unit="W", writable=bounded(0, 1000, 10)
    )
    """Battery charging start power; zero-based address 33148."""

    battery_discharging_start_power = gauge(
        33149, 10, signed=False, nan=0xFFFF, unit="W", writable=bounded(0, 1000, 10)
    )
    """Battery discharging start power; zero-based address 33149."""
