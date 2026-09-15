"""The inverter firmware subsystem."""

from modbus_connection.model import string

from .model import SungrowComponent


class InverterFirmware(SungrowComponent):
    """Inverter firmware register fields."""

    register_space = "input"

    inverter_firmware_version = string(13249, 15)
    """Inverter Firmware Version; zero-based address 13249."""
