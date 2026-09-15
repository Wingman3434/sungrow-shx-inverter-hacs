"""Sungrow SHx Inverter test_diagnostics checks."""

from homeassistant.core import HomeAssistant
from modbus_connection import ModbusTimeoutError
from modbus_connection.mock import MockModbusConnection
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sungrow_shx_inverter.diagnostics import (
    async_get_config_entry_diagnostics,
)

from . import SERIAL


async def test_diagnostics_redact_raw_serial_and_errors(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    connection: MockModbusConnection,
) -> None:
    """Test diagnostics redact raw serial and errors."""
    result = await async_get_config_entry_diagnostics(hass, init_integration)
    assert not any(a in result["raw"]["input"] for a in range(4989, 4999))
    assert SERIAL not in str(result)
    assert "192.0.2.2" not in str(result)
    connection.for_unit(1).fail_requests(ModbusTimeoutError("host=192.0.2.2"))
    result = await async_get_config_entry_diagnostics(hass, init_integration)
    assert result["read_error"] == "ModbusTimeoutError"
    assert result["raw"] == {}
    assert "192.0.2.2" not in str(result)
