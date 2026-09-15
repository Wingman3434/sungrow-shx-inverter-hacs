"""The grid output subsystem."""

from modbus_connection.model import gauge, int32

from .model import SungrowComponent


class GridOutput(SungrowComponent):
    """Grid output register fields."""

    register_space = "input"

    phase_a_current = gauge(13030, 0.1, signed=True, unit="A")
    """Phase A current; zero-based address 13030."""

    phase_b_current = gauge(13031, 0.1, signed=True, unit="A")
    """Phase B current; zero-based address 13031."""

    phase_c_current = gauge(13032, 0.1, signed=True, unit="A")
    """Phase C current; zero-based address 13032."""

    total_active_power = int32(13033, word_order="little", unit="W")
    """Total active power; zero-based address 13033."""
