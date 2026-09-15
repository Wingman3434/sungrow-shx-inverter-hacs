"""The meter electrical subsystem."""

from modbus_connection.model import gauge

from .model import SungrowComponent


class MeterElectrical(SungrowComponent):
    """Meter electrical register fields."""

    register_space = "input"

    meter_phase_a_voltage = gauge(5740, 0.1, signed=True, nan=0x7FFF, unit="V")
    """Meter phase A voltage; zero-based address 5740."""

    meter_phase_b_voltage = gauge(5741, 0.1, signed=True, nan=0x7FFF, unit="V")
    """Meter phase B voltage; zero-based address 5741."""

    meter_phase_c_voltage = gauge(5742, 0.1, signed=True, nan=0x7FFF, unit="V")
    """Meter phase C voltage; zero-based address 5742."""

    meter_phase_a_current = gauge(5743, 0.01, signed=False, nan=0xFFFF, unit="A")
    """Meter phase A current; zero-based address 5743."""

    meter_phase_b_current = gauge(5744, 0.01, signed=False, nan=0xFFFF, unit="A")
    """Meter phase B current; zero-based address 5744."""

    meter_phase_c_current = gauge(5745, 0.01, signed=False, nan=0xFFFF, unit="A")
    """Meter phase C current; zero-based address 5745."""
