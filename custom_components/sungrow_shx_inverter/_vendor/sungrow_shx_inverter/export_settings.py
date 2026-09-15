"""The export settings subsystem."""

from modbus_connection.model import integer

from .model import SungrowComponent, bounded, one_of


class ExportSettings(SungrowComponent):
    """Export settings register fields."""

    register_space = "holding"

    export_power_limit = integer(
        13073, signed=False, unit="W", writable=bounded(0, 65535)
    )
    """Export power limit; zero-based address 13073."""

    backup_mode_raw = integer(13074, signed=False, writable=one_of(0xAA, 0x55))
    """Backup mode raw; zero-based address 13074."""

    export_power_limit_mode_raw = integer(
        13086, signed=False, writable=one_of(0xAA, 0x55)
    )
    """Export power limit mode raw; zero-based address 13086."""
