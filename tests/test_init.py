"""Sungrow SHx Inverter test_init checks."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from modbus_connection import ModbusError, ModbusTimeoutError
from modbus_connection.mock import MockModbusConnection
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sungrow_shx_inverter._vendor.sungrow_shx_inverter import (
    SungrowSHxInverter,
    UpdateReport,
)

from . import DOMAIN, SERIAL, USER_INPUT, seed
from .common import entity_id


async def test_setup_and_unload(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test setup and unload."""
    assert init_integration.state is ConfigEntryState.LOADED
    entities = er.async_entries_for_config_entry(
        entity_registry, init_integration.entry_id
    )
    assert {entry.domain for entry in entities} == {
        "sensor",
        "binary_sensor",
        "number",
        "switch",
        "select",
        "button",
    }
    voltage = hass.states.get(entity_id(entity_registry, "sensor", "mppt1_voltage"))
    assert voltage.state == "230.0"
    assert (
        hass.states.get(
            entity_id(entity_registry, "binary_sensor", "battery_charging")
        ).state
        == "on"
    )
    assert not any("mppt3" in entry.unique_id for entry in entities)
    assert await hass.config_entries.async_unload(init_integration.entry_id)
    assert init_integration.state is ConfigEntryState.NOT_LOADED


async def test_entities_are_grouped_by_sub_device(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
) -> None:
    """Each subsystem reports on its own device page, linked to the inverter."""
    parent_name = "Sungrow SHx Inverter SH10RT"
    devices = dr.async_entries_for_config_entry(
        device_registry, init_integration.entry_id
    )
    by_name = {device.name: device for device in devices}
    assert parent_name in by_name
    for suffix in ("PV", "Battery", "Meter", "Energy", "Backup"):
        assert f"SH10RT {suffix}" in by_name
    parent = by_name[parent_name]
    for name, device in by_name.items():
        if name != parent_name:
            assert device.via_device_id == parent.id
    expected = {
        "mppt1_voltage": "SH10RT PV",
        "battery_power": "SH10RT Battery",
        "meter_active_power": "SH10RT Meter",
        "daily_pv_generation": "SH10RT Energy",
        "backup_phase_a_power": "SH10RT Backup",
        "phase_a_voltage": parent_name,
    }
    for key, group in expected.items():
        registry_entry = entity_registry.async_get(
            entity_id(entity_registry, "sensor", key)
        )
        assert device_registry.async_get(registry_entry.device_id).name == group, key
    preset = entity_registry.async_get(
        entity_id(entity_registry, "select", "operating_preset")
    )
    assert device_registry.async_get(preset.device_id).id == parent.id


async def test_setup_unreachable(
    hass: HomeAssistant, entry: MockConfigEntry, connection: MockModbusConnection
) -> None:
    """Test setup unreachable."""
    connection.for_unit(1).fail_requests(ModbusTimeoutError())
    entry.add_to_hass(hass)
    with patch(
        "custom_components.sungrow_shx_inverter.async_get_unit",
        return_value=connection.for_unit(1),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY


@pytest.mark.parametrize(
    "mode", ["different_serial", "unsupported", "all_components_refused"]
)
async def test_setup_failure_modes(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    connection: MockModbusConnection,
    mode: str,
) -> None:
    """Distinguish an unexpected device from a temporarily unavailable register map."""
    unit = connection.for_unit(1)
    if mode == "different_serial":
        unit.input[4989] = [0x4F54, 0x4845, 0x5200] + [0] * 7
    elif mode == "unsupported":
        unit.input[4999] = 0xFFFF
    else:
        # Identity remains available, but every subsequent component read refuses.

        entry.add_to_hass(hass)
        with (
            patch(
                "custom_components.sungrow_shx_inverter.async_get_unit",
                return_value=unit,
            ),
            patch.object(
                SungrowSHxInverter,
                "async_update_components",
                return_value=UpdateReport(set(), {"state": ModbusError()}),
            ),
        ):
            await hass.config_entries.async_setup(entry.entry_id)
        assert entry.state is ConfigEntryState.SETUP_RETRY
        return
    entry.add_to_hass(hass)
    with patch(
        "custom_components.sungrow_shx_inverter.async_get_unit",
        return_value=unit,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_ERROR


async def test_configured_battery_cap(
    hass: HomeAssistant, entry: MockConfigEntry, connection: MockModbusConnection
) -> None:
    """Installation options limit controls below the inverter's BDC rating."""
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options={"battery_max_power": 3500})
    with patch(
        "custom_components.sungrow_shx_inverter.async_get_unit",
        return_value=connection.for_unit(1),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.runtime_data.device.battery_max_power == 3500


async def test_two_units_share_transport_and_unload_independently(
    hass: HomeAssistant, connection: MockModbusConnection
) -> None:
    """Two serials use one shared link without duplicate IDs or early close."""
    serial2 = "SGTEST12346"
    unit2 = connection.for_unit(2)
    seed(unit2)
    raw = serial2.encode().ljust(20, b"\0")
    unit2.input[4989] = [int.from_bytes(raw[i : i + 2], "big") for i in range(0, 20, 2)]
    entries = [
        MockConfigEntry(
            domain=DOMAIN, unique_id=SERIAL, data=USER_INPUT, title="Inverter 1"
        ),
        MockConfigEntry(
            domain=DOMAIN,
            unique_id=serial2,
            data={**USER_INPUT, "unit_id": 2},
            title="Inverter 2",
        ),
    ]
    with (
        patch(
            "homeassistant.components.modbus.connection.ModbusConnection",
            return_value=connection,
        ) as factory,
        patch.object(connection, "close", wraps=connection.close) as close,
    ):
        for entry in entries:
            entry.add_to_hass(hass)
            assert await hass.config_entries.async_setup(entry.entry_id)
        assert factory.call_count == 1
        close.assert_not_awaited()
        assert await hass.config_entries.async_unload(entries[0].entry_id)
        close.assert_not_awaited()
        assert entries[1].state is ConfigEntryState.LOADED
        assert await hass.config_entries.async_unload(entries[1].entry_id)
        close.assert_awaited_once()
