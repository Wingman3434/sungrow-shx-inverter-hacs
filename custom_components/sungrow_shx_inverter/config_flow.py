"""Sungrow discovery, duplicate prevention and reconfiguration."""

from typing import Any, override

from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)
from modbus_connection import ModbusError, ModbusTcpParams
import voluptuous as vol

from ._vendor.sungrow_shx_inverter import SungrowSHxInverter, UnsupportedDeviceError
from .const import (
    CONF_BATTERY_MAX_POWER,
    CONF_MESSAGE_WAIT,
    CONF_UNIT_ID,
    DEFAULT_MESSAGE_WAIT,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
)


def _number(low: float, high: float, step: float = 1) -> NumberSelector:
    """Number."""
    return NumberSelector(
        NumberSelectorConfig(min=low, max=high, step=step, mode=NumberSelectorMode.BOX)
    )


STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): vol.All(TextSelector(), vol.Length(min=1)),
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            _number(1, 65535), vol.Coerce(int)
        ),
        vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): vol.All(
            _number(1, 247), vol.Coerce(int)
        ),
        vol.Required(CONF_MESSAGE_WAIT, default=DEFAULT_MESSAGE_WAIT): _number(
            0, 10, 0.001
        ),
    }
)


async def _async_probe(
    hass: HomeAssistant, values: dict[str, Any]
) -> SungrowSHxInverter:
    """Read only identity while holding the temporary shared unit."""
    async with async_get_temporary_unit(
        hass,
        ModbusTcpParams(host=values[CONF_HOST], port=values[CONF_PORT]),
        values[CONF_UNIT_ID],
    ) as unit:
        device = SungrowSHxInverter(
            unit,
            message_wait=values.get(CONF_MESSAGE_WAIT, DEFAULT_MESSAGE_WAIT),
        )
        await device.async_identify()
    return device


class SungrowConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a device from its own serial number, not its network address."""

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry: ConfigEntry) -> SungrowOptionsFlow:
        """Manage optional installation limits."""
        return SungrowOptionsFlow()

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up an inverter."""
        return await self._async_form("user", user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update connection details without changing the device identity."""
        return await self._async_form("reconfigure", user_input)

    async def _async_form(
        self, step: str, values: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Async form."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry() if step == "reconfigure" else None
        if values is not None:
            values = {**values, CONF_HOST: str(values[CONF_HOST]).strip()}
            try:
                device = await _async_probe(self.hass, values)
            except UnsupportedDeviceError:
                errors["base"] = "unsupported_device"
            except (ModbusError, HomeAssistantError):  # fmt: skip
                errors["base"] = "cannot_connect"
            else:
                assert device.serial_number is not None
                await self.async_set_unique_id(device.serial_number)
                if entry is not None:
                    self._abort_if_unique_id_mismatch()
                    return self.async_update_reload_and_abort(
                        entry, data_updates=values
                    )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Sungrow SHx Inverter {device.model}", data=values
                )
        return self.async_show_form(
            step_id=step,
            data_schema=self.add_suggested_values_to_schema(
                STEP_SCHEMA, values or (entry.data if entry is not None else {})
            ),
            errors=errors,
        )


class SungrowOptionsFlow(OptionsFlowWithReload):
    """Set or clear the optional battery power cap without reconnecting in the form."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update optional settings; an empty form clears the cap."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema({vol.Optional(CONF_BATTERY_MAX_POWER): _number(10, 65535)}),
                self.config_entry.options,
            ),
        )
