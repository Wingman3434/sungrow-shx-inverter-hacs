"""Shared mock transport and entry fixtures."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from modbus_connection.mock import MockModbusConnection
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from . import DOMAIN, SERIAL, USER_INPUT, seed


@pytest.fixture
def connection() -> MockModbusConnection:
    """An in-memory device, with no socket or hardware access."""
    conn = MockModbusConnection()
    seed(conn.for_unit(1))
    return conn


@pytest.fixture
def entry() -> MockConfigEntry:
    """A configured inverter."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=SERIAL,
        data=USER_INPUT,
        title="Sungrow SHx Inverter SH10RT",
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant, entry: MockConfigEntry, connection: MockModbusConnection
) -> MockConfigEntry:
    """Set up all six platforms with the real library over the mock."""
    entry.add_to_hass(hass)
    with patch(
        "custom_components.sungrow_shx_inverter.async_get_unit",
        return_value=connection.for_unit(1),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done(wait_background_tasks=True)
    return entry


@pytest.fixture(autouse=True)
def enable_custom(enable_custom_integrations):
    """Enable this custom integration."""
    return
