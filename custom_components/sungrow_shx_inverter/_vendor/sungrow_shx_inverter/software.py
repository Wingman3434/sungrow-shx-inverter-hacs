"""The software subsystem."""

from modbus_connection.model import string, uint32

from .model import SungrowComponent


class Software(SungrowComponent):
    """Software register fields."""

    register_space = "input"

    protocol_version = uint32(4951, word_order="little")
    """Protocol Version; zero-based address 4951."""

    arm_software = string(4953, 15)
    """Arm Software; zero-based address 4953."""

    dsp_software = string(4968, 15)
    """DSP Software; zero-based address 4968."""
