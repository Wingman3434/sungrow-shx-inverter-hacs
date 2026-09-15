"""The export bounds subsystem."""

from modbus_connection.model import gauge

from .model import SungrowComponent


class ExportBounds(SungrowComponent):
    """Export bounds register fields."""

    register_space = "input"

    export_power_limit_min = gauge(5621, 10, signed=False, nan=0xFFFF, unit="W")
    """Export power limit min; zero-based address 5621."""

    export_power_limit_max = gauge(5622, 10, signed=False, nan=0xFFFF, unit="W")
    """Export power limit max; zero-based address 5622."""
