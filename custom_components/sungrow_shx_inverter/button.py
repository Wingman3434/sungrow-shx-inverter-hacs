"""Explicit write-only inverter start and stop commands."""

from dataclasses import dataclass
from typing import override

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from modbus_connection import ModbusError

from ._vendor.sungrow_shx_inverter.enums import InverterCommand
from .const import DOMAIN
from .coordinator import SungrowConfigEntry
from .entity import SungrowDescription, SungrowEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class SungrowButtonDescription(ButtonEntityDescription, SungrowDescription):
    """A write-only operating command."""

    command: InverterCommand


BUTTONS = tuple(
    SungrowButtonDescription(
        key=f"{command.name.lower()}_inverter",
        translation_key=f"{command.name.lower()}_inverter",
        component="state",
        field="running_state_raw",
        dependencies=("state",),
        source_fields=(("state", "running_state_raw"),),
        command=command,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.CONFIG,
    )
    for command in InverterCommand
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SungrowConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Buttons are available for explicit opt-in, never pressed during setup."""
    async_add_entities(
        SungrowButton(entry.runtime_data, description) for description in BUTTONS
    )


class SungrowButton(SungrowEntity, ButtonEntity):
    """A command with no invented readback state."""

    entity_description: SungrowButtonDescription

    @override
    async def async_press(self) -> None:
        """Send the selected command once."""
        try:
            await self.coordinator.device.async_command(self.entity_description.command)
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="write_failed"
            ) from err
        await self.coordinator.async_refresh_components("state")
