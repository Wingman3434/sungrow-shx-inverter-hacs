"""The load settings subsystem."""

from modbus_connection.model import integer

from .model import SungrowComponent, one_of


class LoadSettings(SungrowComponent):
    """Load settings register fields."""

    register_space = "holding"

    load_adjustment_mode_selection_raw = integer(
        13001, signed=False, writable=one_of(0, 1, 2, 3)
    )
    """Load adjustment mode selection raw; zero-based address 13001."""

    load_adjustment_mode_enable_raw = integer(
        13010, signed=False, writable=one_of(0xAA, 0x55)
    )
    """Load adjustment mode enable raw; zero-based address 13010."""
