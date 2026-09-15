"""Mapped operation modes without silent fallback on unknown register words."""

from dataclasses import dataclass
import logging
from typing import override

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from modbus_connection import ModbusError

from .const import DATA_PRESET_ENTITIES, DOMAIN
from .coordinator import SungrowConfigEntry, SungrowCoordinator
from .entity import SungrowDescription, SungrowEntity, is_supported
from .presets import PRESETS, PresetStep, fallback_maximum, resolve_value

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class SungrowSelectDescription(SelectEntityDescription, SungrowDescription):
    """Stable translated options and their exact register words."""

    values: dict[str, int]


SELECTS = (
    SungrowSelectDescription(
        key="ems_mode",
        translation_key="ems_mode",
        component="battery_settings",
        field="ems_mode_selection_raw",
        dependencies=("battery_settings",),
        source_fields=(("battery_settings", "ems_mode_selection_raw"),),
        values={
            "self_consumption_mode": 0,
            "forced_mode": 2,
            "external_ems": 3,
            "vpp": 4,
        },
        options=["self_consumption_mode", "forced_mode", "external_ems", "vpp"],
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowSelectDescription(
        key="battery_forced_charge_discharge",
        translation_key="battery_forced_charge_discharge",
        component="battery_settings",
        field="battery_forced_charge_discharge_cmd_raw",
        dependencies=("battery_settings",),
        source_fields=(
            ("battery_settings", "battery_forced_charge_discharge_cmd_raw"),
        ),
        values={"stop": 204, "forced_charge": 170, "forced_discharge": 187},
        options=["stop", "forced_charge", "forced_discharge"],
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowSelectDescription(
        key="load_adjustment_mode",
        translation_key="load_adjustment_mode",
        component="load_settings",
        field="load_adjustment_mode_selection_raw",
        dependencies=("load_settings",),
        source_fields=(("load_settings", "load_adjustment_mode_selection_raw"),),
        values={"timing": 0, "on_off": 1, "power_optimization": 2, "disabled": 3},
        options=["timing", "on_off", "power_optimization", "disabled"],
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SungrowConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the register-backed selects plus the composed preset selector."""
    entities: list[SelectEntity] = [
        SungrowSelect(entry.runtime_data, description)
        for description in SELECTS
        if is_supported(entry.runtime_data, description)
    ]
    if "battery_settings" in entry.runtime_data.device.components:
        preset = SungrowOperatingPreset(entry.runtime_data)
        entities.append(preset)
        presets = hass.data.setdefault(DOMAIN, {}).setdefault(
            DATA_PRESET_ENTITIES, set()
        )
        presets.add(preset)
        entry.async_on_unload(lambda: presets.discard(preset))
    async_add_entities(entities)


class SungrowSelect(SungrowEntity, SelectEntity):
    """A mode which is unknown if the inverter reports an undocumented word."""

    entity_description: SungrowSelectDescription

    @property
    @override
    def current_option(self) -> str | None:
        """Return a known option or None."""
        return next(
            (
                key
                for key, word in self.entity_description.values.items()
                if word == self._value()
            ),
            None,
        )

    @override
    async def async_select_option(self, option: str) -> None:
        """Write the selected operation mode."""
        await self._async_write(self.entity_description.values[option])


class SungrowOperatingPreset(CoordinatorEntity[SungrowCoordinator], SelectEntity):
    """A whole mode preset, applied the way the source scenes applied it.

    It is not backed by one register: selecting an option writes the EMS mode,
    the forced charge/discharge command and the relevant limit, reading the
    inverter's live maximum instead of a configured secret.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "operating_preset"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(PRESETS)

    def __init__(self, coordinator: SungrowCoordinator) -> None:
        """Initialize the preset selector on the inverter's device page."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.serial_number}_operating_preset"
        self._attr_device_info = coordinator.device_info
        self._attr_current_option: str | None = None

    @property
    @override
    def available(self) -> bool:
        """Presets are usable once the battery-settings cohort has answered."""
        return super().available and "battery_settings" in self.coordinator.data.updated

    @override
    async def async_select_option(self, option: str) -> None:
        """Apply the chosen preset."""
        await self.async_set_preset(option)

    async def async_set_preset(self, preset: str) -> None:
        """Apply a preset sequence, then refresh every cohort it touched."""
        steps = PRESETS.get(preset)
        if steps is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_value"
            )
        touched: set[str] = set()
        try:
            for step in steps:
                await self._async_apply_step(step)
                touched.add(step.component)
        except ValueError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="invalid_value"
            ) from err
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="write_failed"
            ) from err
        self._attr_current_option = preset
        self.async_write_ha_state()
        await self.coordinator.async_refresh_components(*sorted(touched), "state")

    async def _async_apply_step(self, step: PresetStep) -> None:
        """Write one step, letting a maximum step settle below its rating.

        A step that asks for the inverter's maximum may be capped lower by the
        device (rated versus configured limits), so the value the inverter
        settles on is accepted when the write demonstrably took effect. If the
        write was refused outright, one lower device-derived ceiling is tried
        before failing. An explicit value must be confirmed exactly.
        """
        device = self.coordinator.device
        target = device.components.get(step.component)
        previous = getattr(target, step.field, None) if target is not None else None
        value = resolve_value(device, step)
        try:
            await device.async_write(step.component, step.field, value)
        except ModbusError:
            if not step.is_maximum or target is None:
                raise
            achieved = getattr(target, step.field, None)
            if achieved is not None and achieved != previous:
                _LOGGER.debug(
                    "Sungrow capped %s.%s at %s (requested %s)",
                    step.component,
                    step.field,
                    achieved,
                    value,
                )
                return
            fallback = fallback_maximum(device, step)
            if fallback is not None and 0 < fallback < value:
                try:
                    await device.async_write(step.component, step.field, fallback)
                except ModbusError:
                    pass
                else:
                    _LOGGER.info(
                        "Sungrow accepted %s.%s=%s; rated maximum %s was refused",
                        step.component,
                        step.field,
                        fallback,
                        value,
                    )
                    return
            _LOGGER.warning(
                "Sungrow refused %s.%s=%s (device kept %s); bdc_rated_power=%s,"
                " inverter_rated_output=%s, battery_max_power=%s, fallback=%s",
                step.component,
                step.field,
                value,
                achieved,
                getattr(device.battery_info, "bdc_rated_power", None),
                getattr(device.identity, "inverter_rated_output", None),
                getattr(device, "battery_max_power", None),
                fallback,
            )
            raise
        else:
            return
