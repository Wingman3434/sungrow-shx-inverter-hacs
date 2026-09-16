"""Sungrow SHx Inverter test_sensor checks."""

from unittest.mock import patch

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from modbus_connection import (
    IllegalDataAddressError,
    ModbusTimeoutError,
    ServerDeviceFailureError,
)
from modbus_connection.mock import MockModbusConnection
from pytest_homeassistant_custom_component.common import MockConfigEntry

from . import DOMAIN, SERIAL
from .common import entity_id


async def test_partial_failure_and_recovery(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    connection: MockModbusConnection,
) -> None:
    """Test partial failure and recovery."""
    coordinator = init_integration.runtime_data
    unit = connection.for_unit(1)
    pv_id = entity_id(entity_registry, "sensor", "mppt1_voltage")
    unit.fail_read(5010, ServerDeviceFailureError(), register_type="input")
    await coordinator.async_refresh_components("pv")
    assert hass.states.get(pv_id).state == STATE_UNAVAILABLE
    assert (
        hass.states.get(
            entity_id(entity_registry, "binary_sensor", "battery_charging")
        ).state
        == "on"
    )
    unit.fail_read(5010, None, register_type="input")
    await coordinator.async_refresh_components("pv")
    # Flush the standard 10-second request-refresh debouncer for this test.
    await coordinator.async_refresh()
    assert hass.states.get(pv_id).state == "230.0"


async def test_total_holds_through_outage(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    connection: MockModbusConnection,
) -> None:
    """Test total holds through outage."""
    coordinator = init_integration.runtime_data
    total_id = entity_id(entity_registry, "sensor", "total_pv_generation")
    before = hass.states.get(total_id).state
    connection.for_unit(1).fail_requests(ModbusTimeoutError())
    await coordinator.async_refresh_components("state")
    assert not coordinator.last_update_success
    assert hass.states.get(total_id).state == STATE_UNAVAILABLE
    assert (
        hass.states.get(entity_id(entity_registry, "sensor", "mppt1_voltage")).state
        == STATE_UNAVAILABLE
    )
    connection.for_unit(1).fail_requests(None)
    await coordinator.async_refresh()
    assert hass.states.get(total_id).state == before


async def test_refused_subsystem_is_never_exposed(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    connection: MockModbusConnection,
    entity_registry: er.EntityRegistry,
) -> None:
    """A block the device refuses is dropped before the platforms are set up."""
    unit = connection.for_unit(1)
    unit.fail_read(2581, IllegalDataAddressError(), register_type="input")
    entry.add_to_hass(hass)
    with patch(
        "custom_components.sungrow_shx_inverter.async_get_unit",
        return_value=unit,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done(wait_background_tasks=True)
    coordinator = entry.runtime_data
    assert "legacy_firmware" not in coordinator.device.components
    assert coordinator.device.absent == {"legacy_firmware"}
    assert (
        entity_registry.async_get_entity_id("sensor", DOMAIN, f"{SERIAL}_version_1")
        is None
    )
    assert (
        entity_registry.async_get_entity_id(
            "sensor", DOMAIN, f"{SERIAL}_daily_pv_generation"
        )
        is not None
    )


async def test_pruned_subsystem_keeps_the_rest_polling(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    connection: MockModbusConnection,
    entity_registry: er.EntityRegistry,
) -> None:
    """Dropping an absent subsystem must not break the poll schedule."""
    coordinator = init_integration.runtime_data
    connection.for_unit(1).fail_read(
        5722, IllegalDataAddressError(), register_type="input"
    )
    await coordinator.async_refresh_components("backup")
    await coordinator.async_refresh()
    assert "backup" not in coordinator.device.components
    assert "backup" in coordinator.device.absent
    assert coordinator.last_update_success
    assert (
        hass.states.get(
            entity_id(entity_registry, "sensor", "daily_pv_generation")
        ).state
        != STATE_UNAVAILABLE
    )
    assert (
        hass.states.get(
            entity_id(entity_registry, "sensor", "total_backup_power")
        ).state
        == STATE_UNAVAILABLE
    )
