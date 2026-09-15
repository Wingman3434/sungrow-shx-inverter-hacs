"""The battery firmware subsystem."""

from modbus_connection.model import string

from .model import SungrowComponent


class BatteryFirmware(SungrowComponent):
    """Battery firmware register fields."""

    register_space = "input"

    battery_firmware_version = string(13279, 15)
    """Battery Firmware Version; zero-based address 13279."""
