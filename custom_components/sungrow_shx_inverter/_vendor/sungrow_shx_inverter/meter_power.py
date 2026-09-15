"""The meter power subsystem."""

from modbus_connection.model import int32

from .model import SungrowComponent


class MeterPower(SungrowComponent):
    """Meter power register fields."""

    register_space = "input"

    meter_active_power = int32(5600, word_order="little", nan=0x7FFFFFFF, unit="W")
    """Meter active power; zero-based address 5600."""

    meter_phase_a_active_power = int32(
        5602, word_order="little", nan=0x7FFFFFFF, unit="W"
    )
    """Meter phase A active power; zero-based address 5602."""

    meter_phase_b_active_power = int32(
        5604, word_order="little", nan=0x7FFFFFFF, unit="W"
    )
    """Meter phase B active power; zero-based address 5604."""

    meter_phase_c_active_power = int32(
        5606, word_order="little", nan=0x7FFFFFFF, unit="W"
    )
    """Meter phase C active power; zero-based address 5606."""
