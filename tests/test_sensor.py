"""Sungrow SHx Inverter test_sensor checks."""

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from modbus_connection import IllegalDataAddressError, ModbusTimeoutError
from modbus_connection.mock import MockModbusConnection
from pytest_homeassistant_custom_component.common import MockConfigEntry

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
    unit.fail_read(5010, IllegalDataAddressError(), register_type="input")
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
