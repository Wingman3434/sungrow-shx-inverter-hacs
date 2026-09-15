"""Exercise real config flows using temporary shared units."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from modbus_connection import ModbusTimeoutError
from modbus_connection.mock import MockModbusConnection, MockModbusUnit
from probatio.codecs.fields import to_field_list
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from . import DOMAIN, SERIAL, USER_INPUT, seed


def temporary(connection: MockModbusConnection):
    """Patch the supported temporary-unit context without owning a connection."""

    @asynccontextmanager
    async def acquire(*args, **kwargs) -> AsyncIterator[MockModbusUnit]:
        """Acquire."""
        yield connection.for_unit(1)

    return patch(
        "custom_components.sungrow_shx_inverter.config_flow.async_get_temporary_unit",
        side_effect=acquire,
    )


async def test_form(hass: HomeAssistant) -> None:
    """Test form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}


async def test_form_schema_serializes_for_frontend(hass: HomeAssistant) -> None:
    """The settings form must serialize for the UI instead of returning HTTP 500.

    Home Assistant serializes ``data_schema`` with probatio's ``to_field_list``
    before sending it to the frontend. A bare callable validator (for example
    ``str.strip``) raises ``ValueError: unable to serialize schema`` there, which
    the browser surfaces as "Config flow could not be loaded: 500".
    """
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    fields = to_field_list(
        result["data_schema"], custom_serializer=cv.custom_serializer
    )
    assert fields


async def test_create_and_duplicate(
    hass: HomeAssistant, connection: MockModbusConnection
) -> None:
    """Test create and duplicate."""
    writes = []
    connection.for_unit(1).on_write(writes.append)
    with (
        temporary(connection),
        patch(
            "custom_components.sungrow_shx_inverter.async_setup_entry",
            new_callable=AsyncMock,
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=USER_INPUT
        )
        await hass.async_block_till_done()
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["result"].unique_id == SERIAL
        assert result["title"] == "Sungrow SHx Inverter SH10RT"
        duplicate = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=USER_INPUT
        )
        assert duplicate["reason"] == "already_configured"
    assert not writes


@pytest.mark.parametrize(
    ("code", "timeout", "error"),
    [
        (0xFFFF, False, "unsupported_device"),
        (0x0E03, True, "cannot_connect"),
    ],
)
async def test_errors_and_recovery(
    hass: HomeAssistant,
    connection: MockModbusConnection,
    code: int,
    timeout: bool,
    error: str,
) -> None:
    """Test errors and recovery."""
    unit = connection.for_unit(1)
    unit.input[4999] = code
    if timeout:
        unit.fail_requests(ModbusTimeoutError())
    with (
        temporary(connection),
        patch(
            "custom_components.sungrow_shx_inverter.async_setup_entry",
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=USER_INPUT
        )
        assert result["errors"] == {"base": error}
        unit.fail_requests(None)
        seed(unit)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        await hass.async_block_till_done()


async def test_reconfigure(
    hass: HomeAssistant, entry: MockConfigEntry, connection: MockModbusConnection
) -> None:
    """Test reconfigure."""
    entry.add_to_hass(hass)
    with (
        temporary(connection),
        patch(
            "homeassistant.config_entries.ConfigEntries.async_reload", return_value=True
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        assert result["step_id"] == "reconfigure"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {**USER_INPUT, "host": "192.0.2.3"}
        )
        assert result["reason"] == "reconfigure_successful"
        assert entry.data["host"] == "192.0.2.3"


async def test_reconfigure_wrong_device(
    hass: HomeAssistant, entry: MockConfigEntry, connection: MockModbusConnection
) -> None:
    """Test reconfigure wrong device."""
    entry.add_to_hass(hass)
    connection.for_unit(1).input[4989] = [0x4F54, 0x4845, 0x5200] + [0] * 7
    with temporary(connection):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
            data=USER_INPUT,
        )
        assert result["reason"] == "unique_id_mismatch"


async def test_options_set_and_clear(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    """Battery caps can be changed and removed without becoming connection data."""
    entry.add_to_hass(hass)
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_reload", return_value=True
    ):
        form = await hass.config_entries.options.async_init(entry.entry_id)
        assert form["type"] is FlowResultType.FORM
        result = await hass.config_entries.options.async_configure(
            form["flow_id"], {"battery_max_power": 3500}
        )
        await hass.async_block_till_done()
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert entry.options == {"battery_max_power": 3500}
        assert "battery_max_power" not in entry.data
        form = await hass.config_entries.options.async_init(entry.entry_id)
        await hass.config_entries.options.async_configure(form["flow_id"], {})
        await hass.async_block_till_done()
        assert entry.options == {}


async def test_connection_conflict(hass: HomeAssistant) -> None:
    """The shared owner rejecting a link is a recoverable form error."""
    with patch(
        "custom_components.sungrow_shx_inverter.config_flow.async_get_temporary_unit",
        side_effect=HomeAssistantError("conflicting link settings"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=USER_INPUT
        )
    assert result["errors"] == {"base": "cannot_connect"}


async def test_millisecond_gap(
    hass: HomeAssistant, connection: MockModbusConnection
) -> None:
    """A source-recommended 5 ms gap survives UI validation unchanged."""
    with (
        temporary(connection),
        patch(
            "custom_components.sungrow_shx_inverter.async_setup_entry",
            return_value=True,
        ),
    ):
        form = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            form["flow_id"], {**USER_INPUT, "message_wait": 0.005}
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["message_wait"] == 0.005
