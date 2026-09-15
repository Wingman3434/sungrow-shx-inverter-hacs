"""The backup subsystem."""

from modbus_connection.model import int32, integer

from .model import SungrowComponent


class Backup(SungrowComponent):
    """Backup register fields."""

    register_space = "input"

    backup_phase_a_power = integer(5722, signed=True, unit="W")
    """Backup phase A power; zero-based address 5722."""

    backup_phase_b_power = integer(5723, signed=True, unit="W")
    """Backup phase B power; zero-based address 5723."""

    backup_phase_c_power = integer(5724, signed=True, unit="W")
    """Backup phase C power; zero-based address 5724."""

    total_backup_power = int32(5725, word_order="little", unit="W")
    """Total backup power; zero-based address 5725."""
