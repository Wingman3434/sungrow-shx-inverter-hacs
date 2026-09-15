"""The pv subsystem."""

from modbus_connection.model import gauge, uint32

from .model import SungrowComponent


class Pv(SungrowComponent):
    """Pv register fields."""

    register_space = "input"

    mppt1_voltage = gauge(5010, 0.1, signed=False, unit="V")
    """MPPT1 voltage; zero-based address 5010."""

    mppt1_current = gauge(5011, 0.1, signed=False, unit="A")
    """MPPT1 current; zero-based address 5011."""

    mppt2_voltage = gauge(5012, 0.1, signed=False, unit="V")
    """MPPT2 voltage; zero-based address 5012."""

    mppt2_current = gauge(5013, 0.1, signed=False, unit="A")
    """MPPT2 current; zero-based address 5013."""

    mppt3_voltage = gauge(5014, 0.1, signed=False, nan=0xFFFF, unit="V")
    """MPPT3 voltage; zero-based address 5014."""

    mppt3_current = gauge(5015, 0.1, signed=False, nan=0xFFFF, unit="A")
    """MPPT3 current; zero-based address 5015."""

    total_dc_power = uint32(5016, word_order="little", unit="W")
    """Total DC power; zero-based address 5016."""

    mppt4_voltage = gauge(5114, 0.1, signed=False, nan=0xFFFF, unit="V")
    """MPPT4 voltage; zero-based address 5114."""

    mppt4_current = gauge(5115, 0.1, signed=False, nan=0xFFFF, unit="A")
    """MPPT4 current; zero-based address 5115."""
