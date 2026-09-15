"""The battery settings subsystem."""

from modbus_connection.model import gauge, integer

from .model import SungrowComponent, bounded, one_of


class BatterySettings(SungrowComponent):
    """Battery settings register fields."""

    register_space = "holding"

    ems_mode_selection_raw = integer(13049, signed=False, writable=one_of(0, 2, 3, 4))
    """EMS mode selection raw; zero-based address 13049."""

    battery_forced_charge_discharge_cmd_raw = integer(
        13050, signed=False, writable=one_of(0xAA, 0xBB, 0xCC)
    )
    """Battery forced charge discharge cmd raw; zero-based address 13050."""

    battery_forced_charge_discharge_power = integer(
        13051, signed=False, unit="W", writable=bounded(0, 65535)
    )
    """Battery forced charge discharge power; zero-based address 13051."""

    battery_max_soc = gauge(
        13057, 0.1, signed=False, unit="%", writable=bounded(50, 100)
    )
    """Battery max SoC; zero-based address 13057."""

    battery_min_soc = gauge(13058, 0.1, signed=False, unit="%", writable=bounded(0, 50))
    """Battery min SoC; zero-based address 13058."""

    battery_reserved_soc_for_backup = integer(
        13099, signed=False, unit="%", writable=bounded(0, 100)
    )
    """Battery reserved SoC for backup; zero-based address 13099."""
