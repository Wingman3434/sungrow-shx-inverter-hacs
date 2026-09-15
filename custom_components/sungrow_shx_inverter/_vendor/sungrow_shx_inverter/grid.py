"""The grid subsystem."""

from modbus_connection.model import gauge, int32

from .model import SungrowComponent


class Grid(SungrowComponent):
    """Grid register fields."""

    register_space = "input"

    phase_a_voltage = gauge(5018, 0.1, signed=False, unit="V")
    """Phase A voltage; zero-based address 5018."""

    phase_b_voltage = gauge(5019, 0.1, signed=False, unit="V")
    """Phase B voltage; zero-based address 5019."""

    phase_c_voltage = gauge(5020, 0.1, signed=False, unit="V")
    """Phase C voltage; zero-based address 5020."""

    reactive_power = int32(5032, word_order="little", unit="var")
    """Reactive power; zero-based address 5032."""

    power_factor = gauge(5034, 0.001, signed=True)
    """Power factor; zero-based address 5034."""

    grid_frequency = gauge(5241, 0.01, signed=False, unit="Hz")
    """Grid frequency; zero-based address 5241."""
