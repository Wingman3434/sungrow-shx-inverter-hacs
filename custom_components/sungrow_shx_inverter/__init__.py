"""Integrate Sungrow residential hybrid inverters."""

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.service import async_extract_entities
from homeassistant.helpers.typing import ConfigType
from modbus_connection import ModbusTcpParams
import voluptuous as vol

from ._vendor.sungrow_shx_inverter import SungrowSHxInverter
from .const import (
    ATTR_PRESET,
    CONF_BATTERY_MAX_POWER,
    CONF_MESSAGE_WAIT,
    CONF_UNIT_ID,
    DATA_PRESET_ENTITIES,
    DEFAULT_MESSAGE_WAIT,
    DOMAIN,
    SERVICE_SET_PRESET,
)
from .coordinator import SungrowConfigEntry, SungrowCoordinator
from .presets import PRESET_KEYS

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
SET_PRESET_SCHEMA = cv.make_entity_service_schema(
    {vol.Required(ATTR_PRESET): vol.In(PRESET_KEYS)}
)
PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BUTTON,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the preset service once per Home Assistant run."""

    async def _async_set_preset(call: ServiceCall) -> None:
        """Apply a preset to every targeted preset selector."""
        targets = await async_extract_entities(
            hass.data.get(DOMAIN, {}).get(DATA_PRESET_ENTITIES, set()), call
        )
        if not targets:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="no_preset_target"
            )
        for entity in targets:
            await entity.async_set_preset(call.data[ATTR_PRESET])

    hass.services.async_register(
        DOMAIN, SERVICE_SET_PRESET, _async_set_preset, schema=SET_PRESET_SCHEMA
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SungrowConfigEntry) -> bool:
    """Acquire a shared unit, identify, and start coordinators."""
    unit = async_get_unit(
        hass,
        entry,
        ModbusTcpParams(host=entry.data[CONF_HOST], port=entry.data[CONF_PORT]),
        entry.data[CONF_UNIT_ID],
    )
    device = SungrowSHxInverter(
        unit,
        message_wait=entry.data.get(CONF_MESSAGE_WAIT, DEFAULT_MESSAGE_WAIT),
        battery_max_power=entry.options.get(CONF_BATTERY_MAX_POWER),
    )
    coordinator = SungrowCoordinator(hass, entry, device)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SungrowConfigEntry) -> bool:
    """Unload entities; the shared connection owner releases the unit."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: SungrowConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """Allow removing a device this entry no longer provides.

    The entry provides only the inverter device, identified by the serial kept in
    its unique ID. Anything else — for example the sub-devices an earlier release
    created — is stale, so Home Assistant may remove it.
    """
    return (DOMAIN, config_entry.unique_id) not in device_entry.identifiers
