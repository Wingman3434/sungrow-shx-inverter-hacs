"""The grid flow subsystem."""

from modbus_connection.model import int32

from .model import SungrowComponent


class GridFlow(SungrowComponent):
    """Grid flow register fields."""

    register_space = "input"

    export_power_raw = int32(13009, word_order="little", nan=0x7FFFFFFF, unit="W")
    """Export power raw; zero-based address 13009."""
