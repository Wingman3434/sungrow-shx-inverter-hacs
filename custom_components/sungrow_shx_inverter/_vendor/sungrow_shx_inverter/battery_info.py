"""The battery info subsystem."""

from modbus_connection.model import gauge, integer

from .model import SungrowComponent


class BatteryInfo(SungrowComponent):
    """Battery info register fields."""

    register_space = "input"

    bdc_rated_power = gauge(5627, 100, signed=False, unit="W")
    """BDC rated power; zero-based address 5627."""

    bms_max_charging_current = integer(5634, signed=False, unit="A")
    """BMS max. charging current; zero-based address 5634."""

    bms_max_discharging_current = integer(5635, signed=False, unit="A")
    """BMS max. discharging current; zero-based address 5635."""

    battery_capacity_high_precision = gauge(5638, 0.01, signed=False, unit="kWh")
    """Battery capacity high precision; zero-based address 5638."""
