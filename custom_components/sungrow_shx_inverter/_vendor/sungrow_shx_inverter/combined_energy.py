"""The combined energy subsystem."""

from modbus_connection.model import gauge, uint32

from .model import SungrowComponent


class CombinedEnergy(SungrowComponent):
    """Combined energy register fields."""

    register_space = "input"

    daily_pv_generation_battery_discharge = gauge(5002, 0.1, signed=False, unit="kWh")
    """Daily PV generation & battery discharge; zero-based address 5002."""

    total_pv_generation_battery_discharge = uint32(
        5003, scale=0.1, word_order="little", unit="kWh"
    )
    """Total PV generation & battery discharge; zero-based address 5003."""
