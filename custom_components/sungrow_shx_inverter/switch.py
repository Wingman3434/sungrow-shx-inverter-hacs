"""Enable/disable controls using the vendor's 0xAA/0x55 words."""

from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from ._vendor.sungrow_shx_inverter.enums import Enable
from .coordinator import SungrowConfigEntry
from .entity import SungrowDescription, SungrowEntity, is_supported


@dataclass(frozen=True, kw_only=True)
class SungrowSwitchDescription(SwitchEntityDescription, SungrowDescription):
    """A platform-specific typed entity description."""


PARALLEL_UPDATES = 1
SWITCHES = (
    SungrowSwitchDescription(
        key="backup_mode",
        translation_key="backup_mode",
        component="export_settings",
        field="backup_mode_raw",
        dependencies=("export_settings",),
        source_fields=(("export_settings", "backup_mode_raw"),),
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowSwitchDescription(
        key="export_power_limit",
        translation_key="export_power_limit",
        component="export_settings",
        field="export_power_limit_mode_raw",
        dependencies=("export_settings",),
        source_fields=(("export_settings", "export_power_limit_mode_raw"),),
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowSwitchDescription(
        key="load_adjustment_mode",
        translation_key="load_adjustment_mode",
        component="load_settings",
        field="load_adjustment_mode_enable_raw",
        dependencies=("load_settings",),
        source_fields=(("load_settings", "load_adjustment_mode_enable_raw"),),
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SungrowConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the three source-defined switches."""
    async_add_entities(
        SungrowSwitch(entry.runtime_data, description)
        for description in SWITCHES
        if is_supported(entry.runtime_data, description)
    )


class SungrowSwitch(SungrowEntity, SwitchEntity):
    """A confirmed switch; unknown words are never assumed enabled."""

    entity_description: SungrowSwitchDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return the known device switch state."""
        value: int | None = self._value()
        if value not in (Enable.ENABLED, Enable.DISABLED):
            return None
        return value == Enable.ENABLED

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the setting."""
        await self._async_write(Enable.ENABLED)

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the setting."""
        await self._async_write(Enable.DISABLED)
