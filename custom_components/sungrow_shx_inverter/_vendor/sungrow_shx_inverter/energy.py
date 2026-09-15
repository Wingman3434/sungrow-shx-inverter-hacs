"""The energy subsystem."""

from modbus_connection.model import gauge, uint32

from .model import SungrowComponent


class Energy(SungrowComponent):
    """Energy register fields."""

    register_space = "input"

    daily_pv_generation = gauge(13001, 0.1, signed=False, unit="kWh")
    """Daily PV generation; zero-based address 13001."""

    total_pv_generation = uint32(13002, scale=0.1, word_order="little", unit="kWh")
    """Total PV generation; zero-based address 13002."""

    daily_exported_energy_from_pv = gauge(13004, 0.1, signed=False, unit="kWh")
    """Daily exported energy from PV; zero-based address 13004."""

    total_exported_energy_from_pv = uint32(
        13005, scale=0.1, word_order="little", unit="kWh"
    )
    """Total exported energy from PV; zero-based address 13005."""

    daily_battery_charge_from_pv = gauge(13011, 0.1, signed=False, unit="kWh")
    """Daily battery charge from PV; zero-based address 13011."""

    total_battery_charge_from_pv = uint32(
        13012, scale=0.1, word_order="little", unit="kWh"
    )
    """Total battery charge from PV; zero-based address 13012."""

    daily_direct_energy_consumption = gauge(13016, 0.1, signed=False, unit="kWh")
    """Daily direct energy consumption; zero-based address 13016."""

    total_direct_energy_consumption = uint32(
        13017, scale=0.1, word_order="little", unit="kWh"
    )
    """Total direct energy consumption; zero-based address 13017."""

    daily_battery_discharge = gauge(13025, 0.1, signed=False, unit="kWh")
    """Daily battery discharge; zero-based address 13025."""

    total_battery_discharge = uint32(13026, scale=0.1, word_order="little", unit="kWh")
    """Total battery discharge; zero-based address 13026."""

    daily_imported_energy = gauge(13035, 0.1, signed=False, unit="kWh")
    """Daily imported energy; zero-based address 13035."""

    total_imported_energy = uint32(13036, scale=0.1, word_order="little", unit="kWh")
    """Total imported energy; zero-based address 13036."""

    daily_battery_charge = gauge(13039, 0.1, signed=False, unit="kWh")
    """Daily battery charge; zero-based address 13039."""

    total_battery_charge = uint32(13040, scale=0.1, word_order="little", unit="kWh")
    """Total battery charge; zero-based address 13040."""

    daily_exported_energy = gauge(13044, 0.1, signed=False, unit="kWh")
    """Daily exported energy; zero-based address 13044."""

    total_exported_energy = uint32(13045, scale=0.1, word_order="little", unit="kWh")
    """Total exported energy; zero-based address 13045."""
