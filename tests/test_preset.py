"""Mode presets reproduce the source scenes over the mock transport."""

import logging
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from modbus_connection.mock import MockModbusConnection, WriteEvent
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sungrow_shx_inverter.presets import PRESETS

from .common import entity_id

SLEEP = (
    "custom_components.sungrow_shx_inverter._vendor.sungrow_shx_inverter.device.sleep"
)


@pytest.fixture
def preset_entity_id(entity_registry: er.EntityRegistry) -> str:
    """Entity id of the operating-preset selector."""
    return entity_id(entity_registry, "select", "operating_preset")


@pytest.mark.parametrize(
    ("preset", "expected"),
    [
        (
            "self_consumption_max_battery_discharge",
            {13049: 0, 13050: 0xCC, 33047: 1000},
        ),
        (
            "self_consumption_no_battery_discharge",
            {13049: 0, 13050: 0xCC, 33047: 1},
        ),
        ("zero_export", {13086: 0xAA, 13073: 0}),
        ("max_export", {13086: 0xAA, 13073: 10000}),
        ("battery_bypass", {13049: 2, 13050: 0xCC}),
        ("battery_forced_discharge", {13049: 2, 13050: 0xBB}),
        ("battery_forced_charge", {13049: 2, 13050: 0xAA}),
    ],
)
async def test_preset_writes_the_scene_registers(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    preset_entity_id: str,
    connection: MockModbusConnection,
    preset: str,
    expected: dict[int, int],
) -> None:
    """Each preset writes exactly the registers the old scenes wrote."""
    with patch(SLEEP, new_callable=AsyncMock):
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": preset_entity_id, "option": preset},
            blocking=True,
        )
    unit = connection.for_unit(1)
    for address, value in expected.items():
        assert unit.holding[address] == value, f"{preset}: holding {address}"


async def test_preset_options_and_reported_state(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """The selector exposes every preset and reports the applied one."""
    result = entity_id(entity_registry, "select", "operating_preset")
    before = hass.states.get(result)
    assert before is not None
    assert set(before.attributes["options"]) == set(PRESETS)
    with patch(SLEEP, new_callable=AsyncMock):
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": result, "option": "battery_bypass"},
            blocking=True,
        )
    assert hass.states.get(result).state == "battery_bypass"


async def test_set_preset_service_matches_the_selector(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    preset_entity_id: str,
    connection: MockModbusConnection,
) -> None:
    """The service applies the same sequence as the selector."""
    with patch(SLEEP, new_callable=AsyncMock):
        await hass.services.async_call(
            "sungrow_shx_inverter",
            "set_preset",
            {"entity_id": preset_entity_id, "preset": "zero_export"},
            blocking=True,
        )
    unit = connection.for_unit(1)
    assert unit.holding[13086] == 0xAA
    assert unit.holding[13073] == 0


async def test_maximum_step_accepts_the_inverter_cap(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    preset_entity_id: str,
    connection: MockModbusConnection,
) -> None:
    """A maximum step succeeds when the inverter caps it below the request."""
    unit = connection.for_unit(1)

    def cap(event: WriteEvent) -> None:
        if event.register_type == "holding" and event.address == 33047:
            if int(event.values[0]) > 600:
                unit.holding[33047] = 600  # the inverter caps at 6000 W

    unit.on_write(cap)
    with patch(SLEEP, new_callable=AsyncMock):
        await hass.services.async_call(
            "select",
            "select_option",
            {
                "entity_id": preset_entity_id,
                "option": "self_consumption_max_battery_discharge",
            },
            blocking=True,
        )
    assert unit.holding[33047] == 600
    assert (
        hass.states.get(preset_entity_id).state
        == "self_consumption_max_battery_discharge"
    )


async def test_explicit_value_still_requires_confirmation(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    preset_entity_id: str,
    connection: MockModbusConnection,
) -> None:
    """A fixed value that the inverter silently changes is still an error."""
    unit = connection.for_unit(1)
    unit.holding[33047] = 1230

    def ignore(event: WriteEvent) -> None:
        if event.register_type == "holding" and event.address == 33047:
            unit.holding[33047] = 1230

    unit.on_write(ignore)
    with (
        patch(SLEEP, new_callable=AsyncMock),
        pytest.raises(HomeAssistantError),
    ):
        await hass.services.async_call(
            "select",
            "select_option",
            {
                "entity_id": preset_entity_id,
                "option": "self_consumption_no_battery_discharge",
            },
            blocking=True,
        )


async def test_max_export_requires_reported_bounds(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    preset_entity_id: str,
    connection: MockModbusConnection,
) -> None:
    """With no reported export bound, max_export fails loudly, not silently."""
    connection.for_unit(1).input[5622] = 0xFFFF
    await init_integration.runtime_data.async_refresh_components("export_bounds")
    await hass.async_block_till_done()
    with patch(SLEEP, new_callable=AsyncMock), pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": preset_entity_id, "option": "max_export"},
            blocking=True,
        )


async def test_maximum_step_falls_back_to_inverter_rating(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    preset_entity_id: str,
    connection: MockModbusConnection,
) -> None:
    """A refused rated maximum is retried at the inverter's own rating."""
    unit = connection.for_unit(1)
    unit.input[5627] = 200  # BDC rating 20000 W, above the 10000 W rated output
    await init_integration.runtime_data.async_refresh_components("battery_info")
    await hass.async_block_till_done()

    def refuse_above_rating(event: WriteEvent) -> None:
        if event.register_type == "holding" and event.address == 33047:
            if int(event.values[0]) > 1000:
                unit.holding[33047] = 0

    unit.on_write(refuse_above_rating)
    with patch(SLEEP, new_callable=AsyncMock):
        await hass.services.async_call(
            "select",
            "select_option",
            {
                "entity_id": preset_entity_id,
                "option": "self_consumption_max_battery_discharge",
            },
            blocking=True,
        )
    assert unit.holding[33047] == 1000
    assert (
        hass.states.get(preset_entity_id).state
        == "self_consumption_max_battery_discharge"
    )


async def test_maximum_step_reports_when_nothing_is_accepted(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    preset_entity_id: str,
    connection: MockModbusConnection,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An outright refusal still fails, and logs the values needed to explain it."""
    unit = connection.for_unit(1)

    def refuse_all(event: WriteEvent) -> None:
        if event.register_type == "holding" and event.address == 33047:
            unit.holding[33047] = 0

    unit.on_write(refuse_all)
    with (
        caplog.at_level(
            logging.WARNING, logger="custom_components.sungrow_shx_inverter"
        ),
        patch(SLEEP, new_callable=AsyncMock),
        pytest.raises(HomeAssistantError),
    ):
        await hass.services.async_call(
            "select",
            "select_option",
            {
                "entity_id": preset_entity_id,
                "option": "self_consumption_max_battery_discharge",
            },
            blocking=True,
        )
    assert any(
        "refused battery_limits.battery_max_discharge_power" in r.message
        for r in caplog.records
    )
