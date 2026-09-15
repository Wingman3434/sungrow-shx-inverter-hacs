"""The state subsystem."""

from modbus_connection.model import int32, integer

from .model import SungrowComponent


class State(SungrowComponent):
    """State register fields."""

    register_space = "input"

    running_state_raw = integer(12999, signed=False)
    """Running state raw; zero-based address 12999."""

    power_flow_status = integer(13000, signed=False)
    """Power Flow Status; zero-based address 13000."""

    load_power = int32(13007, word_order="little", nan=0x7FFFFFFF, unit="W")
    """Load power; zero-based address 13007."""
