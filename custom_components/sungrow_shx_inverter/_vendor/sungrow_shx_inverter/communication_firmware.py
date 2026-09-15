"""The communication firmware subsystem."""

from modbus_connection.model import string

from .model import SungrowComponent


class CommunicationFirmware(SungrowComponent):
    """Communication firmware register fields."""

    register_space = "input"

    communication_module_firmware_version = string(13264, 15)
    """Communication Module Firmware Version; zero-based address 13264."""
