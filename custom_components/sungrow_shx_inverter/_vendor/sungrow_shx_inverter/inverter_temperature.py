"""The inverter temperature subsystem."""

from modbus_connection.model import gauge

from .model import SungrowComponent


class InverterTemperature(SungrowComponent):
    """Inverter temperature register fields."""

    register_space = "input"

    inverter_temperature = gauge(5007, 0.1, signed=True, unit="°C")
    """Inverter temperature; zero-based address 5007."""
