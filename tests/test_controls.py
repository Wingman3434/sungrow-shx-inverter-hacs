"""Sungrow SHx Inverter test_controls checks."""

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from modbus_connection import ModbusError
from modbus_connection.mock import MockModbusConnection
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sungrow_shx_inverter.button import BUTTONS, SungrowButton
from custom_components.sungrow_shx_inverter.entity import SungrowEntity
from custom_components.sungrow_shx_inverter.number import NUMBERS
from custom_components.sungrow_shx_inverter.switch import SWITCHES, SungrowSwitch

from .common import entity_id


async def test_number_switch_and_select_writes(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    connection: MockModbusConnection,
) -> None:
    """Test number switch and select writes."""
    unit = connection.for_unit(1)
    with patch(
        "custom_components.sungrow_shx_inverter._vendor.sungrow_shx_inverter.device.sleep",
        new_callable=AsyncMock,
    ):
        await hass.services.async_call(
            "number",
            "set_value",
            {
                "entity_id": entity_id(entity_registry, "number", "battery_min_soc"),
                "value": 20,
            },
            blocking=True,
        )
        assert unit.holding[13058] == 200
        await hass.services.async_call(
            "switch",
            "turn_on",
            {
                "entity_id": entity_id(entity_registry, "switch", "backup_mode"),
            },
            blocking=True,
        )
        assert unit.holding[13074] == 0xAA
        await hass.services.async_call(
            "select",
            "select_option",
            {
                "entity_id": entity_id(entity_registry, "select", "ems_mode"),
                "option": "forced_mode",
            },
            blocking=True,
        )
        assert unit.holding[13049] == 2


async def test_start_stop_commands(
    init_integration: MockConfigEntry, connection: MockModbusConnection
) -> None:
    """Only explicit presses send the write-only command words."""
    for description, expected in zip(BUTTONS, (0xCF, 0xCE), strict=True):
        button = SungrowButton(init_integration.runtime_data, description)
        await button.async_press()
        assert connection.for_unit(1).holding[12999] == expected


async def test_button_error(
    init_integration: MockConfigEntry, connection: MockModbusConnection
) -> None:
    """Surface command failure as a translated action exception."""
    button = SungrowButton(init_integration.runtime_data, BUTTONS[0])
    connection.for_unit(1).fail_write(12999, ModbusError())
    with pytest.raises(HomeAssistantError):
        await button.async_press()


@pytest.mark.parametrize("error", [ValueError("range"), ModbusError("refused")])
async def test_write_errors(
    init_integration: MockConfigEntry, error: Exception
) -> None:
    """Write validation and protocol failures have distinct public exceptions."""
    entity = SungrowEntity(init_integration.runtime_data, NUMBERS[0])
    with (
        patch.object(
            init_integration.runtime_data.device,
            "async_write",
            new_callable=AsyncMock,
            side_effect=error,
        ),
        pytest.raises(
            ServiceValidationError
            if isinstance(error, ValueError)
            else HomeAssistantError
        ),
    ):
        await entity._async_write(20)


async def test_disable_and_unknown_switch(
    init_integration: MockConfigEntry, connection: MockModbusConnection
) -> None:
    """Unknown wire words remain unknown; disabling writes exactly 0x55."""
    switch = SungrowSwitch(init_integration.runtime_data, SWITCHES[0])
    with patch(
        "custom_components.sungrow_shx_inverter._vendor.sungrow_shx_inverter.device.sleep",
        new_callable=AsyncMock,
    ):
        await switch.async_turn_off()
    assert connection.for_unit(1).holding[13074] == 0x55
    connection.for_unit(1).holding[13074] = 1
    await init_integration.runtime_data.device.export_settings.async_update()
    assert switch.is_on is None


async def test_forced_charge_discharge_power_accepts_watt_steps(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    connection: MockModbusConnection,
) -> None:
    """Register 13051 is a 1 W value, so the UI step must not be 100 W."""
    description = next(
        d for d in NUMBERS if d.key == "battery_forced_charge_discharge_power"
    )
    assert description.native_step == 1
    with patch(
        "custom_components.sungrow_shx_inverter._vendor.sungrow_shx_inverter.device.sleep",
        new_callable=AsyncMock,
    ):
        await hass.services.async_call(
            "number",
            "set_value",
            {
                "entity_id": entity_id(
                    entity_registry, "number", "battery_forced_charge_discharge_power"
                ),
                "value": 6750,
            },
            blocking=True,
        )
    assert connection.for_unit(1).holding[13051] == 6750
