"""Validated inverter setpoints."""

from dataclasses import dataclass
from typing import cast, override

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SungrowConfigEntry
from .entity import SungrowDescription, SungrowEntity, is_supported

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class SungrowNumberDescription(NumberEntityDescription, SungrowDescription):
    """A register setpoint in engineering units."""

    native_min_value: float
    native_max_value: float
    native_step: float


NUMBERS = (
    SungrowNumberDescription(
        key="battery_min_soc",
        translation_key="battery_min_soc",
        component="battery_settings",
        field="battery_min_soc",
        dependencies=("battery_settings",),
        source_fields=(("battery_settings", "battery_min_soc"),),
        native_min_value=0,
        native_max_value=50,
        native_step=1,
        native_unit_of_measurement="%",
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowNumberDescription(
        key="battery_max_soc",
        translation_key="battery_max_soc",
        component="battery_settings",
        field="battery_max_soc",
        dependencies=("battery_settings",),
        source_fields=(("battery_settings", "battery_max_soc"),),
        native_min_value=50,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement="%",
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowNumberDescription(
        key="battery_reserved_soc_for_backup",
        translation_key="battery_reserved_soc_for_backup",
        component="battery_settings",
        field="battery_reserved_soc_for_backup",
        dependencies=("battery_settings",),
        source_fields=(("battery_settings", "battery_reserved_soc_for_backup"),),
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement="%",
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowNumberDescription(
        key="battery_forced_charge_discharge_power",
        translation_key="battery_forced_charge_discharge_power",
        component="battery_settings",
        field="battery_forced_charge_discharge_power",
        dependencies=("battery_settings",),
        source_fields=(("battery_settings", "battery_forced_charge_discharge_power"),),
        native_min_value=0,
        native_max_value=65535,
        native_step=1,
        native_unit_of_measurement="W",
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowNumberDescription(
        key="battery_max_charge_power",
        translation_key="battery_max_charge_power",
        component="battery_limits",
        field="battery_max_charge_power",
        dependencies=("battery_limits",),
        source_fields=(("battery_limits", "battery_max_charge_power"),),
        native_min_value=10,
        native_max_value=65535,
        native_step=10,
        native_unit_of_measurement="W",
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowNumberDescription(
        key="battery_max_discharge_power",
        translation_key="battery_max_discharge_power",
        component="battery_limits",
        field="battery_max_discharge_power",
        dependencies=("battery_limits",),
        source_fields=(("battery_limits", "battery_max_discharge_power"),),
        native_min_value=10,
        native_max_value=65535,
        native_step=10,
        native_unit_of_measurement="W",
        entity_category=EntityCategory.CONFIG,
    ),
    SungrowNumberDescription(
        key="export_power_limit",
        translation_key="export_power_limit",
        component="export_settings",
        field="export_power_limit",
        dependencies=("export_settings",),
        source_fields=(("export_settings", "export_power_limit"),),
        native_min_value=0,
        native_max_value=65535,
        native_step=100,
        native_unit_of_measurement="W",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SungrowConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up numbers supported by this model."""
    async_add_entities(
        SungrowNumber(entry.runtime_data, description)
        for description in NUMBERS
        if is_supported(entry.runtime_data, description)
    )


class SungrowNumber(SungrowEntity, NumberEntity):
    """A bounded setpoint with confirmed readback."""

    entity_description: SungrowNumberDescription

    @property
    @override
    def native_value(self) -> float | None:
        """Return the engineering-unit value."""
        return cast(float | None, self._value())

    @property
    @override
    def native_min_value(self) -> float:
        """Use the inverter's export lower bound."""
        if self.entity_description.field == "export_power_limit":
            return self.coordinator.device.export_bounds.export_power_limit_min or 0
        return self.entity_description.native_min_value

    @property
    @override
    def native_max_value(self) -> float:
        """Bound power writes using the detected inverter/battery rating."""
        field = self.entity_description.field
        if field == "export_power_limit":
            maximum = self.coordinator.device.export_bounds.export_power_limit_max
            return min(maximum, 65535) if maximum is not None else 0
        if field in (
            "battery_forced_charge_discharge_power",
            "battery_max_charge_power",
            "battery_max_discharge_power",
        ):
            maximum = self.coordinator.device.battery_max_power
            return (
                min(maximum, self.entity_description.native_max_value)
                if maximum is not None
                else 0
            )
        return self.entity_description.native_max_value

    @property
    @override
    def available(self) -> bool:
        """Check fresh device limits and current value."""
        if not super().available or self.native_value is None:
            return False
        field = self.entity_description.field
        if field == "export_power_limit":
            return (
                "export_bounds" in self.coordinator.data.updated
                and self.coordinator.device.export_bounds.export_power_limit_max
                is not None
            )
        if field in (
            "battery_forced_charge_discharge_power",
            "battery_max_charge_power",
            "battery_max_discharge_power",
        ):
            return (
                "battery_info" in self.coordinator.data.updated
                and self.coordinator.device.battery_max_power is not None
            )
        return True

    @override
    async def async_set_native_value(self, value: float) -> None:
        """Apply device-level range checks and verify the write."""
        await self._async_write(value)
