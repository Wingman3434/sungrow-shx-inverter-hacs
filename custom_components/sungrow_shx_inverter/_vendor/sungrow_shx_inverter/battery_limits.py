"""The battery limits subsystem."""

from modbus_connection.model import gauge

from .model import SungrowComponent, bounded


class BatteryLimits(SungrowComponent):
    """Battery limits register fields."""

    register_space = "holding"

    battery_max_charge_power = gauge(
        33046, 10, signed=False, unit="W", writable=bounded(10, 655350, 10)
    )
    """Battery max charge power; zero-based address 33046."""

    battery_max_discharge_power = gauge(
        33047, 10, signed=False, unit="W", writable=bounded(10, 655350, 10)
    )
    """Battery max discharge power; zero-based address 33047."""
